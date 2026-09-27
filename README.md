# Prediction Engine

Local prediction service. The only external inference API is **xAI**. No DigitalOcean deploy in this session (pending Luis approval).

## Status — 2026-09-27 00:20 EDT

- GitHub connector authenticated as `ABBYCRM`. Only this repo was touched. No DigitalOcean deploy (pending Luis approval).
- Version 0.19.0: binary log-loss (`mean_log_loss`) from caller-supplied p/y only; analog `last_ts` in hit summaries; MCP `calibration.log_loss`. Sheets still unwired. SMTP still dual-gated and not live.
- pytest must stay green.
- xAI only at api.x.ai when `XAI_API_KEY` is set.
