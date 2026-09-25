# WORKLOG

## 2026-09-24 16:09–16:40 EDT — cadence hour 16

- Gate: America/New_York hour 16 ∈ {0,4,8,12,16,20}. Worked.
- Touched only ABBYCRM/Prediction-engine. No DigitalOcean.

## 2026-09-25 12:06–12:36 EDT — cadence hour 12

- Gate: America/New_York hour 12 ∈ {0,4,8,12,16,20}. Worked.
- Touched only ABBYCRM/Prediction-engine. No DigitalOcean.
- House-aware `predict(house=)` rejects unknown houses; accepted house is recorded on analog hits and the result.
- Local ledger reader (`ledger.py`): GET `/ledger` and MCP `ledger.read` (extra-key rejection). Filter by house. `remote_writes` stays 0.
- Frontend composer now sends the house selector.
- Version 0.9.0. pytest: 32 passed (`PYTHONPATH=src python3 -m pytest tests/`).
- No invented CTR/CPC/%. No live xAI call (`XAI_API_KEY` unset). No OAuth tokens present.
- Cursor bridge commits `cc6ca7a`, `95f240f`, `403e677`, `937c69d`, `2c9940a`, `f4708b9` plus this commit.
- Next slice: live Sheets client only after Luis provides tokens; keep SMTP dual-gate; no DO.
