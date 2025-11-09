from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class StrategyParams(BaseModel):
    sma_fast: int = Field(default=20, ge=1)
    sma_slow: int = Field(default=50, ge=1)
    rsi_period: int = Field(default=14, ge=1)
    rsi_buy_lower: float = Field(default=45, ge=0, le=100)
    rsi_buy_upper: float = Field(default=65, ge=0, le=100)
    rsi_sell_threshold: float = Field(default=60, ge=0, le=100)


class StrategyBase(BaseModel):
    name: str
    description: Optional[str]
    parameters: StrategyParams


class StrategyCreate(BaseModel):
    name: str
    description: Optional[str]
    parameters: StrategyParams


class StrategyRead(StrategyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class SignalIndicators(BaseModel):
    sma_fast: float
    sma_slow: float
    rsi: float


class SignalResponse(BaseModel):
    symbol: str
    strategy_id: int
    signal: str
    price: float
    timestamp: datetime
    indicators: SignalIndicators


class SimulationRunRequest(BaseModel):
    strategy_id: int
    symbol: str
    start_date: datetime
    end_date: datetime
    starting_balance: float = 10_000.0


class EquityPoint(BaseModel):
    timestamp: datetime
    equity: float
    drawdown: float


class SimulationRead(BaseModel):
    id: int
    strategy_id: int
    symbol: str
    start_date: datetime
    end_date: datetime
    starting_balance: float
    final_balance: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    profitable_trades: int
    equity_curve: List[EquityPoint]
    metadata: Dict[str, Any]
    created_at: datetime

    class Config:
        orm_mode = True


class SimulationSummary(BaseModel):
    id: int
    strategy_id: int
    symbol: str
    start_date: datetime
    end_date: datetime
    final_balance: float
    max_drawdown: float
    win_rate: float


class SimulationRunResponse(BaseModel):
    simulation: SimulationRead
