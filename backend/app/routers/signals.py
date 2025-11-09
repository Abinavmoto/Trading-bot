from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import SignalSnapshot, Strategy
from ..schemas import SignalIndicators, SignalResponse, StrategyParams
from ..services.market_data import fetch_candles
from ..services.strategy import StrategyEngine

router = APIRouter(prefix="/api/signals", tags=["signals"])


def _get_strategy(db: Session, strategy_id: Optional[int]) -> Strategy:
    query = db.query(Strategy)
    if strategy_id is not None:
        strategy = query.filter(Strategy.id == strategy_id).first()
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        return strategy
    strategy = query.order_by(Strategy.id.asc()).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="No strategies configured")
    return strategy


@router.get("/latest", response_model=SignalResponse)
def get_latest_signal(
    symbol: str = Query("XAUUSD"),
    strategy_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
) -> SignalResponse:
    strategy = _get_strategy(db, strategy_id)
    params = StrategyParams(**strategy.parameters)

    end = datetime.utcnow()
    start = end - timedelta(days=30)

    candles = fetch_candles(symbol, start, end)
    engine = StrategyEngine(params)
    result = engine.compute(candles)

    snapshot = SignalSnapshot(
        strategy_id=strategy.id,
        symbol=symbol,
        signal=result.signal,
        indicators=result.indicators,
        price=result.price,
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    return SignalResponse(
        symbol=symbol,
        strategy_id=strategy.id,
        signal=result.signal,
        price=result.price,
        timestamp=snapshot.timestamp,
        indicators=SignalIndicators(**result.indicators),
    )


@router.get("/history")
def get_signal_history(
    symbol: str = Query("XAUUSD"),
    strategy_id: Optional[int] = Query(None),
    start: Optional[datetime] = Query(None, alias="from"),
    end: Optional[datetime] = Query(None, alias="to"),
    db: Session = Depends(get_db),
):
    strategy = _get_strategy(db, strategy_id)
    params = StrategyParams(**strategy.parameters)

    if end is None:
        end = datetime.utcnow()
    if start is None:
        start = end - timedelta(days=180)

    candles = fetch_candles(symbol, start, end)
    engine = StrategyEngine(params)

    history = []
    warmup = max(params.sma_fast, params.sma_slow, params.rsi_period)
    for idx in range(len(candles)):
        window = candles.iloc[: idx + 1]
        if len(window) < warmup:
            continue
        result = engine.compute(window)
        timestamp = candles.index[idx].to_pydatetime()
        history.append(
            {
                "timestamp": timestamp,
                "signal": result.signal,
                "price": result.price,
                "indicators": result.indicators,
            }
        )
    return {"symbol": symbol, "strategy_id": strategy.id, "history": history}
