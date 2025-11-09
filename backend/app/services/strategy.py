from dataclasses import dataclass
from typing import Dict, List

import pandas as pd

from ..schemas import StrategyParams


@dataclass
class StrategyResult:
    signal: str
    price: float
    indicators: Dict[str, float]


class StrategyEngine:
    def __init__(self, params: StrategyParams):
        self.params = params

    def compute(self, candles: pd.DataFrame) -> StrategyResult:
        if candles.empty:
            raise ValueError("No candles provided")

        close = candles["close"]
        sma_fast = close.rolling(window=self.params.sma_fast).mean()
        sma_slow = close.rolling(window=self.params.sma_slow).mean()
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=self.params.rsi_period).mean()
        avg_loss = loss.rolling(window=self.params.rsi_period).mean()
        rs = avg_gain / avg_loss.replace({0: float("inf")})
        rsi = 100 - (100 / (1 + rs))

        latest = candles.iloc[-1]
        latest_sma_fast = float(sma_fast.iloc[-1])
        latest_sma_slow = float(sma_slow.iloc[-1])
        latest_rsi = float(rsi.iloc[-1])

        signal = "HOLD"
        price = float(latest["close"])

        if (
            price > latest_sma_fast
            and latest_sma_fast > latest_sma_slow
            and self.params.rsi_buy_lower <= latest_rsi <= self.params.rsi_buy_upper
        ):
            signal = "BUY"
        elif price < latest_sma_fast and latest_sma_fast < latest_sma_slow and latest_rsi > self.params.rsi_sell_threshold:
            signal = "SELL"

        return StrategyResult(
            signal=signal,
            price=price,
            indicators={
                "sma_fast": latest_sma_fast,
                "sma_slow": latest_sma_slow,
                "rsi": latest_rsi,
            },
        )

    def generate_signals(self, candles: pd.DataFrame) -> List[StrategyResult]:
        results: List[StrategyResult] = []
        for idx in range(len(candles)):
            window = candles.iloc[: idx + 1]
            if len(window) < max(self.params.sma_fast, self.params.sma_slow, self.params.rsi_period):
                continue
            result = self.compute(window)
            results.append(result)
        return results
