from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Simulation, Strategy
from ..schemas import SimulationRead, SimulationRunRequest, SimulationRunResponse, StrategyParams
from ..services.market_data import fetch_candles
from ..services.simulation import SimulationEngine

router = APIRouter(prefix="/api/simulations", tags=["simulations"])


def _get_strategy(db: Session, strategy_id: int) -> Strategy:
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy


@router.post("/run", response_model=SimulationRunResponse)
def run_simulation(request: SimulationRunRequest, db: Session = Depends(get_db)) -> SimulationRunResponse:
    strategy = _get_strategy(db, request.strategy_id)
    params = StrategyParams(**strategy.parameters)

    candles = fetch_candles(request.symbol, request.start_date, request.end_date)
    engine = SimulationEngine(params)
    results = engine.run(candles, request)

    simulation = Simulation(
        strategy_id=strategy.id,
        symbol=request.symbol,
        start_date=request.start_date,
        end_date=request.end_date,
        starting_balance=request.starting_balance,
        final_balance=results["final_balance"],
        max_drawdown=results["max_drawdown"],
        win_rate=results["win_rate"],
        total_trades=results["total_trades"],
        profitable_trades=results["profitable_trades"],
        equity_curve=results["equity_curve"],
        metadata={
            "strategy_params": strategy.parameters,
            "trades": results["trades"],
        },
    )
    db.add(simulation)
    db.commit()
    db.refresh(simulation)

    return SimulationRunResponse(simulation=_to_schema(simulation))


@router.get("/{simulation_id}", response_model=SimulationRead)
def get_simulation(simulation_id: int, db: Session = Depends(get_db)) -> SimulationRead:
    simulation = db.query(Simulation).filter(Simulation.id == simulation_id).first()
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return _to_schema(simulation)


def _to_schema(simulation: Simulation) -> SimulationRead:
    return SimulationRead(
        id=simulation.id,
        strategy_id=simulation.strategy_id,
        symbol=simulation.symbol,
        start_date=simulation.start_date,
        end_date=simulation.end_date,
        starting_balance=simulation.starting_balance,
        final_balance=simulation.final_balance,
        max_drawdown=simulation.max_drawdown,
        win_rate=simulation.win_rate,
        total_trades=simulation.total_trades,
        profitable_trades=simulation.profitable_trades,
        equity_curve=simulation.equity_curve,
        metadata=simulation.metadata,
        created_at=simulation.created_at,
    )
