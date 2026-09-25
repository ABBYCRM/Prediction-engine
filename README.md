# Prediction Engine

Local prediction service. The only external inference API is **xAI**. No DigitalOcean deploy in this session (pending Luis approval).

## Status — 2026-09-25 08:02 EDT

- GitHub connector authenticated as `ABBYCRM`. Only this repo was touched. No DigitalOcean deploy (pending Luis approval).
- Version 0.8.0: Sheets write gated on Google OAuth + `GOOGLE_SHEETS_SPREADSHEET_ID`. Without tokens, target=`sheets` is refused. Local JSONL writeback works.
- GET `/health` reports connector presence flags (no token leak). POST `/writeback` + MCP `sheets.write`.
- Default predict still records allowlisted URL/host with `fetched: false`.
- pytest expected green (`PYTHONPATH=src python3 -m pytest tests/`).
- Ads playbook: 11 sourced facts with `as_of`. Predictions labeled `kind=prediction`.
- xAI only at api.x.ai when `XAI_API_KEY` is set.
