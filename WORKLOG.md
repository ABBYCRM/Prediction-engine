# WORKLOG

See git history for slices through 2026-09-25 16:31 EDT.

## 2026-09-26 04:03–04:33 EDT — cadence hour 4

- Gate: last slice ended 2026-09-26 00:35 EDT; now 04:03 EDT (≥3.5h). Hour 4 ∈ {0,4,8,12,16,20}. Worked.
- Touched only ABBYCRM/Prediction-engine. No DigitalOcean. No invented CPL/ROAS.
- SMTP dual-gate: HOST+FROM is gate A; SMTP_SEND_ENABLED is gate B. Resend key still cannot bypass either gate. Mailer.send still does not open a live SMTP socket (`live_smtp: false`).
- Sheets live client remains unwired. Added public values.append field-name contract + preview route/MCP tool. Tokens still required before any future remote write.
- Version 0.14.0. pytest: 50 passed.
- Next slice: live Sheets client only after tokens + Luis sign-off; live SMTP socket only after dual-gate and explicit send test; no DO.
- Blockers: native GitHub write 403 (Cursor bridge used); XAI_API_KEY unset; Google OAuth / spreadsheet id unset.

## 2026-09-26 00:05–00:35 EDT — cadence hour 0

- Gate: last slice ended 2026-09-25 20:35 EDT; now 00:05 EDT (≥3.5h). Hour 0 ∈ {0,4,8,12,16,20}. Worked.
- Touched only ABBYCRM/Prediction-engine. No DigitalOcean (Luis has not approved deploy in this human message).
- Portable contracts added from public docs only (field names + URL + as_of): Robyn calibration_input columns, Reach Planner axes, CampaignToForecast fields, Adobe Mix goal-plan setup names, Conversion Lift holdout power axes. No invented CPL/ROAS numbers.
- Analog: title/claim/product boosts + trigrams. House 10→0 strips foreign keys; 0→1 seeds empty per-house ledger. Playbook facts inherit pack as_of. Local Chrome --dump-dom when binary present; otherwise httpx snapshot. Resend outbox cc/bcc/reply_to/tags + draft list. Chat UI: live-scrape checkbox, house-bridge button, shell layout.
- Version 0.13.0. pytest: 45 passed.
- Next slice: live Sheets only after tokens; SMTP dual-gate send path; no DO.
- Blockers: native GitHub connector needs re-auth; deploy blocked pending Luis.

## 2026-09-25 20:05–20:35 EDT — cadence hour 20

- Gate: last slice ended 2026-09-25 16:31 EDT; now 20:05 EDT (≥3.5h). Hour 20 ∈ {0,4,8,12,16,20}. Worked.
- Touched only ABBYCRM/Prediction-engine. No DigitalOcean.
- Portable GeoX/Robyn/Meridian ModelSpec contracts only (field names + URLs + as_of). No CPL/ROAS invented.
- Analog bigrams. GET /contracts. Analogs + Publishers buttons.
- Version 0.12.0. pytest: 39 passed.
- Cursor bridge commits ec4ecf6, b9307a8, e3eea39, a2fd92f, c338d76 plus this commit.
- Next slice: live Sheets only after tokens; SMTP dual-gate; no DO.
