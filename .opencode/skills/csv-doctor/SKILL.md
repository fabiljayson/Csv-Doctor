---
name: csv-doctor
description: CSV Data Quality Doctor work (Streamlit + Pandas + Plotly data-quality analysis tool). Use for ANY task under /home/fabiljayson/Projects/Csv-Doctor — covers the venv/streamlit启动 commands and the non-destructive cleaning contract.
---

# CSV Data Quality Doctor

Modular data-quality tool: profiling, missing-value/duplicate/anomaly detection (IQR + Z-score, explainable), format consistency checks, configurable validation rules, transparent 0–100 quality scoring, and safe cleaning.

## Contract: cleaning is non-destructive

Every cleaning operation keeps the original data intact with **preview → confirmation → history trace**. Never add a destructive shortcut. Quality scoring stays transparent (completeness, uniqueness, validity, consistency) — no unexplained magic numbers.

## Run

Streamlit is **not global** — it lives in the project's `.venv`:

```bash
cd Csv-Doctor && source .venv/bin/activate && streamlit run app.py
```

(If the venv is missing: `uv sync` / `pip install -r requirements.txt` first.)

## Layout

`app.py` at root + logic in `src/` (src layout). Robust CSV loading matters: multiple encodings, delimiters and parsing edge cases are a feature, not an afterthought.
