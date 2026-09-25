# Prediction Engine

Local prediction service. The only external inference API is **xAI**. No DigitalOcean deploy in this session (pending Luis approval).

## Status — 2026-09-25 00:00 EDT

- GitHub connector authenticated as `ABBYCRM`. Only this repo was touched. No DigitalOcean deploy (pending Luis approval).
- Version 0.4.0: analog retrieval, PI/SSDI house bridges, portable MMM contracts, Resend-shaped outbox, Chrome dump-dom scrape path, 21st-shaped chat UI.
- pytest expected green (`PYTHONPATH=src python3 -m pytest`).
- Ads playbook: 11 sourced facts with `as_of`. Portable contracts file has field names only — no invented CPL/ROAS.
- Predictions are labeled `kind=prediction`. Facts carry source URL + as_of.
