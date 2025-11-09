"""High-level trading bot orchestration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pandas as pd

from .data import PriceData
from .portfolio import Portfolio


class Strategy(Protocol):
    def generate_trading_actions(self, prices: pd.Series) -> pd.Series:
        ...


@dataclass
class TradingBot:
    """Glue module that wires the strategy, data, and portfolio together."""

    strategy: Strategy
    portfolio: Portfolio

    def run(self, price_data: PriceData) -> dict:
        """Execute the trading strategy against historical prices."""

        closing_prices = price_data.frame["close"]
        actions = self.strategy.generate_trading_actions(closing_prices)
        self.portfolio.apply_signals(closing_prices, actions)
        return self.portfolio.summary()
