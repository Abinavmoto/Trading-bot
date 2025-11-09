"""Utility functions for loading and validating market data."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import pandas as pd


REQUIRED_COLUMNS: List[str] = [
    "open",
    "high",
    "low",
    "close",
    "volume",
]


class DataValidationError(ValueError):
    """Raised when market data is missing required information."""


@dataclass(frozen=True)
class PriceData:
    """Wrapper holding the validated OHLCV dataframe."""

    frame: pd.DataFrame

    def __post_init__(self) -> None:
        missing = [column for column in REQUIRED_COLUMNS if column not in self.frame.columns]
        if missing:
            raise DataValidationError(f"Missing columns: {', '.join(missing)}")
        if self.frame.index.name != "timestamp":
            raise DataValidationError("Index must be named 'timestamp'.")
        if not pd.api.types.is_datetime64_any_dtype(self.frame.index):
            raise DataValidationError("Index must be a datetime type.")
        if self.frame.isna().any().any():
            raise DataValidationError("Price data contains NaN values.")


def _normalise_path(path: Path | str) -> Path:
    """Return an absolute path to the provided data file."""

    resolved = Path(path).expanduser()
    if not resolved.exists():
        raise FileNotFoundError(f"Price data file does not exist: {resolved}")
    return resolved


def load_price_data(path: Path | str) -> PriceData:
    """Load OHLCV data from a CSV file.

    The timestamp column is parsed into a timezone-aware datetime index.
    A :class:`PriceData` instance containing the validated frame is returned.
    """

    csv_path = _normalise_path(path)
    frame = pd.read_csv(csv_path)
    required_with_timestamp = ["timestamp", *REQUIRED_COLUMNS]
    missing = [column for column in required_with_timestamp if column not in frame.columns]
    if missing:
        raise DataValidationError(f"CSV file must contain columns: {', '.join(missing)}")

    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    frame = frame.set_index("timestamp").sort_index()

    return PriceData(frame=frame)


def resample_prices(price_data: PriceData, rule: str) -> PriceData:
    """Resample the OHLCV data using the provided pandas frequency rule."""

    ohlc_dict = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    resampled = price_data.frame.resample(rule).apply(ohlc_dict).dropna()
    resampled.index.name = "timestamp"
    return PriceData(frame=resampled)


def rolling_window(series: pd.Series, window: int) -> Iterable[pd.Series]:
    """Yield rolling windows over the provided series.

    This helper is useful for indicator calculations that require explicit
    iteration over windows (e.g. in streaming scenarios).
    """

    if window <= 0:
        raise ValueError("Window must be positive")
    for i in range(window, len(series) + 1):
        yield series.iloc[i - window : i]
