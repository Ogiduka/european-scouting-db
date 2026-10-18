# European Scouting DB · mobile pilot

Mobile Safari / iPad dashboard based on the previously created V4 scouting workbook.

## Deploy without a PC

1. On iPhone/iPad Safari, create a GitHub account: https://github.com/signup .
2. Create a **private** repository, for example `european-scouting-db`.
3. In GitHub's repository, upload **the contents of this ZIP**, preserving `data/` and `.github/workflows/`. The web UI may not reliably upload nested directories from iOS; if that happens, use GitHub's browser editor or a GitHub-compatible iOS client to create paths, or upload through a browser with desktop-site mode. The repository root must include `streamlit_app.py` and `requirements.txt`.
4. Sign in at https://share.streamlit.io , press **Create app**, select repo and branch `main`, main file `streamlit_app.py`, then Deploy.
5. Open the generated `*.streamlit.app` URL in Safari, optionally Share > Add to Home Screen. Set private viewing in app sharing settings if needed; a private GitHub repo alone should not substitute for verifying app privacy.
6. At GitHub: **Actions** > **FEB daily first-page import** > **Run workflow**. Check job logs. Scheduled workflow runs daily (UTC) but GitHub can delay scheduled runs. If errors occur, nothing is updated.
7. If GitHub rejects writes, configure repository Actions permissions for read/write workflow token; keep access restricted. Do not enable automated fetching until permission and source terms are reviewed.

## Important limits

- Existing V4 player sample is not full Europe and contains incompletely verified age fields.
- FEB importer only attempts visible ranking first page. It is **unverified against live website structure** and may exit with `NO ROWS` (JavaScript or table layout changes); it does not automatically traverse pages and it cannot capture all players or roster-only entries.
- A reliable age≤34/PPG≥0/level1–4 filter requires matching birth dates, teams, leagues and game records; not falsely applied to missing values.
- Streamlit Community Cloud is a prototype deployment, not a guaranteed always-on production ingestion service. GitHub repo committed CSV files provide persistent snapshots when import succeeds.
- Always respect league website terms and rate limits. Do not bypass blocks or authentication.
