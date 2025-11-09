import { FormEvent, useEffect, useState } from "react";

import { listStrategies, saveStrategy, Strategy, StrategyParams } from "../api/strategies";

const StrategyConfig = () => {
  const [strategy, setStrategy] = useState<Strategy | null>(null);
  const [params, setParams] = useState<StrategyParams | null>(null);
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      const strategies = await listStrategies();
      if (strategies.length > 0) {
        setStrategy(strategies[0]);
        setParams(strategies[0].parameters);
      }
    };
    load();
  }, []);

  const handleChange = (key: keyof StrategyParams, value: number) => {
    if (!params) return;
    setParams({ ...params, [key]: value });
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!strategy || !params) return;
    await saveStrategy({ name: strategy.name, description: strategy.description, parameters: params });
    setStatus("Strategy parameters updated successfully.");
    setTimeout(() => setStatus(null), 4000);
  };

  if (!params) {
    return <div className="text-sm text-slate-400">Loading strategy configuration...</div>;
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6 rounded-xl border border-slate-800 bg-slate-900/60 p-6">
      <div>
        <h2 className="text-lg font-semibold text-white">{strategy?.name ?? "Strategy"}</h2>
        <p className="text-sm text-slate-400">Tune the SMA and RSI thresholds used by the signal engine.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="flex flex-col gap-2">
          <label className="text-xs uppercase tracking-wide text-slate-400">SMA Fast</label>
          <input
            type="number"
            min={5}
            value={params.sma_fast}
            onChange={(event) => handleChange("sma_fast", Number(event.target.value))}
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white focus:border-sky-500 focus:outline-none"
            required
          />
        </div>
        <div className="flex flex-col gap-2">
          <label className="text-xs uppercase tracking-wide text-slate-400">SMA Slow</label>
          <input
            type="number"
            min={10}
            value={params.sma_slow}
            onChange={(event) => handleChange("sma_slow", Number(event.target.value))}
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white focus:border-sky-500 focus:outline-none"
            required
          />
        </div>
        <div className="flex flex-col gap-2">
          <label className="text-xs uppercase tracking-wide text-slate-400">RSI Period</label>
          <input
            type="number"
            min={5}
            value={params.rsi_period}
            onChange={(event) => handleChange("rsi_period", Number(event.target.value))}
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white focus:border-sky-500 focus:outline-none"
            required
          />
        </div>
        <div className="flex flex-col gap-2">
          <label className="text-xs uppercase tracking-wide text-slate-400">RSI Buy Range</label>
          <div className="flex gap-2">
            <input
              type="number"
              value={params.rsi_buy_lower}
              onChange={(event) => handleChange("rsi_buy_lower", Number(event.target.value))}
              className="w-1/2 rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white focus:border-sky-500 focus:outline-none"
            />
            <input
              type="number"
              value={params.rsi_buy_upper}
              onChange={(event) => handleChange("rsi_buy_upper", Number(event.target.value))}
              className="w-1/2 rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white focus:border-sky-500 focus:outline-none"
            />
          </div>
        </div>
        <div className="flex flex-col gap-2 md:col-span-2">
          <label className="text-xs uppercase tracking-wide text-slate-400">RSI Sell Threshold</label>
          <input
            type="number"
            value={params.rsi_sell_threshold}
            onChange={(event) => handleChange("rsi_sell_threshold", Number(event.target.value))}
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white focus:border-sky-500 focus:outline-none"
          />
        </div>
      </div>

      <button
        type="submit"
        className="rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-emerald-400"
      >
        Save Strategy
      </button>

      {status && <div className="text-sm text-emerald-300">{status}</div>}
    </form>
  );
};

export default StrategyConfig;
