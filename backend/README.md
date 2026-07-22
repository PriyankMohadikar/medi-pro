# MediPrice Pro — Backend API

Production-ready FastAPI backend for the AI-powered Healthcare Pricing Optimization & Competitive Intelligence System.

## Quick Start

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

## Swagger Docs

Open [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API documentation.

## API Endpoints

All endpoints are served under the `/api` prefix.

| #  | Method | Endpoint                    | Description                          |
|----|--------|-----------------------------|--------------------------------------|
| 1  | GET    | `/api/tests`                | Return all tests                     |
| 2  | GET    | `/api/tests/{test_name}`    | Providers offering a specific test   |
| 3  | GET    | `/api/packages`             | Return all packages                  |
| 4  | GET    | `/api/packages/{pkg_name}`  | Providers offering a specific package|
| 5  | POST   | `/api/compare/tests`        | Compare test prices across providers |
| 6  | POST   | `/api/compare/packages`     | Compare package prices               |
| 7  | POST   | `/api/pricing/margin`       | Calculate margin & selling price     |
| 8  | POST   | `/api/custom-package`       | Build custom package with margin     |
| 9  | GET    | `/api/providers`            | Return all providers                 |
| 10 | GET    | `/api/analytics/market`     | Market analytics summary             |
| 11 | GET    | `/api/analytics/competitors`| Competitor analytics & rankings      |
| 12 | GET    | `/api/dashboard`            | Dashboard summary                    |
| 13 | GET    | `/api/stats`                | Frontend dashboard KPI aggregates    |
| -  | POST   | `/api/chat`                 | AI Chat (Ollama pending — Stage 3)   |
| -  | GET    | `/api/health`               | API health check                     |

## Architecture

```
backend/
├── app/
│   ├── api/            # API route handlers (thin controllers)
│   │   ├── tests.py        # APIs 1-2
│   │   ├── packages.py     # APIs 3-4
│   │   ├── comparison.py   # APIs 5-6
│   │   ├── pricing.py      # APIs 7-8
│   │   ├── providers.py    # API 9
│   │   ├── analytics.py    # APIs 10-11
│   │   ├── dashboard.py    # API 12
│   │   ├── stats.py        # API 13 (frontend KPIs)
│   │   └── chat.py         # AI Chat (placeholder)
│   ├── services/       # Business logic layer
│   ├── database/       # SQLAlchemy models & session management
│   ├── schemas/        # Pydantic validation schemas
│   ├── utils/          # Helper utilities
│   ├── config.py       # Environment & settings
│   └── main.py         # FastAPI application entry point
├── api_server.py       # [LEGACY] Old monolithic API — replaced by app/
├── main.py             # ETL pipeline entry point (still active)
├── .env                # PostgreSQL credentials
├── requirements.txt
└── README.md
```

## Environment Variables

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=healthcare_pricing
DB_USER=postgres
DB_PASSWORD=root
```

## Frontend Integration

The React frontend (Vite on port 3000) proxies `/api/*` requests to `http://localhost:8000`.
The frontend calls these specific endpoints:
- `GET /api/tests` → Individual test pricing data
- `GET /api/packages` → Package pricing data
- `GET /api/stats` → Dashboard KPI aggregates
- `GET /api/providers` → Provider list
- `GET /api/health` → Health check

## Stage 3 — Ollama AI Integration

The `services/chat_service.py` module exposes Python functions ready for Ollama tool-calling:
- `chat_compare_test_prices()`
- `chat_calculate_margin()`
- `chat_build_custom_package()`
- `chat_get_market_analytics()`
- `chat_get_provider_rankings()`

The `/api/chat` POST endpoint currently returns a placeholder response and will be wired to Ollama in Stage 3.
