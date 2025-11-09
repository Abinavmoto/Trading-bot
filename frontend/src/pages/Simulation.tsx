import { FormEvent, useState } from "react";

import { runSimulation, Simulation } from "../api/simulations";
import { listStrategies } from "../api/strategies";
import EquityChart from "../components/EquityChart";
import MetricsCards from "../components/MetricsCards";
import TradesTable from "../components/TradesTable";

const SimulationPage = () => {
  const [simulation, setSimulation] = useState<Simulation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [startDate, setStartDate] = useState(() => new Date(Date.now() - 1000 * 60 * 60 * 24 * 90).toISOString().slice(0, 10));
  const [endDate, setEndDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [startingBalance, setStartingBalance] = useState(10000);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      setLoading(true);
      setError(null);
      const strategies = await listStrategies();
      const strategy = strategies[0];
      if (!strategy) {
        throw new Error("No strategy configured");
      }
      const result = await runSimulation({
        strategy_id: strategy.id,
        symbol: "XAUUSD",
        start_date: new Date(startDate).toISOString(),
        end_date: new Date(endDate).toISOString(),
        starting_balance: startingBalance
      });
      setSimulation(result);
    } catch (err) {
      console.error(err);
      setError("Failed to run simulation.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <form onSubmit={handleSubmit} className="grid gap-4 rounded-xl border border-slate-800 bg-slate-900/60 p-6 md:grid-cols-4">
        <div className="flex flex-col gap-2">
          <label className="text-xs uppercase tracking-wide text-slate-400">Start Date</label>
          <input
            type="date"
            value={startDate}
            onChange={(event) => setStartDate(event.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white focus:border-sky-500 focus:outline-none"
            required
          />
        </div>
        <div className="flex flex-col gap-2">
          <label className="text-xs uppercase tracking-wide text-slate-400">End Date</label>
          <input
            type="date"
            value={endDate}
            onChange={(event) => setEndDate(event.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white focus:border-sky-500 focus:outline-none"
            required
          />
        </div>
        <div className="flex flex-col gap-2">
          <label className="text-xs uppercase tracking-wide text-slate-400">Starting Balance</label>
          <input
            type="number"
            value={startingBalance}
            onChange={(event) => setStartingBalance(Number(event.target.value))}
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white focus:border-sky-500 focus:outline-none"
            min={1000}
          />
        </div>
        <div className="flex items-end">
          <button
            type="submit"
            className="w-full rounded-lg bg-sky-500 px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-sky-400"
            disabled={loading}
          >
            {loading ? "Running..." : "Run Backtest"}
          </button>
        </div>
      </form>

      {error && <div className="text-sm text-rose-400">{error}</div>}

      {simulation && (
        <div className="space-y-6">
          <MetricsCards
            finalBalance={simulation.final_balance}
            maxDrawdown={simulation.max_drawdown}
            winRate={simulation.win_rate}
            totalTrades={simulation.total_trades}
          />
          <EquityChart equityCurve={simulation.equity_curve} />
          <div>
            <h3 className="mb-3 text-lg font-semibold">Trades</h3>
            <TradesTable trades={simulation.metadata?.trades} />
          </div>
        </div>
      )}
    </div>
  );
};

export default SimulationPage;
