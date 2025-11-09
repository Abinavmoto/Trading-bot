"""Configuration management for the trading bot deployment."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping


CONFIG_DIR = Path("config")
CONFIG_DIR.mkdir(exist_ok=True)
DEFAULT_CONFIG_PATH = CONFIG_DIR / "config.json"


class ConfigError(ValueError):
    """Raised when the supplied configuration is invalid."""


@dataclass(frozen=True)
class ProviderMeta:
    """Metadata describing a market data vendor."""

    label: str
    description: str
    required_credentials: tuple[str, ...]
    default_base_url: str


PROVIDERS: Mapping[str, ProviderMeta] = {
    "alpha_vantage": ProviderMeta(
        label="Alpha Vantage (Free)",
        description="Free forex data with throttled request limits.",
        required_credentials=("api_key",),
        default_base_url="https://www.alphavantage.co",
    ),
    "twelve_data": ProviderMeta(
        label="Twelve Data",
        description="Low-latency forex and crypto data with generous limits.",
        required_credentials=("api_key",),
        default_base_url="https://api.twelvedata.com",
    ),
    "oanda": ProviderMeta(
        label="OANDA",
        description="Broker-grade forex pricing and trade execution APIs.",
        required_credentials=("api_key", "account_id"),
        default_base_url="https://api-fxtrade.oanda.com",
    ),
}


DEFAULT_CONFIG: Dict[str, Any] = {
    "data_provider": {
        "vendor": "alpha_vantage",
        "api_key": "",
        "api_secret": "",
        "account_id": "",
        "base_url": PROVIDERS["alpha_vantage"].default_base_url,
        "symbol": "EURUSD",
        "interval": "60min",
    },
    "trade_settings": {
        "mode": "backtest",
        "base_currency": "USD",
        "risk_per_trade": 0.01,
    },
}


def _ensure_config_path(path: Path | None = None) -> Path:
    """Return a normalised configuration path, creating parents when necessary."""

    config_path = Path(path or DEFAULT_CONFIG_PATH).expanduser()
    if not config_path.parent.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
    return config_path


def load_config(path: Path | None = None) -> Dict[str, Any]:
    """Load configuration from disk, falling back to defaults when absent."""

    config_path = _ensure_config_path(path)
    if not config_path.exists():
        return json.loads(json.dumps(DEFAULT_CONFIG))

    with config_path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data


def save_config(config: Mapping[str, Any], path: Path | None = None) -> None:
    """Persist configuration to disk."""

    config_path = _ensure_config_path(path)
    with config_path.open("w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2, sort_keys=True)


def validate_config(config: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate configuration fields and normalise missing defaults."""

    if "data_provider" not in config:
        raise ConfigError("Configuration must include 'data_provider'.")
    if "trade_settings" not in config:
        raise ConfigError("Configuration must include 'trade_settings'.")

    validated: Dict[str, Any] = {
        "data_provider": dict(DEFAULT_CONFIG["data_provider"]),
        "trade_settings": dict(DEFAULT_CONFIG["trade_settings"]),
    }

    provider_section = {**validated["data_provider"], **config["data_provider"]}
    vendor = provider_section.get("vendor")
    if vendor not in PROVIDERS:
        known = ", ".join(PROVIDERS)
        raise ConfigError(f"Unknown data provider '{vendor}'. Known providers: {known}.")

    provider_meta = PROVIDERS[vendor]
    base_url = provider_section.get("base_url")
    if not base_url:
        provider_section["base_url"] = provider_meta.default_base_url

    for field in provider_meta.required_credentials:
        if not provider_section.get(field):
            raise ConfigError(
                f"Provider '{provider_meta.label}' requires the field '{field}' to be configured."
            )

    if not provider_section.get("symbol"):
        raise ConfigError("Default trading symbol must be provided.")

    if not provider_section.get("interval"):
        raise ConfigError("Price interval must be provided (e.g. '60min').")

    validated["data_provider"] = provider_section

    trade_settings = {**validated["trade_settings"], **config["trade_settings"]}
    mode = trade_settings.get("mode")
    if mode not in {"backtest", "paper", "live"}:
        raise ConfigError("Trade mode must be one of: backtest, paper, live.")

    if mode == "live":
        missing = [
            key
            for key in ("api_key", "account_id")
            if not provider_section.get(key)
        ]
        if missing:
            raise ConfigError(
                "Live trading mode requires the following data provider fields: "
                + ", ".join(missing)
            )

    risk = trade_settings.get("risk_per_trade")
    if not isinstance(risk, (int, float)) or risk <= 0 or risk >= 1:
        raise ConfigError("risk_per_trade must be a decimal between 0 and 1.")

    if not trade_settings.get("base_currency"):
        raise ConfigError("Base currency must be configured (e.g. 'USD').")

    validated["trade_settings"] = trade_settings
    return validated


__all__ = [
    "ConfigError",
    "DEFAULT_CONFIG",
    "DEFAULT_CONFIG_PATH",
    "PROVIDERS",
    "load_config",
    "save_config",
    "validate_config",
]
