import pandas as pd

from trading_bot.ai_insight import FALLBACK_RESPONSE, generate_ai_insight
from trading_bot.config import DEFAULT_CONFIG, save_config
from trading_bot.frontend import create_app
from trading_bot.strategy import GoldSmaRsiSignal


def _sample_signal() -> GoldSmaRsiSignal:
    index = pd.date_range("2023-01-01", periods=60, freq="H", tz="UTC")
    prices = pd.Series([1800 + i for i in range(60)], index=index)
    signal = GoldSmaRsiSignal(
        timestamp=index[-1],
        price=float(prices.iloc[-1]),
        sma_short=float(prices.rolling(5).mean().iloc[-1]),
        sma_long=float(prices.rolling(10).mean().iloc[-1]),
        rsi=55.0,
        signal="BUY",
    )
    return signal


def _sample_frame() -> pd.DataFrame:
    index = pd.date_range("2023-01-01", periods=60, freq="H", tz="UTC")
    data = {
        "open": [1800 + i for i in range(60)],
        "high": [1801 + i for i in range(60)],
        "low": [1799 + i for i in range(60)],
        "close": [1800 + i for i in range(60)],
        "volume": [1000 for _ in range(60)],
    }
    frame = pd.DataFrame(data, index=index)
    frame.index.name = "timestamp"
    return frame


def test_generate_ai_insight_without_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = generate_ai_insight(
        signal=_sample_signal(),
        recent_frame=_sample_frame(),
        strategy_config=DEFAULT_CONFIG["strategy"],
    )
    assert result["bias"] == FALLBACK_RESPONSE["bias"]
    assert "not financial advice" in result["explanation"].lower()


def test_ai_endpoint_returns_fallback(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    config_path = tmp_path / "config.json"
    save_config(DEFAULT_CONFIG, config_path)

    app = create_app(config_path=config_path)
    client = app.test_client()

    response = client.get("/api/ai-insight")
    assert response.status_code == 200
    data = response.get_json()
    assert data["bias"] == "neutral"
    assert data["disclaimer"] == FALLBACK_RESPONSE["disclaimer"]
    assert "symbol" in data
    assert "timestamp" in data
