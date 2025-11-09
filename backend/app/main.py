from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import SessionLocal, engine
from .models import Base, Strategy
from .routers import signals, simulations, strategies

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(signals.router)
app.include_router(simulations.router)
app.include_router(strategies.router)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if not db.query(Strategy).filter(Strategy.name == "gold_sma_rsi_v1").first():
            default_strategy = Strategy(
                name="gold_sma_rsi_v1",
                description="Baseline SMA/RSI strategy for Gold",
                parameters={
                    "sma_fast": 20,
                    "sma_slow": 50,
                    "rsi_period": 14,
                    "rsi_buy_lower": 45,
                    "rsi_buy_upper": 65,
                    "rsi_sell_threshold": 60,
                },
            )
            db.add(default_strategy)
            db.commit()


@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow(), "live_mode": settings.live_mode}
