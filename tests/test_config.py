from __future__ import annotations

from pathlib import Path

import pytest

from trading_bot import config as config_module


@pytest.fixture()
def config_file(tmp_path: Path) -> Path:
    file_path = tmp_path / "config.json"
    return file_path


def test_load_config_returns_defaults_when_missing(config_file: Path) -> None:
    data = config_module.load_config(config_file)
    assert data["data_provider"]["vendor"] == config_module.DEFAULT_CONFIG["data_provider"]["vendor"]


def test_save_and_reload_roundtrip(config_file: Path) -> None:
    example = config_module.validate_config(
        {
            "data_provider": {
                "vendor": "twelve_data",
                "api_key": "demo",
                "symbol": "GBPUSD",
                "interval": "1h",
            },
            "trade_settings": {
                "mode": "paper",
                "base_currency": "USD",
                "risk_per_trade": 0.02,
            },
        }
    )

    config_module.save_config(example, config_file)
    loaded = config_module.load_config(config_file)
    assert loaded == example


def test_validate_config_requires_live_credentials() -> None:
    with pytest.raises(config_module.ConfigError):
        config_module.validate_config(
            {
                "data_provider": {
                    "vendor": "oanda",
                    "api_key": "",
                    "account_id": "",
                    "symbol": "EURUSD",
                    "interval": "1h",
                },
                "trade_settings": {
                    "mode": "live",
                    "base_currency": "USD",
                    "risk_per_trade": 0.01,
                },
            }
        )


def test_validate_config_rejects_invalid_risk_value() -> None:
    with pytest.raises(config_module.ConfigError):
        config_module.validate_config(
            {
                "data_provider": {
                    "vendor": "alpha_vantage",
                    "api_key": "demo",
                    "symbol": "EURUSD",
                    "interval": "1h",
                },
                "trade_settings": {
                    "mode": "backtest",
                    "base_currency": "USD",
                    "risk_per_trade": 1.5,
                },
            }
        )
