import pandas as pd

from trading_bot.bot import TradingBot
from trading_bot.data import load_price_data
from trading_bot.portfolio import Portfolio
from trading_bot.strategy import MovingAverageCrossStrategy


def test_portfolio_executes_trades() -> None:
    index = pd.date_range("2023-01-01", periods=5, freq="D")
    prices = pd.Series([1, 2, 3, 2, 1], index=index)
    actions = pd.Series([0, 1, 0, -1, 0], index=index)
    portfolio = Portfolio(starting_cash=1000, unit_size=1)
    portfolio.apply_signals(prices, actions)
    assert len(portfolio.trades) == 2
    assert portfolio.position == 0


def test_trading_bot_summary() -> None:
    data = load_price_data("data/sample_data.csv")
    strategy = MovingAverageCrossStrategy(short_window=2, long_window=5)
    portfolio = Portfolio(starting_cash=1000, unit_size=1)
    bot = TradingBot(strategy=strategy, portfolio=portfolio)
    result = bot.run(data)
    assert "total_return" in result.summary
    assert isinstance(result.trades, list)
