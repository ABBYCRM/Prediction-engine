# Prediction Engine

Local prediction service. The only external inference API is **xAI**. No DigitalOcean deploy in this session (pending Luis approval).

## Status — 2026-09-25 16:01 EDT

- GitHub connector authenticated as `ABBYCRM`. Only this repo was touched. No DigitalOcean deploy (pending Luis approval).
- Version 0.10.0: GET `/publishers` + MCP `publishers.list` expose allowlisted hosts only (`live_fetch: false`). Analog log and GET `/analogs` accept an optional `house` filter.
- GET `/ledger` + MCP `ledger.read` still expose the local writeback JSONL only (`remote: false`). Sheets still refused without OAuth + spreadsheet id; live Sheets client not wired.
- Default predict still records allowlisted URL/host with `fetched: false`.
- pytest expected green (`PYTHONPATH=src python3 -m pytest tests/`).
- Ads playbook: 11 sourced facts. Predictions labeled `kind=prediction`.
- xAI only at api.x.ai when `XAI_API_KEY` is set.
