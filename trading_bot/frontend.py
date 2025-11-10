"""Flask application exposing a configuration screen for the trading bot."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import pandas as pd
from flask import Flask, flash, jsonify, render_template, request

from trading_bot.config import (
    CONFIG_DIR,
    DEFAULT_CONFIG_PATH,
    PROVIDERS,
    ConfigError,
    DEFAULT_CONFIG,
    load_config,
    save_config,
    validate_config,
)
from trading_bot.ai_insight import FALLBACK_RESPONSE, generate_ai_insight, stub_headlines
from trading_bot.data import PriceData, load_symbol_data
from trading_bot.simulation import run_backtest
from trading_bot.strategy import GoldSmaRsiStrategy


def create_app(config_path: Path | None = None) -> Flask:
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).with_name("templates")),
        static_folder=str(Path(__file__).with_name("static")),
    )
    app.secret_key = os.environ.get("TRADING_BOT_SECRET", "dev-secret")

    resolved_path = Path(
        config_path or os.environ.get("TRADING_BOT_CONFIG", DEFAULT_CONFIG_PATH)
    ).expanduser()

    @app.after_request
    def add_cors_headers(response):  # type: ignore[override]
        origin = request.headers.get("Origin")
        if origin and origin.startswith("http://localhost"):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers.setdefault("Vary", "Origin")
        response.headers.setdefault("Access-Control-Allow-Headers", "Content-Type")
        response.headers.setdefault("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        return response

    @app.route("/", methods=["GET", "POST"])
    def config_screen() -> str:
        current_config: Dict[str, Any] = load_config(resolved_path)

        if request.method == "POST":
            risk_raw = request.form.get("risk_per_trade", "").strip()
            submitted = {
                "data_provider": {
                    "vendor": request.form.get("vendor", "").strip(),
                    "api_key": request.form.get("api_key", "").strip(),
                    "api_secret": request.form.get("api_secret", "").strip(),
                    "account_id": request.form.get("account_id", "").strip(),
                    "base_url": request.form.get("base_url", "").strip(),
                    "symbol": request.form.get("symbol", "").strip(),
                    "interval": request.form.get("interval", "").strip(),
                },
                "trade_settings": {
                    "mode": request.form.get("mode", "").strip(),
                    "base_currency": request.form.get("base_currency", "").strip(),
                    "risk_per_trade": risk_raw,
                },
            }

            try:
                submitted["trade_settings"]["risk_per_trade"] = float(
                    submitted["trade_settings"].get("risk_per_trade", 0)
                )
                validated = validate_config(submitted)
            except ValueError:
                flash("Risk per trade must be a numeric value between 0 and 1.", "error")
                current_config = submitted
            except ConfigError as exc:
                flash(str(exc), "error")
                current_config = submitted
            else:
                save_config(validated, resolved_path)
                flash("Configuration saved successfully.", "success")
                current_config = validated

        provider_choices = {
            key: {
                "label": meta.label,
                "description": meta.description,
                "default_base_url": meta.default_base_url,
                "required_credentials": meta.required_credentials,
            }
            for key, meta in PROVIDERS.items()
        }

        return render_template(
            "config.html",
            config=current_config,
            providers=provider_choices,
            config_path=resolved_path,
        )

    def _build_strategy(config: Dict[str, Any]) -> GoldSmaRsiStrategy:
        strategy_cfg = {**DEFAULT_CONFIG["strategy"], **config.get("strategy", {})}
        return GoldSmaRsiStrategy(
            short_ma_length=int(strategy_cfg.get("short_ma_length", 20)),
            long_ma_length=int(strategy_cfg.get("long_ma_length", 50)),
            rsi_period=int(strategy_cfg.get("rsi_period", 14)),
            rsi_buy_min=float(strategy_cfg.get("rsi_buy_min", 45)),
            rsi_buy_max=float(strategy_cfg.get("rsi_buy_max", 65)),
            rsi_sell_min=float(strategy_cfg.get("rsi_sell_min", 60)),
        )

    def _serialise_price_data(
        price_data: PriceData, start: pd.Timestamp | None, end: pd.Timestamp | None
    ) -> PriceData:
        frame = price_data.frame
        if start:
            frame = frame.loc[frame.index >= start]
        if end:
            frame = frame.loc[frame.index <= end]
        if frame.empty:
            raise ValueError("No price data available for the requested period.")
        return PriceData(frame=frame)

    def _load_context() -> tuple[Dict[str, Any], Dict[str, Any], PriceData, GoldSmaRsiStrategy]:
        config = load_config(resolved_path)
        provider_cfg = config.get("data_provider", DEFAULT_CONFIG["data_provider"])
        price_data = load_symbol_data(provider_cfg["symbol"], provider_cfg["interval"])
        strategy = _build_strategy(config)
        return config, provider_cfg, price_data, strategy

    @app.route("/dashboard", methods=["GET"])
    def dashboard() -> str:
        config = load_config(resolved_path)
        provider_cfg = config.get("data_provider", DEFAULT_CONFIG["data_provider"])
        return render_template(
            "dashboard.html",
            symbol=provider_cfg.get("symbol", "XAUUSD"),
            timeframe=provider_cfg.get("interval", "60min"),
        )

    @app.route("/api/signal/latest", methods=["GET"])
    def latest_signal() -> tuple[Any, int] | Any:
        try:
            _, provider_cfg, price_data, strategy = _load_context()
        except (KeyError, FileNotFoundError) as exc:
            return jsonify({"error": str(exc)}), 400

        try:
            signal = strategy.latest_signal(price_data.frame["close"])
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        payload = {
            "symbol": provider_cfg.get("symbol", "XAUUSD"),
            "timeframe": provider_cfg.get("interval", "60min"),
            "timestamp": signal.timestamp.isoformat(),
            "price": signal.price,
            "sma20": signal.sma_short,
            "sma50": signal.sma_long,
            "rsi14": signal.rsi,
            "signal": signal.signal,
        }
        return jsonify(payload)

    @app.route("/api/simulation/run", methods=["POST", "OPTIONS"])
    def run_simulation() -> tuple[Any, int] | Any:
        if request.method == "OPTIONS":
            return ("", 204)

        payload = request.get_json(silent=True) or {}
        required_fields = {"symbol", "timeframe", "start_date", "end_date", "starting_balance"}
        missing = required_fields - payload.keys()
        if missing:
            return jsonify({"error": f"Missing fields: {', '.join(sorted(missing))}"}), 400

        try:
            start = pd.to_datetime(payload["start_date"], utc=True)
            end = pd.to_datetime(payload["end_date"], utc=True)
            starting_balance = float(payload["starting_balance"])
        except (ValueError, TypeError) as exc:
            return jsonify({"error": f"Invalid request data: {exc}"}), 400

        if start > end:
            return jsonify({"error": "start_date must be before end_date."}), 400

        try:
            price_data = load_symbol_data(payload["symbol"], payload["timeframe"])
            filtered = _serialise_price_data(price_data, start, end)
        except (FileNotFoundError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 400

        strategy = _build_strategy(load_config(resolved_path))
        try:
            result = run_backtest(filtered, strategy, starting_balance)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        def _serialise_curve(curve: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
            return [
                {"timestamp": point["timestamp"].isoformat(), key: point[key]} for point in curve
            ]

        trades_payload = [
            {
                "entry_time": trade.entry_time.isoformat(),
                "exit_time": trade.exit_time.isoformat(),
                "side": trade.side,
                "entry_price": trade.entry_price,
                "exit_price": trade.exit_price,
                "size": trade.size,
                "pnl": trade.pnl,
            }
            for trade in result.trades
        ]

        response = {
            "summary": result.summary,
            "equity_curve": _serialise_curve(result.equity_curve, "equity"),
            "drawdown_curve": _serialise_curve(result.drawdown_curve, "drawdown"),
            "trades": trades_payload,
        }
        return jsonify(response)

    @app.route("/api/ai-insight", methods=["GET"])
    def ai_insight() -> Any:
        fallback = dict(FALLBACK_RESPONSE)
        try:
            config, provider_cfg, price_data, strategy = _load_context()
        except (FileNotFoundError, KeyError):
            return jsonify(fallback)

        try:
            signal = strategy.latest_signal(price_data.frame["close"])
        except ValueError:
            fallback.update(
                {
                    "symbol": provider_cfg.get("symbol", "XAUUSD"),
                    "timeframe": provider_cfg.get("interval", "60min"),
                    "timestamp": None,
                }
            )
            return jsonify(fallback)

        recent_frame = price_data.frame.tail(60)
        insight = generate_ai_insight(
            signal=signal,
            recent_frame=recent_frame,
            strategy_config=config.get("strategy", DEFAULT_CONFIG["strategy"]),
            headlines=stub_headlines(),
        )
        payload = {
            **insight,
            "symbol": provider_cfg.get("symbol", "XAUUSD"),
            "timeframe": provider_cfg.get("interval", "60min"),
            "timestamp": signal.timestamp.isoformat(),
        }
        return jsonify(payload)

    return app


def main() -> None:
    """Entrypoint for running the config UI server."""

    port = int(os.environ.get("PORT", "8000"))
    host = os.environ.get("HOST", "0.0.0.0")
    config_path = Path(os.environ.get("TRADING_BOT_CONFIG", DEFAULT_CONFIG_PATH))
    CONFIG_DIR.mkdir(exist_ok=True)

    app = create_app(config_path=config_path)
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":  # pragma: no cover - manual execution
    main()
