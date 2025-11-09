# Trading Bot

This repository provides a minimal, fully-tested trading bot that implements a
moving average crossover strategy alongside an XAUUSD-focused SMA + RSI
strategy. It includes utilities for loading market prices, generating trading
signals, executing simulated trades, exposing a JSON API, and evaluating
performance. A Docker-based deployment workflow makes it possible to run the
bot with a single command.

## Project layout

```
.
├── data/                  # Sample OHLCV data
├── config/                # Persisted configuration written by the UI
├── trading_bot/           # Bot implementation modules
├── tests/                 # Automated unit tests (pytest)
├── main.py                # Command-line interface
├── Dockerfile             # Container definition for one-touch deployment
├── deploy.sh              # Helper script to build and run the container
└── Makefile               # Common development tasks
```

## Getting started

1. **Create a virtual environment and install dependencies**

   ```bash
   make install
   ```

2. **Run the automated test suite**

   ```bash
   make test
   ```

3. **Launch the configuration UI (optional)**

   ```bash
   make run-config-ui
   ```

   The command starts a local Flask application at http://127.0.0.1:8000 that
   surfaces a configuration screen. Use it to select a data vendor, capture API
   credentials, and toggle between backtest, paper, or live execution modes.
   Settings are saved to `config/config.json` and validated to ensure live
   trading requirements (API keys, account identifiers, and risk controls) are
   present before deployment.

4. **Execute the bot locally**

   ```bash
   make run
   ```

   The command prints a trade summary after running the moving average crossover
   strategy against the sample dataset. When a configuration file exists, the
   bot can be extended to read the saved settings for data fetching and trading
   controls.

## Gold SMA+RSI Strategy

The `gold_sma_rsi_v1` strategy evaluates gold (XAUUSD) price action using a
combination of simple moving averages and a relative strength index filter. For
each candle the strategy calculates:

* **SMA20 / SMA50** (configurable) – short- and long-term trend filters.
* **RSI14** (configurable period) – momentum filter ensuring trades occur during
  balanced conditions.

Signal rules (thresholds are configurable through `config/config.json`):

* **BUY** when price > SMA(short) and SMA(short) > SMA(long) and `rsi_buy_min`
  ≤ RSI ≤ `rsi_buy_max`.
* **SELL** when price < SMA(short) and SMA(short) < SMA(long) and RSI ≥
  `rsi_sell_min`.
* Otherwise **HOLD**.

Each evaluation produces a structured payload containing the timestamp, price,
indicator values, and recommended action.

## API Endpoints

The existing Flask configuration UI now also exposes JSON endpoints suitable
for powering dashboards or downstream services. Start the app via `make
run-config-ui` and call the following routes:

* `GET /api/signal/latest` – returns the most recent gold strategy signal using
  the symbol, interval, and strategy parameters stored in `config/config.json`.
* `POST /api/simulation/run` – accepts `{symbol, timeframe, start_date,
  end_date, starting_balance}` and runs a backtest with the configured gold
  strategy parameters, returning summary statistics, the equity and drawdown
  curves, and a list of executed trades.

Cross-origin requests from any `http://localhost:*` origin are permitted so a
front-end application can consume these endpoints during development.

## One-touch deployment

The provided `deploy.sh` script builds the Docker image and runs it in a single
step:

```bash
./deploy.sh
```

Pass an optional image name to tag the image differently:

```bash
./deploy.sh my-custom-image
```

The container executes the bot against the bundled sample data by default.
Modify the `CMD` in the `Dockerfile` or override the command at runtime to point
at different datasets or strategy parameters.

## Adding new data or strategies

* Place additional CSV files (with `timestamp, open, high, low, close, volume`)
  inside the `data/` directory or supply an absolute path when running
  `main.py`.
* Implement new strategies in `trading_bot/strategy.py` (or additional modules)
  and update `main.py` to expose new options.
* Extend the test suite under `tests/` to cover any new behaviour.

## License

This project is licensed under the terms of the MIT License. See `LICENSE` for
full details.
