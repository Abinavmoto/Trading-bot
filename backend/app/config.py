from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = "Gold Signal Service"
    database_url: str = Field(default="sqlite:///" + str(Path(__file__).resolve().parents[1] / "signals.db"))
    live_mode: bool = False
    mt5_login: Optional[str] = None
    mt5_password: Optional[str] = None
    mt5_server: Optional[str] = None
    default_starting_balance: float = 10_000.0
    data_source: str = "yfinance"
    candles_interval: str = "1h"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
