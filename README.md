# Prediction Engine

Local prediction service. The only external inference API is **xAI**. No DigitalOcean deploy in this session (pending Luis approval).

## Status — 2026-09-26 12:20 EDT

- GitHub connector authenticated as `ABBYCRM`. Only this repo was touched. No DigitalOcean deploy (pending Luis approval).
- Version 0.16.0: local calibration ledger (caller-supplied p/y only, Brier), local JSONL `ledger.append`, cadence `window_remaining_minutes` + 30-minute slice budget. Sheets still unwired. SMTP still dual-gated and not live.
- pytest must stay green.
- xAI only at api.x.ai when `XAI_API_KEY` is set.
