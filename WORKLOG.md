# WORKLOG

## 2026-09-24 16:09–16:40 EDT — cadence hour 16

- Gate: America/New_York hour 16 ∈ {0,4,8,12,16,20}. Worked.
- Touched only ABBYCRM/Prediction-engine. No DigitalOcean.
- Repo was incomplete vs README. Restored missing engine surface.
- Added: config (api.x.ai host lock), xAI client (no call without XAI_API_KEY), SSRF scraper, HTML snapshotter, SMTP-gated mailer, allowlisted MCP gateway, sourced 11-fact ads playbook, engine, stdlib HTTP API, frontend CSS/JS, tests.
- Playbook claims paraphrased from Google Ads Policy Help and Meta Transparency Center URLs only. No CTR/CPC/% invented.
- pytest: 9 passed (`PYTHONPATH=src python3 -m pytest`).
- Push: native GitHub connector returned 403 on contents write; files pushed via Cursor user-Github bridge.
- xAI: only https://api.x.ai when XAI_API_KEY is set. Key was not set this session; no live inference call.

## 2026-09-24 20:00–20:30 EDT — cadence hour 20

- Gate: America/New_York hour 20 ∈ {0,4,8,12,16,20}. Worked.
- Touched only ABBYCRM/Prediction-engine. No DigitalOcean.
- Added `cadence.py` (fixed hours, NY tz) and surfaced status on GET `/health` with version, xai_available (no key leak), playbook count, MCP tool list.
- Added GET `/tools`, MCP tool `engine.predict` (same extra-key rejection as other tools).
- Engine empty-query path returns `query_required` without inventing facts or calling xAI.
- Frontend health pill shows xai-on/off.
- Version 0.3.0. pytest: 12 passed (`PYTHONPATH=src python3 -m pytest`).
- No invented CTR/CPC/%. No live xAI call (`XAI_API_KEY` unset).
- Push: native GitHub `push_files` 403; Cursor user-Github bridge commits `4c1681d`, `0c4fb6b`, `59cafee`.

## 2026-09-25 00:00–00:30 EDT — cadence hour 0

- Gate: last slice ended 2026-09-24 20:30 EDT; now 00:00 EDT (≥3.5h). Hour 0 ∈ {0,4,8,12,16,20}. Worked.
- Touched only ABBYCRM/Prediction-engine. No DigitalOcean (Luis has not approved deploy in this message).
- Analog retrieval (`analog.py`) over playbook + portable contracts.
- House isolation (`houses.py`) 10→0 / 0→1; intake MCP tools reject mixed PI/SSDI keys.
- Sourced playbook facts now carry `as_of`. Added `data/mmm_contracts.json` field contracts from Meridian, Robyn, Adobe Mix Modeler scenario planner, Google Performance Planner / Keyword Forecast docs. No invented CPL/ROAS.
- Local Chrome scrape path: `browser.dump_dom` + `scraper.scrape_public` (SSRF first; falls back to httpx + HTML snapshot if Chrome missing).
- Resend-shaped outbox (`outbox.py`) still SMTP-gated.
- Frontend: 21st-shaped sidebar console, house selector, contracts button; answers prefixed `[prediction]`.
- Version 0.4.0. pytest: 16 passed (`PYTHONPATH=src python3 -m pytest`).
- No live xAI call (`XAI_API_KEY` unset).
- Next slice: wire scrape into predict only for allowlisted publisher URLs; persist analog hits; optional Resend API key still must not bypass SMTP gate unless Luis sets both.
- Blockers: native GitHub write may 403 (use Cursor bridge); Chrome binary may be absent in sandbox; no DO deploy.

## 2026-09-25 00:08–00:30 EDT — cadence hour 0 (continue)

- Gate still hour 0 America/New_York. Touched only ABBYCRM/Prediction-engine. No DigitalOcean.
- Implemented next-slice items: publisher allowlist (`publishers.py`) from playbook hosts + floor `support.google.com` / `transparency.meta.com`.
- `scraper.scrape_public` now SSRF then allowlist then snapshot. Default `predict` records allowlisted URL/host without live fetch (`fetched: false`).
- Analog hits persist to `data/analog_hits.jsonl` (gitignored); ids/scores only.
- `RESEND_API_KEY` cannot bypass SMTP_HOST+SMTP_FROM.
- Version 0.5.0. pytest: 17 passed (`PYTHONPATH=src python3 -m pytest`).
- No invented CTR/CPC/%. No live xAI call (`XAI_API_KEY` unset).
- Next slice: optional live scrape behind explicit flag; expose analog log on GET; keep SMTP dual-gate.

## 2026-09-25 02:15–02:45 EDT — continue e2e (this session)

- Local tree `/home/workdir/Prediction-engine` was empty at start; cloned `ABBYCRM/Prediction-engine` (repo exists, push permission true).
- pytest before change: 17 passed. After change: 22 passed (`PYTHONPATH=src python3 -m pytest tests/`).
- Default xAI model is `grok-4.7` on `https://api.x.ai`. `XAI_API_KEY` unset; no live inference. Client now accepts optional `web_search` / `x_search` tool payload when a key exists.
- Live cited research written under `data/live_runs/` as four house-isolated JSON files (pi policy, pi keyword, ssdi policy, ssdi keyword). Official Google/Meta/SSA URLs used as facts with `as_of`. Agency CPC/volume tables discarded. Predictions labeled `prediction`.
- Added `research.py` writer (rejects %, CPC, CTR, CPL, ROAS in claims), `writeback.py` + `data/writeback_schema.json`, `oauth.py` Google Ads / Meta gates that raise unless real env tokens exist. No OAuth tokens present; connectors not called.
- Version 0.6.0.
- Next still: live scrape flag; Sheets write only after Google OAuth; no DigitalOcean.
- Blockers: XAI_API_KEY unset; Google/Meta OAuth unset; no DO deploy.
- Push: native `github___push_files` 403 again; Cursor user-Github bridge commits `9284f86`, `27f03e0`, `597c0c0`, `be74010`, `5efd622`, `783129c` plus this commit.
