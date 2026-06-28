# Changelog

All notable changes to this portfolio will be documented in this file.

---

## v1.1.0 — Polish Round (2026-06-28)

### Root README
- **Changed** "AI-audited code" → "Code-audited: 47+ automated checks" (de-AI branding)
- **Changed** "Fast first response" → "Same-day response, first milestone free if missed"
- **Changed** Author credit to `Ck.epsilon` only (removed AI co-author from public READMEs)

### ai-workbench
- **Added** Architecture section to Chinese README (FN-2)
- **Moved** System Requirements to end of document (unified EN/CN order)
- **Changed** "30+ tokens/sec" → "sub-second first-token latency, steady streaming"
- **Changed** GPU description to include CPU-only caveat
- **Added** Screenshot placeholder

### scraper-dashboard
- **Added** `docker-compose.yml` + `backend/Dockerfile`
- **Added** Performance footnote (*per-task limits, throughput caveat)
- **Added** Browser row to Supported Environment tables (EN + CN)
- **Added** Ethics disclaimer to Chinese section

### api-starter
- **Changed** "8 endpoints in <300 LOC" → "8 endpoints, minimal boilerplate"
- **Added** `.env.example` comment for SQLite quick-start clarity

### admin-dashboard
- **Added** "See package.json for dependency details"
- **Added** Dark mode demo placeholder

### scraper-template
- **Added** `pandas>=1.5.0` to requirements.txt
- **Added** HackerNews output example (EN + CN)
- **Added** Anti-detection disclaimer about advanced challenges
- **Added** Browser row to Supported Environment tables

### Cross-Project
- **Added** `.github/workflows/ci.yml` — pytest for scraper-dashboard, syntax/lint for others
- **Added** `CHANGELOG.md` (this file)
- **Changed** All 6 README author lines: `Ck.epsilon & Chaos` → `Ck.epsilon`

---

## v1.0.0 — Initial Release

- 5 portfolio projects with bilingual READMEs
- Root README with live previews via htmlpreview.github.io
- MIT License
