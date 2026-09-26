# WORKLOG

See git history for slices through 2026-09-25 16:31 EDT.

## 2026-09-26 12:02–12:32 EDT — cadence hour 12

- Gate: America/New_York hour 12 ∈ {0,4,8,12,16,20}. Worked.
- Touched only ABBYCRM/Prediction-engine. No DigitalOcean. No invented CPL/ROAS or other market numbers.
- v0.16.0: `calibration` records caller-supplied p∈[0,1], y∈{0,1} and Brier only; GET/POST `/calibration`; MCP `calibration.record` / `calibration.summary`. Local `ledger.append` JSONL (remote=false). Cadence reports `window_remaining_minutes` and 30-minute slice budget. Restored outbox draft `scheduled_at` + `headers` so v0.15 tests stay green.
- xAI only at api.x.ai when XAI_API_KEY is set (unset this slice; no live LLM call).
- Next slice: live Sheets only after tokens + Luis sign-off; live SMTP only after dual-gate + explicit send test; no DO.


## 2026-09-26 08:08–08:38 EDT — cadence hour 8

- Gate: last slice ended 2026-09-26 04:33 EDT; now 08:08 EDT (≥3.5h). Hour 8 ∈ {0,4,8,12,16,20}. Worked.
- Touched only ABBYCRM/Prediction-engine. No DigitalOcean. Luis has not approved deploy in this human message.
- Portable contracts added from public docs only (field names + URL + as_of): Meridian HoldoutSpec/GeoHoldoutSpec (`holdout`, `holdout_id`, `geos`, `date_ranges`), Adobe Mix conversion table columns and global harmonized fields, Performance Planner view columns Planned/Existing/Diff, Keen Planning Module metadata axes. No invented CPL/ROAS numbers.
- Analog: exact-id and URL-token boosts. Playbook match includes source URL. House 10→0 still strips foreign keys only; 0→1 still seeds an empty per-house ledger. Resend outbox keeps `scheduled_at` + `headers` on drafts. Chat UI: live-scrape checkbox, house-bridge POST `/house/bridge`, shell/aside styles.
- Version 0.15.0. pytest: 54 passed.
- Next slice: live Sheets client only after tokens + Luis sign-off; live SMTP socket only after dual-gate and explicit send test; no DO.
- Blockers: native GitHub write may 403 (Cursor bridge fallback); XAI_API_KEY unset; Google OAuth / spreadsheet id unset.
