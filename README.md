# Trading Bot

This repository provides a minimal, fully-tested trading bot that implements a
moving average crossover strategy. It includes utilities for loading market
prices, generating trading signals, executing simulated trades, and evaluating
performance. A Docker-based deployment workflow makes it possible to run the
bot with a single command.

## Project layout

```
.
├── data/                  # Sample OHLCV data
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

3. **Execute the bot locally**

   ```bash
   make run
   ```

   The command prints a trade summary after running the moving average crossover
   strategy against the sample dataset.

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
