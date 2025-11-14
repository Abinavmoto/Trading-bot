"""Backtesting utilities producing rich result structures."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import pandas as pd

from .data import PriceData


@dataclass(frozen=True)
class TradeResult:
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    side: str
    entry_price: float
    exit_price: float
    size: float
    pnl: float


@dataclass(frozen=True)
class BacktestResult:
    summary: Dict[str, float]
    equity_curve: List[Dict[str, float]]
    drawdown_curve: List[Dict[str, float]]
    trades: List[TradeResult]


def _equity_from_state(cash: float, position: float, price: float) -> float:
    return cash + position * price


def _prepare_actions(strategy: object, prices: pd.Series) -> pd.Series:
    if hasattr(strategy, "generate_trading_actions"):
        actions = strategy.generate_trading_actions(prices)
    elif hasattr(strategy, "generate_signals"):
        positions = strategy.generate_signals(prices)
        actions = positions.diff().fillna(0)
    else:
        raise AttributeError("Strategy must implement generate_trading_actions or generate_signals")
    if not isinstance(actions, pd.Series):
        actions = pd.Series(actions, index=prices.index)
    actions = actions.reindex(prices.index).fillna(0).astype(int)
    return actions


def run_backtest(
    price_data: PriceData,
    strategy: object,
    starting_balance: float,
    unit_size: float = 1.0,
) -> BacktestResult:
    """Execute a backtest and return a detailed result object."""

    if starting_balance <= 0:
        raise ValueError("Starting balance must be positive")
    if unit_size <= 0:
        raise ValueError("Unit size must be positive")

    prices = price_data.frame["close"]
    actions = _prepare_actions(strategy, prices)

    cash = starting_balance
    position = 0.0
    open_entry_time: pd.Timestamp | None = None
    open_entry_price: float | None = None
    trades: List[TradeResult] = []
    equity_curve: List[Dict[str, float]] = []
    drawdown_curve: List[Dict[str, float]] = []
    peak_equity = starting_balance

    for timestamp, price in prices.items():
        action = int(actions.loc[timestamp])

        if action > 0 and position <= 0:
            cost = price * unit_size
            if cost > cash:
                continue
            cash -= cost
            position += unit_size
            open_entry_time = timestamp
            open_entry_price = float(price)
        elif action < 0 and position >= unit_size:
            proceeds = price * unit_size
            cash += proceeds
            position -= unit_size
            if open_entry_time is not None and open_entry_price is not None:
                pnl = (float(price) - open_entry_price) * unit_size
                trades.append(
                    TradeResult(
                        entry_time=open_entry_time,
                        exit_time=timestamp,
                        side="LONG" if unit_size > 0 else "SHORT",
                        entry_price=open_entry_price,
                        exit_price=float(price),
                        size=unit_size,
                        pnl=pnl,
                    )
                )
            open_entry_time = None
            open_entry_price = None

        equity = _equity_from_state(cash, position, float(price))
        equity_curve.append({"timestamp": timestamp, "equity": equity})
        if equity > peak_equity:
            peak_equity = equity
        drawdown = 0.0 if peak_equity <= 0 else (equity - peak_equity) / peak_equity
        drawdown_curve.append({"timestamp": timestamp, "drawdown": drawdown})

    if position > 0 and open_entry_time is not None and open_entry_price is not None:
        last_timestamp = prices.index[-1]
        last_price = float(prices.iloc[-1])
        proceeds = last_price * unit_size
        cash += proceeds
        position -= unit_size
        pnl = (last_price - open_entry_price) * unit_size
        trades.append(
            TradeResult(
                entry_time=open_entry_time,
                exit_time=last_timestamp,
                side="LONG" if unit_size > 0 else "SHORT",
                entry_price=open_entry_price,
                exit_price=last_price,
                size=unit_size,
                pnl=pnl,
            )
        )

        equity = _equity_from_state(cash, position, last_price)
        equity_curve[-1] = {"timestamp": last_timestamp, "equity": equity}
        if equity > peak_equity:
            peak_equity = equity
        drawdown = 0.0 if peak_equity <= 0 else (equity - peak_equity) / peak_equity
        drawdown_curve[-1] = {"timestamp": last_timestamp, "drawdown": drawdown}

    final_balance = cash
    max_drawdown = min((point["drawdown"] for point in drawdown_curve), default=0.0)
    wins = sum(1 for trade in trades if trade.pnl > 0)
    num_trades = len(trades)
    win_rate = wins / num_trades if num_trades else 0.0
    total_return = (final_balance - starting_balance) / starting_balance

    summary = {
        "starting_balance": starting_balance,
        "final_balance": final_balance,
        "max_drawdown": abs(max_drawdown),
        "win_rate": win_rate,
        "num_trades": num_trades,
        "total_return": total_return,
    }

    return BacktestResult(
        summary=summary,
        equity_curve=equity_curve,
        drawdown_curve=drawdown_curve,
        trades=trades,
    )

