from datetime import datetime
from typing import Any, Dict

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    parameters = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    simulations = relationship("Simulation", back_populates="strategy")


class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)
    symbol = Column(String(50), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    starting_balance = Column(Float, nullable=False)
    final_balance = Column(Float, nullable=False)
    max_drawdown = Column(Float, nullable=False)
    win_rate = Column(Float, nullable=False)
    total_trades = Column(Integer, nullable=False)
    profitable_trades = Column(Integer, nullable=False)
    equity_curve = Column(JSON, nullable=False)
    metadata = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    strategy = relationship("Strategy", back_populates="simulations")


class SignalSnapshot(Base):
    __tablename__ = "signal_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)
    symbol = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    signal = Column(String(10), nullable=False)
    indicators = Column(JSON, nullable=False)
    price = Column(Float, nullable=False)

    strategy = relationship("Strategy")
