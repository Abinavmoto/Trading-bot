"""High-level trading bot orchestration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pandas as pd

from .data import PriceData
from .portfolio import Portfolio
from .simulation import BacktestResult, run_backtest


class Strategy(Protocol):
    def generate_trading_actions(self, prices: pd.Series) -> pd.Series:
        ...


@dataclass
class TradingBot:
    """Glue module that wires the strategy, data, and portfolio together."""

    strategy: Strategy
    portfolio: Portfolio

    def run(self, price_data: PriceData) -> BacktestResult:
        """Execute the trading strategy against historical prices."""

        result = run_backtest(
            price_data=price_data,
            strategy=self.strategy,
            starting_balance=self.portfolio.starting_cash,
            unit_size=self.portfolio.unit_size,
        )
        return result
