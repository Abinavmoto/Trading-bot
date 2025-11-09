import client from "./client";

export interface SignalIndicators {
  sma_fast: number;
  sma_slow: number;
  rsi: number;
}

export interface SignalResponse {
  symbol: string;
  strategy_id: number;
  signal: "BUY" | "SELL" | "HOLD";
  price: number;
  timestamp: string;
  indicators: SignalIndicators;
}

export interface SignalHistoryEntry {
  timestamp: string;
  signal: string;
  price: number;
  indicators: SignalIndicators;
}

export async function fetchLatestSignal(symbol = "XAUUSD"): Promise<SignalResponse> {
  const response = await client.get<SignalResponse>("/signals/latest", { params: { symbol } });
  return response.data;
}

export async function fetchSignalHistory(symbol = "XAUUSD") {
  const response = await client.get<{ history: SignalHistoryEntry[] }>("/signals/history", {
    params: { symbol }
  });
  return response.data.history;
}
