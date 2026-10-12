# Email Personalization Tool

[![CI](https://github.com/snahar7/Email-Personalization-Tool/actions/workflows/ci.yml/badge.svg)](https://github.com/snahar7/Email-Personalization-Tool/actions/workflows/ci.yml)

Load a list of prospects and an AI agent drafts a personalized sales email for each one, using their role, company research, and any product-usage data you pass in. You can then send it over SMTP.

**Why:** reps spend hours personalizing outreach. This hands the first draft to an agent.

![Screenshot](docs/screenshot.png) <!-- TODO: add screenshot/GIF -->

## Try it in one command
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python scripts/demo.py --mock      # no API key: imports sample_prospects.csv and drafts mock emails
python scripts/demo.py             # real drafts; needs OPENAI_API_KEY in .env or your shell
```
The demo uses a throwaway `demo.db`.

## Features
- CSV import of prospects and companies (`name,email,title,company,industry,website,linkedin,company_description`), skipping duplicate emails
- AI-drafted emails with the OpenAI SDK (default `gpt-4o-mini`; set `OPENAI_MODEL` to change it), optionally based on a saved template plus extra context
- Sending over SMTP (STARTTLS), which marks the prospect as contacted
- Companies, prospects, templates and engagement-metrics API
- React + TypeScript dashboard

## Tech stack
Python 3.11–3.13, FastAPI, SQLAlchemy 2, Pydantic 2, OpenAI SDK v1 · React + TypeScript (Create React App) · pytest · GitHub Actions

## Run the app
```bash
cp .env.example .env                  # add OPENAI_API_KEY (and SMTP_* to send)
uvicorn app.main:app --reload         # API on http://localhost:8000 (docs at /docs)

cd frontend
cp .env.example .env                  # REACT_APP_API_URL, defaults to http://localhost:8000/api
npm install && npm start              # http://localhost:3000
```

## Environment variables
| Variable | Required | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | to generate emails | OpenAI key |
| `OPENAI_MODEL` | no | defaults to `gpt-4o-mini` |
| `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD` | to send emails | SMTP with STARTTLS (for Gmail, use an app password) |
| `SMTP_FROM` | no | defaults to `SMTP_USERNAME` |
| `DATABASE_URL` | no | any SQLAlchemy URL; defaults to `sqlite:///./app.db` |
| `REACT_APP_API_URL` | no (frontend) | backend base URL |

If a required key is missing, the endpoint returns `503` with a message naming it.

## API
| Method | Path | |
|---|---|---|
| GET | `/health` | health check |
| POST/GET | `/api/companies/` · GET/PUT `/api/companies/{id}` | companies |
| POST | `/api/companies/upload-csv` | import prospects CSV |
| POST/GET | `/api/prospects/` · GET `/api/prospects/{id}` | prospects |
| POST | `/api/prospects/{id}/generate-email` | body `{"template_id"?, "additional_context"?}` → `{subject, body, model}` |
| POST | `/api/prospects/{id}/send-email` | body `{"subject", "body", "template_id"?}` |
| POST/GET | `/api/templates/` | email templates |
| POST | `/api/engagements/` · GET `/api/engagements/metrics/` · GET `/api/prospects/{id}/engagement/` | engagement tracking |

## Tests
```bash
pip install -r requirements-dev.txt
pytest -q
```
OpenAI and SMTP are mocked, so the tests need no keys.

## License
MIT
