import { SignalIndicators } from "../api/signals";

interface Props {
  signal: "BUY" | "SELL" | "HOLD";
  price: number;
  timestamp: string;
  indicators: SignalIndicators;
}

const signalColor: Record<Props["signal"], string> = {
  BUY: "bg-buy/20 text-buy",
  SELL: "bg-sell/20 text-sell",
  HOLD: "bg-hold/20 text-hold"
};

const SignalCard = ({ signal, price, timestamp, indicators }: Props) => {
  const formattedDate = new Date(timestamp).toLocaleString();
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-6 shadow-lg">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm uppercase tracking-wide text-slate-400">Current Signal</p>
          <h2 className={`mt-2 inline-flex items-center rounded-full px-4 py-2 text-xl font-semibold ${signalColor[signal]}`}>
            {signal}
          </h2>
        </div>
        <div className="text-right">
          <p className="text-sm text-slate-400">Spot Price</p>
          <p className="text-2xl font-semibold text-white">${price.toFixed(2)}</p>
          <p className="mt-1 text-xs text-slate-500">Updated {formattedDate}</p>
        </div>
      </div>
      <div className="mt-6 grid grid-cols-3 gap-4 text-center text-sm text-slate-300">
        <div className="rounded-lg border border-slate-800 p-3">
          <p className="text-xs uppercase text-slate-500">SMA Fast</p>
          <p className="mt-1 text-lg font-semibold">{indicators.sma_fast.toFixed(2)}</p>
        </div>
        <div className="rounded-lg border border-slate-800 p-3">
          <p className="text-xs uppercase text-slate-500">SMA Slow</p>
          <p className="mt-1 text-lg font-semibold">{indicators.sma_slow.toFixed(2)}</p>
        </div>
        <div className="rounded-lg border border-slate-800 p-3">
          <p className="text-xs uppercase text-slate-500">RSI</p>
          <p className="mt-1 text-lg font-semibold">{indicators.rsi.toFixed(2)}</p>
        </div>
      </div>
    </div>
  );
};

export default SignalCard;
