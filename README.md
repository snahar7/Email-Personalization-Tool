# Email Personalization Tool

AI-written sales emails personalized from prospect data, company research and product-usage metrics, with templates, sending and tracking.

**Why:** reps spend hours personalizing outreach. This hands the first draft to an agent.

![Screenshot](docs/screenshot.png) <!-- TODO: add screenshot/GIF -->

## Features
- GPT-4 personalization from prospect + company data
- Prospect management (CSV sample included), email templates, analytics view
- SMTP sending
- FastAPI REST API + React/TypeScript dashboard

## Tech stack
Python, FastAPI, SQLAlchemy (SQLite), Pydantic, OpenAI · React + TypeScript (CRA/webpack) · GitHub Actions (static deploy)

## Setup
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload        # http://localhost:8000
cd frontend && npm install && npm start   # http://localhost:3000
```

## Environment variables
`OPENAI_API_KEY`, `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SECRET_KEY`, `DATABASE_URL`

## API
`GET /`, `GET /health`, `POST /api/prospects/`, `GET /api/prospects/{id}`, `GET /api/prospects/`

## License
MIT
