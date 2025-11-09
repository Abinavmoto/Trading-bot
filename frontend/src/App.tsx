import { NavLink, Route, Routes } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Simulation from "./pages/Simulation";
import StrategyConfig from "./pages/StrategyConfig";

const App = () => {
  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <header className="border-b border-slate-800">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <h1 className="text-2xl font-semibold">Gold Signal Lab</h1>
          <nav className="flex gap-4 text-sm font-medium text-slate-300">
            <NavLink to="/" end className={({ isActive }) => (isActive ? "text-white" : "hover:text-white")}>Dashboard</NavLink>
            <NavLink to="/simulation" className={({ isActive }) => (isActive ? "text-white" : "hover:text-white")}>Simulation</NavLink>
            <NavLink to="/strategy" className={({ isActive }) => (isActive ? "text-white" : "hover:text-white")}>Strategy Config</NavLink>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/simulation" element={<Simulation />} />
          <Route path="/strategy" element={<StrategyConfig />} />
        </Routes>
      </main>
    </div>
  );
};

export default App;
