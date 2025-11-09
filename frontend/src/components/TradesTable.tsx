import { Trade } from "../api/simulations";

interface Props {
  trades?: Trade[];
}

const TradesTable = ({ trades = [] }: Props) => {
  if (!trades.length) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 text-sm text-slate-400">
        No closed trades yet. Run a simulation to generate trade history.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-800">
      <table className="min-w-full divide-y divide-slate-800 text-sm">
        <thead className="bg-slate-900/70 text-xs uppercase tracking-wide text-slate-400">
          <tr>
            <th className="px-4 py-3 text-left">Entry</th>
            <th className="px-4 py-3 text-left">Exit</th>
            <th className="px-4 py-3">Direction</th>
            <th className="px-4 py-3 text-right">Entry Price</th>
            <th className="px-4 py-3 text-right">Exit Price</th>
            <th className="px-4 py-3 text-right">PnL</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800 bg-slate-900/50">
          {trades.map((trade, idx) => (
            <tr key={idx} className="hover:bg-slate-800/40">
              <td className="px-4 py-3">{trade.entry_time ? new Date(trade.entry_time).toLocaleString() : "-"}</td>
              <td className="px-4 py-3">{new Date(trade.exit_time).toLocaleString()}</td>
              <td className="px-4 py-3 text-center">
                <span
                  className={`rounded-full px-3 py-1 text-xs font-semibold ${
                    trade.direction === "LONG" ? "bg-emerald-400/20 text-emerald-300" : "bg-rose-400/20 text-rose-300"
                  }`}
                >
                  {trade.direction}
                </span>
              </td>
              <td className="px-4 py-3 text-right">${trade.entry_price.toFixed(2)}</td>
              <td className="px-4 py-3 text-right">${trade.exit_price.toFixed(2)}</td>
              <td className={`px-4 py-3 text-right ${trade.pnl >= 0 ? "text-emerald-300" : "text-rose-300"}`}>
                {trade.pnl >= 0 ? "+" : ""}${trade.pnl.toFixed(2)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TradesTable;
