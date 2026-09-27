# Prediction Engine

Local prediction service. The only external inference API is **xAI**. No DigitalOcean deploy in this session (pending Luis approval).

## Status — 2026-09-26 20:20 EDT

- GitHub connector authenticated as `ABBYCRM`. Only this repo was touched. No DigitalOcean deploy (pending Luis approval).
- Version 0.18.0: expected calibration error (ECE) from caller-supplied p/y reliability buckets only; analog `unique_ids` in hit summaries; MCP `calibration.reliability`. Sheets still unwired. SMTP still dual-gated and not live.
- pytest must stay green.
- xAI only at api.x.ai when `XAI_API_KEY` is set.
