# Prediction Engine

Local prediction service. The only external inference API is **xAI**. No DigitalOcean deploy in this session (pending Luis approval).

## Status — 2026-09-27 16:15 EDT

- GitHub connector authenticated as `ABBYCRM`. Only this repo was touched. No DigitalOcean deploy (pending Luis approval).
- Version 0.24.0: analog `min_hits_in_query`; calibration `max_abs_error` from caller p,y only; MCP `calibration.max_ae`. Sheets still unwired. SMTP still dual-gated and not live.
- pytest must stay green.
- xAI only at api.x.ai when `XAI_API_KEY` is set.
