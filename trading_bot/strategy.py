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


@dataclass(frozen=True)
class GoldSmaRsiSignal:
    """Structured representation of the gold SMA+RSI strategy output."""

    timestamp: pd.Timestamp
    price: float
    sma_short: float
    sma_long: float
    rsi: float
    signal: str


def _compute_rsi(prices: pd.Series, period: int) -> pd.Series:
    if period <= 0:
        raise ValueError("RSI period must be positive")
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50.0)


@dataclass(frozen=True)
class GoldSmaRsiStrategy:
    """Generate trading signals for gold (XAUUSD) using SMA and RSI filters."""

    short_ma_length: int = 20
    long_ma_length: int = 50
    rsi_period: int = 14
    rsi_buy_min: float = 45.0
    rsi_buy_max: float = 65.0
    rsi_sell_min: float = 60.0

    def __post_init__(self) -> None:
        if self.short_ma_length <= 0 or self.long_ma_length <= 0:
            raise ValueError("Moving-average lengths must be positive")
        if self.short_ma_length >= self.long_ma_length:
            raise ValueError("Short moving average must be shorter than long moving average")
        if self.rsi_period <= 0:
            raise ValueError("RSI period must be positive")
        if self.rsi_buy_min >= self.rsi_buy_max:
            raise ValueError("RSI buy minimum must be lower than the maximum")

    def indicator_frame(self, prices: pd.Series) -> pd.DataFrame:
        """Return a dataframe containing indicators and signals for each timestamp."""

        if len(prices) < self.long_ma_length:
            raise ValueError("Not enough data to compute long moving average")

        sma_short = prices.rolling(window=self.short_ma_length, min_periods=1).mean()
        sma_long = prices.rolling(window=self.long_ma_length, min_periods=1).mean()
        rsi_series = _compute_rsi(prices, self.rsi_period)

        signals = [
            self._determine_signal(price, short, long, rsi)
            for price, short, long, rsi in zip(prices, sma_short, sma_long, rsi_series)
        ]

        frame = pd.DataFrame(
            {
                "price": prices,
                "sma_short": sma_short,
                "sma_long": sma_long,
                "rsi": rsi_series,
                "signal": signals,
            }
        )
        frame.index.name = prices.index.name
        return frame

    def _determine_signal(
        self, price: float, sma_short: float, sma_long: float, rsi: float
    ) -> str:
        if price > sma_short and sma_short > sma_long and self.rsi_buy_min <= rsi <= self.rsi_buy_max:
            return "BUY"
        if price < sma_short and sma_short < sma_long and rsi >= self.rsi_sell_min:
            return "SELL"
        return "HOLD"

    def latest_signal(self, prices: pd.Series) -> GoldSmaRsiSignal:
        """Return the most recent trading signal."""

        frame = self.indicator_frame(prices)
        last_row = frame.iloc[-1]
        timestamp = frame.index[-1]
        return GoldSmaRsiSignal(
            timestamp=timestamp,
            price=float(last_row["price"]),
            sma_short=float(last_row["sma_short"]),
            sma_long=float(last_row["sma_long"]),
            rsi=float(last_row["rsi"]),
            signal=str(last_row["signal"]),
        )

    def generate_trading_actions(self, prices: pd.Series) -> pd.Series:
        """Map strategy signals to trade actions compatible with the backtest engine."""

        frame = self.indicator_frame(prices)
        signal_to_position = (
            frame["signal"].map({"BUY": 1, "SELL": 0}).ffill().fillna(0).astype(float)
        )
        signal_to_position = signal_to_position.clip(lower=0, upper=1)
        actions = signal_to_position.diff().fillna(signal_to_position.iloc[0]).astype(int)
        actions = actions.clip(-1, 1)
        return actions

    def generate_signals(self, prices: pd.Series) -> pd.Series:
        """Expose a position series for compatibility with legacy code paths."""

        frame = self.indicator_frame(prices)
        return frame["signal"].map({"BUY": 1}).fillna(0).astype(int)
