interface MetricCardProps {
  title: string;
  value: string;
  accent?: string;
}

const MetricCard = ({ title, value, accent = "text-white" }: MetricCardProps) => (
  <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 shadow">
    <p className="text-xs uppercase tracking-wide text-slate-500">{title}</p>
    <p className={`mt-2 text-2xl font-semibold ${accent}`}>{value}</p>
  </div>
);

interface MetricsCardsProps {
  finalBalance: number;
  maxDrawdown: number;
  winRate: number;
  totalTrades: number;
}

const MetricsCards = ({ finalBalance, maxDrawdown, winRate, totalTrades }: MetricsCardsProps) => {
  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
      <MetricCard title="Final Balance" value={`$${finalBalance.toFixed(2)}`} accent="text-emerald-400" />
      <MetricCard title="Max Drawdown" value={`${(maxDrawdown * 100).toFixed(2)}%`} accent="text-rose-400" />
      <MetricCard title="Win Rate" value={`${(winRate * 100).toFixed(1)}%`} accent="text-sky-400" />
      <MetricCard title="Trades" value={totalTrades.toString()} accent="text-amber-300" />
    </div>
  );
};

export default MetricsCards;
