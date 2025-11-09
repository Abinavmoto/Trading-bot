from pathlib import Path

import pandas as pd
import pytest

from trading_bot.data import DataValidationError, PriceData, load_price_data, resample_prices


def test_load_price_data(tmp_path: Path) -> None:
    csv = tmp_path / "prices.csv"
    csv.write_text(
        "timestamp,open,high,low,close,volume\n"
        "2023-01-01T00:00:00Z,1,2,0.5,1.5,100\n"
        "2023-01-02T00:00:00Z,1.5,2.5,1,2,120\n"
    )
    data = load_price_data(csv)
    assert isinstance(data, PriceData)
    assert list(data.frame.columns) == ["open", "high", "low", "close", "volume"]
    assert data.frame.index.tz is not None


def test_load_price_data_missing_column(tmp_path: Path) -> None:
    csv = tmp_path / "bad.csv"
    csv.write_text("timestamp,close\n2023-01-01T00:00:00Z,1\n")
    with pytest.raises(DataValidationError):
        load_price_data(csv)


def test_resample_prices() -> None:
    data = load_price_data(Path("data/sample_data.csv"))
    resampled = resample_prices(data, "7D")
    assert len(resampled.frame) < len(data.frame)
    assert resampled.frame.index.freqstr == "7D"
