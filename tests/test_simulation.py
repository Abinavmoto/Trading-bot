import pandas as pd

from trading_bot.data import PriceData
from trading_bot.simulation import run_backtest
from trading_bot.strategy import GoldSmaRsiStrategy


def _make_price_data() -> PriceData:
    index = pd.date_range("2023-01-01", periods=30, freq="H", tz="UTC")
    close = pd.Series(
        [
            1900,
            1901,
            1903,
            1905,
            1907,
            1908,
            1910,
            1912,
            1914,
            1911,
            1909,
            1907,
            1905,
            1903,
            1901,
            1900,
            1899,
            1900,
            1902,
            1905,
            1907,
            1909,
            1911,
            1913,
            1910,
            1908,
            1906,
            1904,
            1902,
            1900,
        ],
        index=index,
    )
    frame = pd.DataFrame(
        {
            "open": close,
            "high": close + 1,
            "low": close - 1,
            "close": close,
            "volume": 1000,
        },
        index=index,
    )
    frame.index.name = "timestamp"
    return PriceData(frame=frame)


def test_run_backtest_returns_expected_structure() -> None:
    price_data = _make_price_data()
    strategy = GoldSmaRsiStrategy(
        short_ma_length=3,
        long_ma_length=8,
        rsi_period=3,
        rsi_buy_min=0,
        rsi_buy_max=100,
        rsi_sell_min=30,
    )

    result = run_backtest(price_data, strategy, starting_balance=10_000, unit_size=1)

    assert set(result.summary.keys()) >= {
        "starting_balance",
        "final_balance",
        "max_drawdown",
        "win_rate",
        "num_trades",
        "total_return",
    }
    assert isinstance(result.equity_curve, list)
    assert isinstance(result.drawdown_curve, list)
    assert isinstance(result.trades, list)
