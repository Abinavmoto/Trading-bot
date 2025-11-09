import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

import { EquityPoint } from "../api/simulations";

interface Props {
  equityCurve: EquityPoint[];
}

const EquityChart = ({ equityCurve }: Props) => {
  const data = equityCurve.map((point) => ({
    ...point,
    equity: Number(point.equity.toFixed(2)),
    drawdownPct: Number((point.drawdown * 100).toFixed(2))
  }));

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-6">
      <h3 className="mb-4 text-lg font-semibold">Equity Curve</h3>
      <ResponsiveContainer width="100%" height={320}>
        <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="equity" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#38bdf8" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="drawdown" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#f87171" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#f87171" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis dataKey="timestamp" tickFormatter={(value) => new Date(value).toLocaleDateString()} stroke="#475569" />
          <YAxis yAxisId="left" stroke="#475569" domain={["auto", "auto"]} />
          <YAxis yAxisId="right" orientation="right" stroke="#475569" unit="%" />
          <Tooltip
            contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #1e293b", borderRadius: "0.75rem" }}
            labelFormatter={(label) => new Date(label).toLocaleString()}
            formatter={(value: number, name) => [name === "drawdownPct" ? `${value.toFixed(2)}%` : `$${value.toFixed(2)}`, name === "drawdownPct" ? "Drawdown" : "Equity"]}
          />
          <Legend />
          <Area yAxisId="left" type="monotone" dataKey="equity" stroke="#38bdf8" fill="url(#equity)" name="Equity" />
          <Area yAxisId="right" type="monotone" dataKey="drawdownPct" stroke="#f87171" fill="url(#drawdown)" name="Drawdown" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default EquityChart;
