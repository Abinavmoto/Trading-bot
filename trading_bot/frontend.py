"""Flask application exposing a configuration screen for the trading bot."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

from flask import Flask, flash, render_template, request

from trading_bot.config import (
    CONFIG_DIR,
    DEFAULT_CONFIG_PATH,
    PROVIDERS,
    ConfigError,
    load_config,
    save_config,
    validate_config,
)


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
