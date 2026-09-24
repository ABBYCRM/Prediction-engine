# Prediction Engine

Local prediction service. The only external inference API is **xAI**. No DigitalOcean deploy in this session (pending Luis approval).

## Status — 2026-09-24 12:03 EDT

- GitHub connector authenticated as `ABBYCRM`. Repo created and pushed via connectors.
- Only this repo was touched. No DigitalOcean deploy (pending Luis approval).
- pytest: 9 passed (`PYTHONPATH=src python3 -m pytest`).
- Ads playbook: 11 sourced facts (Google Ads Policy Help, Google Ads blog 2026-07-09, Meta Transparency Center, Audience Network). No invented metrics.
- Hardening: scraper SSRF, mailer refuses send without SMTP_HOST/SMTP_FROM, MCP rejects unknown tools and extra keys.
- Frontend chat: transcript, health pill, Enter-to-send, playbook index.

## Run

```bash
cd Prediction-engine
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pytest
XAI_API_KEY=... python -m prediction_engine.api
```

Env: `XAI_API_KEY`, optional `XAI_BASE_URL` (default `https://api.x.ai/v1`), `XAI_MODEL` (default `grok-4`), `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`.

## Layout

- `src/prediction_engine/` — config, xAI client, scraper, browser snapshotter, mailer, MCP gateway, ads playbook, engine, HTTP API
- `data/ads_playbook.json` — sourced facts only
- `frontend/` — chat UI
- `tests/`
