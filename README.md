# Prediction Engine

Local prediction service. The only external inference API is **xAI**. No DigitalOcean deploy in this session (pending Luis approval).

## Status — 2026-09-26 08:20 EDT

- GitHub connector authenticated as `ABBYCRM`. Only this repo was touched. No DigitalOcean deploy (pending Luis approval).
- Version 0.15.0: cadence `next_window` + GET `/cadence` + MCP `cadence.status`. Mailer envelope preview (`live_smtp: false`) via MCP `mailer.preview`. GET `/xai` + MCP `xai.guard` pin host `api.x.ai` and never emit the key.
- SMTP dual-gate unchanged. Sheets client still unwired (`wired: false`). Ledger still local JSONL.
- pytest: 55 passed.
- xAI only at api.x.ai when `XAI_API_KEY` is set.
