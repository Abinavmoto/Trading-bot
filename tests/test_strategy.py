import pandas as pd
import pytest

from trading_bot.strategy import MovingAverageCrossStrategy


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
