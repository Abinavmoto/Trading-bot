"""Portfolio and execution utilities for the trading bot."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import pandas as pd


@dataclass
class Trade:
    timestamp: pd.Timestamp
    action: str
    price: float
    quantity: float
    cash_after: float
    position_after: float


@dataclass
class Portfolio:
    """A simple portfolio that trades a single instrument."""

    starting_cash: float
    unit_size: float = 1.0
    trades: List[Trade] = field(default_factory=list)
    cash: float = field(init=False)
    position: float = field(init=False)

    def __post_init__(self) -> None:
        if self.starting_cash <= 0:
            raise ValueError("Starting cash must be positive")
        if self.unit_size <= 0:
            raise ValueError("Unit size must be positive")
        self.cash = self.starting_cash
        self.position = 0.0

    def _execute_trade(self, timestamp: pd.Timestamp, action: str, price: float) -> None:
        """Execute a trade and update portfolio state."""

        if action == "BUY":
            cost = price * self.unit_size
            if cost > self.cash:
                raise ValueError("Insufficient cash to execute buy trade")
            self.cash -= cost
            self.position += self.unit_size
        elif action == "SELL":
            if self.position < self.unit_size:
                raise ValueError("Insufficient position to execute sell trade")
            proceeds = price * self.unit_size
            self.cash += proceeds
            self.position -= self.unit_size
        else:
            raise ValueError(f"Unknown action {action}")

        self.trades.append(
            Trade(
                timestamp=timestamp,
                action=action,
                price=price,
                quantity=self.unit_size,
                cash_after=self.cash,
                position_after=self.position,
            )
        )

    def apply_signals(self, prices: pd.Series, actions: pd.Series) -> None:
        """Execute trades based on provided actions."""

        if not prices.index.equals(actions.index):
            raise ValueError("Prices and actions must share the same index")

        for timestamp, action in actions.items():
            price = float(prices.loc[timestamp])
            if action > 0 and self.position <= 0:
                self._execute_trade(timestamp, "BUY", price)
            elif action < 0 and self.position >= self.unit_size:
                self._execute_trade(timestamp, "SELL", price)

    @property
    def market_value(self) -> float:
        """Return the current market value (cash + holdings valued at last price)."""

        if not self.trades:
            return self.cash
        last_price = self.trades[-1].price
        return self.cash + self.position * last_price

    def equity_curve(self, prices: pd.Series) -> pd.Series:
        """Return the portfolio equity curve over the provided price series."""

        equity = []
        current_cash = self.cash
        current_position = self.position
        for price in prices:
            equity.append(current_cash + current_position * price)
        return pd.Series(equity, index=prices.index)

    def summary(self) -> dict:
        """Return a dictionary summarising portfolio performance."""

        total_return = (self.market_value - self.starting_cash) / self.starting_cash
        return {
            "starting_cash": self.starting_cash,
            "ending_cash": self.cash,
            "position": self.position,
            "market_value": self.market_value,
            "total_return": total_return,
            "trades": [trade.__dict__ for trade in self.trades],
        }
