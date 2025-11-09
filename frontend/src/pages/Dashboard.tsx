import { useEffect, useState } from "react";

import { fetchLatestSignal, SignalResponse } from "../api/signals";
import SignalCard from "../components/SignalCard";

const Dashboard = () => {
  const [signal, setSignal] = useState<SignalResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadSignal = async () => {
      try {
        setLoading(true);
        const data = await fetchLatestSignal();
        setSignal(data);
      } catch (err) {
        console.error(err);
        setError("Failed to load latest signal.");
      } finally {
        setLoading(false);
      }
    };

    loadSignal();
  }, []);

  if (loading) {
    return <div className="text-sm text-slate-400">Loading latest signal...</div>;
  }

  if (error) {
    return <div className="text-sm text-rose-400">{error}</div>;
  }

  if (!signal) {
    return <div className="text-sm text-slate-400">No signal data.</div>;
  }

  return (
    <div className="space-y-6">
      <SignalCard signal={signal.signal} price={signal.price} timestamp={signal.timestamp} indicators={signal.indicators} />
    </div>
  );
};

export default Dashboard;
