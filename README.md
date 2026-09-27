# Prediction Engine

Local prediction service. The only external inference API is **xAI**. No DigitalOcean deploy in this session (pending Luis approval).

## Status — 2026-09-27 04:20 EDT

- GitHub connector authenticated as `ABBYCRM`. Only this repo was touched. No DigitalOcean deploy (pending Luis approval).
- Version 0.21.0: MCP `research.list` / `research.sources` (public URLs only, no fetch on sources); analog `first_ts`; MCP `calibration.brier`. Sheets still unwired. SMTP still dual-gated and not live.
- pytest must stay green.
- xAI only at api.x.ai when `XAI_API_KEY` is set.
