import pandas as pd
import pytest

from trading_bot.strategy import GoldSmaRsiStrategy, MovingAverageCrossStrategy


def test_strategy_generates_signals() -> None:
    prices = pd.Series([1, 2, 3, 4, 5], index=pd.date_range("2023-01-01", periods=5, freq="D"))
    strategy = MovingAverageCrossStrategy(short_window=2, long_window=3)
    signals = strategy.generate_signals(prices)
    assert signals.iloc[-1] == 1
    assert set(signals.unique()).issubset({0, 1})


def test_strategy_validates_windows() -> None:
    with pytest.raises(ValueError):
        MovingAverageCrossStrategy(short_window=5, long_window=3)


def test_generate_trading_actions() -> None:
    prices = pd.Series([1, 2, 3, 2, 1, 2], index=pd.date_range("2023-01-01", periods=6, freq="D"))
    strategy = MovingAverageCrossStrategy(short_window=2, long_window=4)
    actions = strategy.generate_trading_actions(prices)
    assert actions.iloc[0] == 0
    assert actions.iloc[-1] in (-1, 0, 1)
    assert actions.sum() <= 1  # no net creation of positions beyond one unit


def test_gold_strategy_buy_signal() -> None:
    index = pd.date_range("2023-01-01", periods=10, freq="H")
    prices = pd.Series([1, 1.1, 1.2, 1.25, 1.3, 1.32, 1.34, 1.35, 1.36, 1.37], index=index)
    strategy = GoldSmaRsiStrategy(
        short_ma_length=3,
        long_ma_length=5,
        rsi_period=3,
        rsi_buy_min=0,
        rsi_buy_max=100,
        rsi_sell_min=50,
    )
    signal = strategy.latest_signal(prices)
    assert signal.signal == "BUY"
    assert signal.sma_short > signal.sma_long


def test_gold_strategy_sell_signal() -> None:
    index = pd.date_range("2023-01-01", periods=12, freq="H")
    prices = pd.Series(
        [1.5, 1.49, 1.48, 1.47, 1.46, 1.45, 1.44, 1.43, 1.42, 1.41, 1.4, 1.39],
        index=index,
    )
    strategy = GoldSmaRsiStrategy(
        short_ma_length=3,
        long_ma_length=5,
        rsi_period=3,
        rsi_buy_min=0,
        rsi_buy_max=100,
        rsi_sell_min=0,
    )
    signal = strategy.latest_signal(prices)
    assert signal.signal == "SELL"
