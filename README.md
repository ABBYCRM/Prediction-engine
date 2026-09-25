# Prediction Engine

Local prediction service. The only external inference API is **xAI**. No DigitalOcean deploy in this session (pending Luis approval).

## Status — 2026-09-25 02:15 EDT

- GitHub connector authenticated as `ABBYCRM`. Only this repo was touched. No DigitalOcean deploy (pending Luis approval).
- Version 0.6.0: live_runs research files, CRM/Sheets writeback schema, Google/Meta OAuth refuse-without-token, default model grok-4.7.
- pytest expected green (`PYTHONPATH=src python3 -m pytest tests/`).
- Ads playbook: 11 sourced facts with `as_of`. Live runs keep PI and SSDI analog sets apart.
- Predictions are labeled `kind=prediction`. Facts carry source URL + as_of.
- xAI only at api.x.ai when `XAI_API_KEY` is set. Key was unset this session.
