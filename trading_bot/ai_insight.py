"""Utilities for generating AI-powered market insight."""
from __future__ import annotations

import json
import os
import statistics
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Sequence, Tuple
from urllib import error, request

import pandas as pd

from trading_bot.strategy import GoldSmaRsiSignal


@dataclass(frozen=True)
class InsightRequest:
    """Payload sent to the OpenAI API."""

    prompt: str
    model: str
    temperature: float = 0.3
    max_tokens: int = 500


FALLBACK_RESPONSE: Dict[str, Any] = {
    "bias": "neutral",
    "explanation": "AI insight is unavailable at the moment. Not financial advice.",
    "model": None,
    "disclaimer": "AI-generated insight. Not financial advice.",
}


def _format_recent_prices(frame: pd.DataFrame, limit: int = 12) -> Tuple[str, List[float]]:
    closes = frame["close"].tail(limit)
    formatted = ", ".join(
        f"{idx.strftime('%Y-%m-%d %H:%M')}: {price:.2f}" for idx, price in closes.items()
    )
    return formatted, [float(price) for price in closes.values]


def _price_context(prices: Sequence[float]) -> Mapping[str, float]:
    if not prices:
        return {"change_pct": 0.0, "volatility": 0.0}
    start = prices[0]
    end = prices[-1]
    change_pct = 0.0 if start == 0 else (end - start) / start
    if len(prices) <= 1:
        volatility = 0.0
    else:
        returns = [
            (prices[i] - prices[i - 1]) / prices[i - 1]
            for i in range(1, len(prices))
            if prices[i - 1] != 0
        ]
        volatility = statistics.pstdev(returns) if returns else 0.0
    return {"change_pct": change_pct, "volatility": volatility}


def _build_prompt(
    signal: GoldSmaRsiSignal,
    recent_frame: pd.DataFrame,
    headlines: Sequence[str],
    strategy_config: Mapping[str, Any],
) -> str:
    formatted_prices, closes = _format_recent_prices(recent_frame)
    context = _price_context(closes)
    trend = "sideways"
    if context["change_pct"] > 0.01:
        trend = "uptrend"
    elif context["change_pct"] < -0.01:
        trend = "downtrend"

    volatility_desc = "low"
    if context["volatility"] > 0.01:
        volatility_desc = "elevated"
    if context["volatility"] > 0.02:
        volatility_desc = "high"

    news_summary = "; ".join(headlines) if headlines else "No significant news headlines."

    prompt = f"""
You are a trading research assistant. You are NOT a financial advisor and must not give guarantees.
Assess the XAUUSD market using the provided signal and context. Provide concise insight (under 150 words).

Latest signal:
  - Type: {signal.signal}
  - Price: {signal.price:.2f}
  - SMA short ({strategy_config.get('short_ma_length', 20)}): {signal.sma_short:.2f}
  - SMA long ({strategy_config.get('long_ma_length', 50)}): {signal.sma_long:.2f}
  - RSI ({strategy_config.get('rsi_period', 14)}): {signal.rsi:.2f}

Recent closes (most recent last): {formatted_prices}
Estimated trend: {trend}
Volatility regime: {volatility_desc}
Change since oldest close: {context['change_pct'] * 100:.2f}%

Recent headlines: {news_summary}

Return ONLY a JSON object with keys:
  - bias: one of "lean_buy", "neutral", "lean_sell"
  - explanation: brief paragraph highlighting confluence of indicators, market tone, and key risks.
Reiterate that this is not financial advice in the explanation.
""".strip()

    return prompt


def _clean_json_content(content: str) -> str:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        parts = cleaned.split("```")
        if len(parts) >= 3:
            cleaned = parts[1]
        cleaned = cleaned.replace("json", "", 1).strip()
    return cleaned


def _call_openai(request_payload: InsightRequest, api_key: str) -> Tuple[str, str]:
    endpoint = "https://api.openai.com/v1/chat/completions"
    body = json.dumps(
        {
            "model": request_payload.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a cautious trading research assistant.",
                },
                {"role": "user", "content": request_payload.prompt},
            ],
            "temperature": request_payload.temperature,
            "max_tokens": request_payload.max_tokens,
        }
    ).encode("utf-8")

    http_request = request.Request(
        endpoint,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )

    try:
        with request.urlopen(http_request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (error.HTTPError, error.URLError, TimeoutError, ValueError) as exc:
        raise RuntimeError("OpenAI request failed") from exc

    choices = payload.get("choices") or []
    if not choices:
        raise RuntimeError("OpenAI response missing choices")
    message = choices[0].get("message", {})
    content = message.get("content", "")
    if not content:
        raise RuntimeError("OpenAI response missing content")
    return payload.get("model", request_payload.model), content


def generate_ai_insight(
    signal: GoldSmaRsiSignal,
    recent_frame: pd.DataFrame,
    strategy_config: Mapping[str, Any],
    headlines: Sequence[str] | None = None,
) -> Dict[str, Any]:
    """Generate an AI insight dictionary, falling back when unavailable."""

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return dict(FALLBACK_RESPONSE)

    model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
    prompt = _build_prompt(signal, recent_frame, headlines or [], strategy_config)
    request_payload = InsightRequest(prompt=prompt, model=model)

    try:
        model_used, content = _call_openai(request_payload, api_key)
        cleaned = _clean_json_content(content)
        parsed = json.loads(cleaned)
    except Exception:
        return dict(FALLBACK_RESPONSE)

    bias = str(parsed.get("bias", "neutral")).lower()
    if bias not in {"lean_buy", "neutral", "lean_sell"}:
        bias = "neutral"

    explanation = str(parsed.get("explanation", FALLBACK_RESPONSE["explanation"]))

    if "not financial advice" not in explanation.lower():
        explanation = f"{explanation.strip()} Not financial advice."

    return {
        "bias": bias,
        "explanation": explanation,
        "model": model_used,
        "disclaimer": FALLBACK_RESPONSE["disclaimer"],
    }


def stub_headlines() -> List[str]:
    """Return placeholder headlines for the AI prompt."""

    return [
        "Gold traders watch central bank commentary for cues",
        "Markets remain cautious amid mixed inflation signals",
    ]


__all__ = ["generate_ai_insight", "stub_headlines", "FALLBACK_RESPONSE"]
