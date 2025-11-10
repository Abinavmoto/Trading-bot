(function () {
  const signalStatusEl = document.getElementById("signal-status");
  const symbolEl = document.getElementById("signal-symbol");
  const timeframeEl = document.getElementById("signal-timeframe");
  const timestampEl = document.getElementById("signal-timestamp");
  const priceEl = document.getElementById("signal-price");
  const smaShortEl = document.getElementById("signal-sma-short");
  const smaLongEl = document.getElementById("signal-sma-long");
  const rsiEl = document.getElementById("signal-rsi");
  const simulationForm = document.getElementById("simulation-form");
  const simulationSummary = document.getElementById("simulation-summary");
  const summaryFinal = document.getElementById("summary-final-balance");
  const summaryDrawdown = document.getElementById("summary-max-drawdown");
  const summaryWinRate = document.getElementById("summary-win-rate");
  const summaryTrades = document.getElementById("summary-num-trades");
  const chartCard = document.getElementById("chart-card");
  const refreshSignalBtn = document.getElementById("refresh-signal");
  const refreshAiBtn = document.getElementById("refresh-ai");
  const aiBiasEl = document.getElementById("ai-bias");
  const aiExplanationEl = document.getElementById("ai-explanation");

  let equityChart;

  const formatCurrency = (value) => {
    if (value === null || value === undefined || Number.isNaN(value)) {
      return "—";
    }
    return Number(value).toLocaleString(undefined, {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
    });
  };

  const formatPercent = (value) => {
    if (value === null || value === undefined || Number.isNaN(value)) {
      return "—";
    }
    return `${(Number(value) * 100).toFixed(2)}%`;
  };

  const setSignalClass = (signal) => {
    signalStatusEl.classList.remove("buy", "sell", "hold");
    if (!signal) {
      return;
    }
    const className = signal.toLowerCase();
    signalStatusEl.classList.add(className);
  };

  const updateSignalCard = (data) => {
    signalStatusEl.textContent = data.signal || "Unavailable";
    setSignalClass(data.signal);
    symbolEl.textContent = data.symbol || "—";
    timeframeEl.textContent = data.timeframe || "—";
    timestampEl.textContent = data.timestamp
      ? new Date(data.timestamp).toLocaleString()
      : "—";
    priceEl.textContent = data.price != null ? Number(data.price).toFixed(2) : "—";
    smaShortEl.textContent = data.sma20 != null ? Number(data.sma20).toFixed(2) : "—";
    smaLongEl.textContent = data.sma50 != null ? Number(data.sma50).toFixed(2) : "—";
    rsiEl.textContent = data.rsi14 != null ? Number(data.rsi14).toFixed(2) : "—";
  };

  const renderEquityChart = (curve) => {
    const ctx = document.getElementById("equity-chart");
    const labels = curve.map((point) => new Date(point.timestamp).toLocaleString());
    const values = curve.map((point) => point.equity);

    if (!equityChart) {
      equityChart = new Chart(ctx, {
        type: "line",
        data: {
          labels,
          datasets: [
            {
              label: "Equity",
              data: values,
              borderColor: "#2563eb",
              backgroundColor: "rgba(37, 99, 235, 0.1)",
              tension: 0.3,
              pointRadius: 0,
              fill: true,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              ticks: { maxTicksLimit: 6 },
              grid: { display: false },
            },
            y: {
              ticks: { callback: (value) => formatCurrency(value) },
            },
          },
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (context) => formatCurrency(context.parsed.y),
              },
            },
          },
        },
      });
    } else {
      equityChart.data.labels = labels;
      equityChart.data.datasets[0].data = values;
      equityChart.update();
    }
  };

  const showError = (element, message) => {
    element.textContent = message;
    element.classList.remove("buy", "sell", "hold");
  };

  const fetchSignal = async () => {
    try {
      const response = await fetch("/api/signal/latest");
      if (!response.ok) {
        throw new Error(`Signal request failed (${response.status})`);
      }
      const data = await response.json();
      updateSignalCard(data);
      await fetchAiInsight();
    } catch (error) {
      showError(signalStatusEl, "Unable to load signal");
      console.error(error);
    }
  };

  const fetchAiInsight = async () => {
    try {
      aiBiasEl.textContent = "Loading AI insight…";
      aiBiasEl.dataset.bias = "";
      aiExplanationEl.textContent = "";
      const response = await fetch("/api/ai-insight");
      if (!response.ok) {
        throw new Error(`AI insight failed (${response.status})`);
      }
      const data = await response.json();
      aiBiasEl.textContent = `AI Bias: ${
        data.bias === "lean_buy"
          ? "Lean BUY"
          : data.bias === "lean_sell"
          ? "Lean SELL"
          : "Neutral"
      }`;
      aiBiasEl.dataset.bias = data.bias || "neutral";
      aiExplanationEl.textContent = data.explanation || "AI insight unavailable.";
    } catch (error) {
      aiBiasEl.textContent = "AI insight unavailable.";
      aiBiasEl.dataset.bias = "neutral";
      aiExplanationEl.textContent = "The advisory service is currently offline.";
      console.error(error);
    }
  };

  const handleSimulationSubmit = async (event) => {
    event.preventDefault();
    const formData = new FormData(simulationForm);
    const payload = {
      symbol: symbolEl.textContent && symbolEl.textContent !== "—" ? symbolEl.textContent : "XAUUSD",
      timeframe:
        timeframeEl.textContent && timeframeEl.textContent !== "—"
          ? timeframeEl.textContent
          : "60min",
      start_date: formData.get("start_date"),
      end_date: formData.get("end_date"),
      starting_balance: Number(formData.get("starting_balance")),
    };

    try {
      const response = await fetch("/api/simulation/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.error || "Simulation failed");
      }
      const data = await response.json();
      const summary = data.summary || {};
      simulationSummary.hidden = false;
      summaryFinal.textContent = formatCurrency(summary.final_balance);
      summaryDrawdown.textContent = formatPercent(summary.max_drawdown);
      summaryWinRate.textContent = formatPercent(summary.win_rate);
      summaryTrades.textContent = summary.num_trades ?? "—";

      if (Array.isArray(data.equity_curve) && data.equity_curve.length > 1) {
        chartCard.hidden = false;
        chartCard.style.height = "360px";
        renderEquityChart(data.equity_curve);
      }
    } catch (error) {
      console.error(error);
      simulationSummary.hidden = false;
      summaryFinal.textContent = "—";
      summaryDrawdown.textContent = "—";
      summaryWinRate.textContent = "—";
      summaryTrades.textContent = "—";
      chartCard.hidden = true;
    }
  };

  if (simulationForm) {
    simulationForm.addEventListener("submit", handleSimulationSubmit);
  }

  if (refreshSignalBtn) {
    refreshSignalBtn.addEventListener("click", (event) => {
      event.preventDefault();
      fetchSignal();
    });
  }

  if (refreshAiBtn) {
    refreshAiBtn.addEventListener("click", (event) => {
      event.preventDefault();
      fetchAiInsight();
    });
  }

  // Auto-fill default date range (last 30 days)
  const today = new Date();
  const start = new Date(today.getTime() - 29 * 24 * 60 * 60 * 1000);
  const toISODate = (date) => date.toISOString().split("T")[0];
  const startDateInput = document.getElementById("start-date");
  const endDateInput = document.getElementById("end-date");
  if (startDateInput && endDateInput) {
    startDateInput.value = toISODate(start);
    endDateInput.value = toISODate(today);
  }

  fetchSignal();
})();
