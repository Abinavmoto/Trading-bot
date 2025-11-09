from datetime import datetime
from typing import Dict, List

import pandas as pd

from ..config import get_settings
from ..schemas import EquityPoint, SimulationRunRequest, StrategyParams
from .strategy import StrategyEngine


class SimulationEngine:
    def __init__(self, params: StrategyParams):
        self.params = params
        self.settings = get_settings()
        self.strategy_engine = StrategyEngine(params)

    def run(self, candles: pd.DataFrame, request: SimulationRunRequest) -> Dict:
        if candles.empty:
            raise ValueError("No candles to simulate")
        warmup = max(self.params.sma_fast, self.params.sma_slow, self.params.rsi_period)
        balance = request.starting_balance
        position = 0
        entry_price = 0.0
        entry_time: datetime | None = None
        position_size = 0.0
        total_trades = 0
        profitable_trades = 0
        equity_curve: List[Dict] = []
        trades: List[Dict] = []
        peak_equity = balance
        max_drawdown = 0.0

        for idx in range(len(candles)):
            window = candles.iloc[: idx + 1]
            timestamp = candles.index[idx].to_pydatetime()
            price = float(candles.iloc[idx]["close"])

            if len(window) < warmup:
                equity_curve.append({"timestamp": timestamp, "equity": balance, "drawdown": 0.0})
                continue

            result = self.strategy_engine.compute(window)
            target_position = self._signal_to_position(result.signal)

            if position != 0:
                unrealized = (price - entry_price) * position * position_size
                current_equity = balance + unrealized
            else:
                current_equity = balance

            if target_position != position:
                if position != 0:
                    realized = (price - entry_price) * position * position_size
                    balance += realized
                    total_trades += 1
                    if realized > 0:
                        profitable_trades += 1
                    trades.append(
                        {
                            "entry_time": entry_time.isoformat() if entry_time else None,
                            "exit_time": timestamp.isoformat(),
                            "direction": "LONG" if position > 0 else "SHORT",
                            "entry_price": entry_price,
                            "exit_price": price,
                            "pnl": realized,
                        }
                    )
                    position = 0
                    entry_price = 0.0
                    position_size = 0.0
                    entry_time = None
                    current_equity = balance

                if target_position != 0:
                    position = target_position
                    entry_price = price
                    entry_time = timestamp
                    position_size = balance * 0.01

            if position != 0:
                current_equity = balance + (price - entry_price) * position * position_size
            else:
                current_equity = balance

            peak_equity = max(peak_equity, current_equity)
            drawdown = (peak_equity - current_equity) / peak_equity if peak_equity > 0 else 0.0
            max_drawdown = max(max_drawdown, drawdown)
            equity_curve.append({"timestamp": timestamp, "equity": current_equity, "drawdown": drawdown})

        if position != 0:
            price = float(candles.iloc[-1]["close"])
            timestamp = candles.index[-1].to_pydatetime()
            realized = (price - entry_price) * position * position_size
            balance += realized
            total_trades += 1
            if realized > 0:
                profitable_trades += 1
            trades.append(
                {
                    "entry_time": entry_time.isoformat() if entry_time else None,
                    "exit_time": timestamp.isoformat(),
                    "direction": "LONG" if position > 0 else "SHORT",
                    "entry_price": entry_price,
                    "exit_price": price,
                    "pnl": realized,
                }
            )
            position = 0
            entry_price = 0.0
            position_size = 0.0
            entry_time = None

        final_equity = balance
        win_rate = (profitable_trades / total_trades) if total_trades > 0 else 0.0

        equity_points = [
            EquityPoint(timestamp=item["timestamp"], equity=item["equity"], drawdown=item["drawdown"]).dict()
            for item in equity_curve
        ]

        return {
            "final_balance": final_equity,
            "max_drawdown": max_drawdown,
            "win_rate": win_rate,
            "total_trades": total_trades,
            "profitable_trades": profitable_trades,
            "equity_curve": equity_points,
            "trades": trades,
        }

    def _signal_to_position(self, signal: str) -> int:
        if signal == "BUY":
            return 1
        if signal == "SELL":
            return -1
        return 0
