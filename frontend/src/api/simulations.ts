import client from "./client";

export interface EquityPoint {
  timestamp: string;
  equity: number;
  drawdown: number;
}

export interface Trade {
  entry_time: string | null;
  exit_time: string;
  direction: "LONG" | "SHORT";
  entry_price: number;
  exit_price: number;
  pnl: number;
}

export interface SimulationMetadata {
  trades?: Trade[];
  strategy_params?: Record<string, unknown>;
}

export interface Simulation {
  id: number;
  strategy_id: number;
  symbol: string;
  start_date: string;
  end_date: string;
  starting_balance: number;
  final_balance: number;
  max_drawdown: number;
  win_rate: number;
  total_trades: number;
  profitable_trades: number;
  equity_curve: EquityPoint[];
  metadata?: SimulationMetadata;
}

export interface SimulationRequest {
  strategy_id: number;
  symbol: string;
  start_date: string;
  end_date: string;
  starting_balance: number;
}

export async function runSimulation(payload: SimulationRequest) {
  const response = await client.post<{ simulation: Simulation }>("/simulations/run", payload);
  return response.data.simulation;
}

export async function fetchSimulation(id: number) {
  const response = await client.get<Simulation>(`/simulations/${id}`);
  return response.data;
}
