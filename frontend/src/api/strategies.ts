import client from "./client";

export interface StrategyParams {
  sma_fast: number;
  sma_slow: number;
  rsi_period: number;
  rsi_buy_lower: number;
  rsi_buy_upper: number;
  rsi_sell_threshold: number;
}

export interface Strategy {
  id: number;
  name: string;
  description?: string;
  parameters: StrategyParams;
}

export interface StrategyPayload {
  name: string;
  description?: string;
  parameters: StrategyParams;
}

export async function listStrategies() {
  const response = await client.get<Strategy[]>("/strategies");
  return response.data;
}

export async function saveStrategy(payload: StrategyPayload) {
  const response = await client.post<Strategy>("/strategies", payload);
  return response.data;
}
