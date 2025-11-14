"""Command-line interface for running the trading bot backtest."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from trading_bot.bot import TradingBot
from trading_bot.data import PriceData, load_price_data, resample_prices
from trading_bot.portfolio import Portfolio
from trading_bot.strategy import MovingAverageCrossStrategy


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a moving average crossover trading bot")
    parser.add_argument("data", type=Path, help="Path to a CSV file containing OHLCV data")
    parser.add_argument("--short-window", type=int, default=10, help="Short moving average window")
    parser.add_argument("--long-window", type=int, default=30, help="Long moving average window")
    parser.add_argument("--resample", type=str, default=None, help="Optional pandas resample rule (e.g. '1H')")
    parser.add_argument("--starting-cash", type=float, default=10_000.0, help="Initial portfolio cash")
    parser.add_argument("--unit-size", type=float, default=1.0, help="Number of units to trade per signal")
    return parser.parse_args(argv)


def build_bot(args: argparse.Namespace, price_data: PriceData) -> TradingBot:
    strategy = MovingAverageCrossStrategy(short_window=args.short_window, long_window=args.long_window)
    portfolio = Portfolio(starting_cash=args.starting_cash, unit_size=args.unit_size)
    return TradingBot(strategy=strategy, portfolio=portfolio)


def main(argv: Optional[list[str]] = None) -> dict:
    args = parse_args(argv)
    price_data = load_price_data(args.data)
    if args.resample:
        price_data = resample_prices(price_data, args.resample)

    bot = build_bot(args, price_data)
    result = bot.run(price_data)
    summary = result.summary
    print("Trading summary:")
    for key, value in summary.items():
        print(f"{key}: {value}")
    if result.trades:
        print("Trades:")
        for trade in result.trades:
            print(
                "  "
                + f"{trade.entry_time} - {trade.side} {trade.size} @ {trade.entry_price}"
                + f" -> {trade.exit_price} (PnL: {trade.pnl})"
            )
    return summary


if __name__ == "__main__":
    main()
