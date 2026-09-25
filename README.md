# Prediction Engine

Local prediction service. The only external inference API is **xAI**. No DigitalOcean deploy in this session (pending Luis approval).

## Status — 2026-09-25 04:04 EDT

- GitHub connector authenticated as `ABBYCRM`. Only this repo was touched. No DigitalOcean deploy (pending Luis approval).
- Version 0.7.0: optional `live_scrape` on predict (default off), GET `/analogs`, MCP `analog.log`.
- Default predict still records allowlisted URL/host with `fetched: false`.
- pytest expected green (`PYTHONPATH=src python3 -m pytest tests/`).
- Ads playbook: 11 sourced facts with `as_of`. Predictions labeled `kind=prediction`.
- xAI only at api.x.ai when `XAI_API_KEY` is set.
