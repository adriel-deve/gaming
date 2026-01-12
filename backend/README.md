# Backend pipeline (skeleton)

This folder contains a simple pipeline to collect, normalize, store, and serve
game price data. It uses only Python standard library so you can plug in a real
data provider later.

## How it works
1) providers/* -> returns raw items
2) pipeline/collect.py -> writes data/raw/latest.json
3) pipeline/normalize.py -> writes data/normalized/latest.json
4) pipeline/store.py -> writes data/store/prices.json and history.json
5) api/server.py -> serves data from data/store

## Quick start
python backend/pipeline/run_pipeline.py
python backend/api/server.py --port 9000

## API endpoints
- GET /api/health
- GET /api/offers?store=&region=&platform=&on_sale=1
- GET /api/games
- GET /api/prices?game_id=...

## Scheduler
python backend/scheduler.py --once
python backend/scheduler.py

## Provider swap
Replace backend/providers/demo_provider.py with a provider that pulls data
from a licensed feed or a partner API. Keep the output shape the same.
