# Gold Signal Trading Bot

Prototype for a gold (XAUUSD) trading research platform with FastAPI backend and React dashboard.

## Project Structure

```
backend/
  app/
    main.py
    config.py
    models.py
    schemas.py
    services/
    routers/
  requirements.txt
  Dockerfile
frontend/
  src/
  package.json
  Dockerfile
```

## Getting Started

1. Ensure Docker and Docker Compose are installed.
2. From the repository root run:

```bash
docker-compose up --build
```

3. Access the frontend at http://localhost:5173 and backend docs at http://localhost:8000/docs.

The default strategy `gold_sma_rsi_v1` is seeded automatically on startup.

## Environment Variables

Configure backend settings via `.env` if desired:

```
LIVE_MODE=false
MT5_LOGIN=
MT5_PASSWORD=
MT5_SERVER=
```

Frontend can override the API base URL with `VITE_API_URL`.

## Future Work

- Plug in Exness MT5 broker via `ExnessMT5Broker`.
- Toggle live trading with `LIVE_MODE=true` once ready.
