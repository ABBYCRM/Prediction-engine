# Prediction Engine

Local prediction service. The only external inference API is **xAI**. No DigitalOcean deploy in this session (pending Luis approval).

## Status — 2026-09-26 04:20 EDT

- GitHub connector authenticated as `ABBYCRM`. Only this repo was touched. No DigitalOcean deploy (pending Luis approval).
- Version 0.14.0: SMTP dual-gate (`SMTP_HOST`+`SMTP_FROM` **and** `SMTP_SEND_ENABLED`). GET `/mailer`, MCP `mailer.status`. Sheets `values.append` contract + `/sheets/preview` + MCP `sheets.preview` — field names only, `wired: false`.
- GET `/ledger` + MCP `ledger.read` still local JSONL (`remote: false`). Live Sheets write still refused even when OAuth is present.
- Default predict still records allowlisted URL/host with `fetched: false`.
- pytest expected green (`PYTHONPATH=src python3 -m pytest tests/`).
- Ads playbook: 11 sourced facts. Predictions labeled `kind=prediction`.
- xAI only at api.x.ai when `XAI_API_KEY` is set.
