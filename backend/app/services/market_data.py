from datetime import datetime
from typing import List

import pandas as pd
import yfinance as yf

from ..config import get_settings


def fetch_candles(symbol: str, start: datetime, end: datetime) -> pd.DataFrame:
    settings = get_settings()
    interval = settings.candles_interval
    ticker = yf.Ticker(symbol)
    hist = ticker.history(start=start, end=end, interval=interval)
    if hist.empty:
        raise ValueError(f"No market data returned for {symbol}")
    hist = hist.tz_localize(None)
    hist = hist.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
    hist.index = pd.to_datetime(hist.index)
    return hist


def dataframe_to_records(df: pd.DataFrame) -> List[dict]:
    return [
        {
            "timestamp": idx.to_pydatetime(),
            "open": float(row.open),
            "high": float(row.high),
            "low": float(row.low),
            "close": float(row.close),
            "volume": float(row.volume) if not pd.isna(row.volume) else 0.0,
        }
        for idx, row in df.iterrows()
    ]
