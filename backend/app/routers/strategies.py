from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Strategy
from ..schemas import StrategyCreate, StrategyRead

router = APIRouter(prefix="/api/strategies", tags=["strategies"])


@router.get("", response_model=list[StrategyRead])
def list_strategies(db: Session = Depends(get_db)) -> list[StrategyRead]:
    strategies = db.query(Strategy).order_by(Strategy.id.asc()).all()
    return [StrategyRead.from_orm(strategy) for strategy in strategies]


@router.post("", response_model=StrategyRead)
def create_or_update_strategy(payload: StrategyCreate, db: Session = Depends(get_db)) -> StrategyRead:
    strategy = db.query(Strategy).filter(Strategy.name == payload.name).first()
    if strategy:
        strategy.description = payload.description
        strategy.parameters = payload.parameters.dict()
    else:
        strategy = Strategy(
            name=payload.name,
            description=payload.description,
            parameters=payload.parameters.dict(),
        )
        db.add(strategy)
    db.commit()
    db.refresh(strategy)
    return StrategyRead.from_orm(strategy)
