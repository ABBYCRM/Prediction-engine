# WORKLOG

## 2026-09-27 16:00–16:30 EDT — cadence hour 16

- Gate: America/New_York hour 16 ∈ {0,4,8,12,16,20}. Worked.
- Touched only ABBYCRM/Prediction-engine. No DigitalOcean. No invented CPL/ROAS or other market numbers.
- v0.24.0: analog `hit_summary` adds `min_hits_in_query` (None when empty). Calibration `summary` adds `max_abs_error` = max |p−y| from caller p,y only. MCP `calibration.max_ae`. Sheets still unwired. SMTP still dual-gated and not live.
- xAI only at api.x.ai when XAI_API_KEY is set (unset this slice; no live LLM call).
- Next slice: live Sheets only after tokens + Luis sign-off; live SMTP only after dual-gate + explicit send test; no DO.


## 2026-09-27 12:01–12:31 EDT — cadence hour 12

- Gate: America/New_York hour 12 ∈ {0,4,8,12,16,20}. Worked.
- Touched only ABBYCRM/Prediction-engine. No DigitalOcean. No invented CPL/ROAS or other market numbers.
- v0.23.0: analog `hit_summary` adds `max_hits_in_query` (None when empty). Calibration `summary` adds `mean_abs_error` = mean |p−y| from caller p,y only. MCP `calibration.mae`. Sheets still unwired. SMTP still dual-gated and not live.
- xAI only at api.x.ai when XAI_API_KEY is set (unset this slice; no live LLM call).
- Next slice: live Sheets only after tokens + Luis sign-off; live SMTP only after dual-gate + explicit send test; no DO.


See git history for earlier cadence slices.
