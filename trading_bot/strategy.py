"""Trading strategy implementations."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class MovingAverageCrossStrategy:
    """Generate trading signals based on a moving-average crossover."""

    short_window: int = 10
    long_window: int = 30

    def __post_init__(self) -> None:
        if self.short_window <= 0 or self.long_window <= 0:
            raise ValueError("Windows must be positive integers")
        if self.short_window >= self.long_window:
            raise ValueError("Short window must be smaller than long window")

    def generate_signals(self, prices: pd.Series) -> pd.Series:
        """Return a series of position signals (1 for long, 0 for flat)."""

        short_ma = prices.rolling(window=self.short_window, min_periods=1).mean()
        long_ma = prices.rolling(window=self.long_window, min_periods=1).mean()
        signal = (short_ma > long_ma).astype(int)
        return signal

    def generate_trading_actions(self, prices: pd.Series) -> pd.Series:
        """Return trading actions (+1 buy, -1 sell, 0 hold)."""

        positions = self.generate_signals(prices)
        actions = positions.diff().fillna(0).astype(int)
        return actions
