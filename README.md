# CSV Data Quality Doctor

A comprehensive, modular data quality analysis and cleaning tool for CSV datasets. Built with Python, Pandas, Streamlit, and Plotly, this application helps users detect, investigate, explain, and optionally correct data quality issues.

## Overview

CSV Data Quality Doctor is a web-based application that provides end-to-end data quality diagnostics including missing values, duplicates, numerical anomalies, format inconsistencies, validation rules, quality scoring, and safe data cleaning with full traceability.

## Features

- **Robust CSV Loading**: Handles various encodings, delimiters, and parsing edge cases
- **Data Profiling**: Comprehensive dataset and column-level statistics
- **Missing Value Detection**: Identifies NaN/None and configurable missing token strings
- **Duplicate Detection**: Finds exact duplicates and key-based duplicates
- **Anomaly Detection**: IQR and Z-score based outlier detection with explainable results
- **Format Consistency Checks**: Detects whitespace, case inconsistencies, mixed types, date/number formatting issues
- **Data Validation**: Configurable rules (required, min/max, categorical, length, pattern, uniqueness)
- **Quality Scoring**: Transparent 0-100 scoring across completeness, uniqueness, validity, and consistency
- **Safe Data Cleaning**: Non-destructive operations with preview, confirmation, and history tracking
- **Export Capabilities**: Download cleaned CSV, JSON quality reports, and cleaning logs
- **Interactive Dashboard**: Clean Streamlit interface with multiple analysis pages

## Technology Stack

- Python 3.11+
- Pandas 2.x
- NumPy
- Streamlit
- Plotly
- Pytest
- Ruff

## Installation

### Prerequisites

- Python 3.11 or newer
- pip

### Setup

#### Linux/macOS

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Usage

### Launch the Application

```bash
python -m streamlit run app.py
```

The application will open in your default web browser at http://localhost:8501.

### Using the Sample Dataset

The project includes a synthetic messy dataset at `data/sample_messy_data.csv` with intentional data quality issues. You can:
1. Download it from the sidebar
2. Load it directly using the "Load sample dataset" button

## Testing

Run the test suite:

```bash
python -m pytest -q
```

## Linting and Formatting

Check code quality:

```bash
python -m ruff check .
```

Format code:

```bash
python -m ruff format .
```

## Project Structure

```
Csv-Doctor/
├── app.py                 # Streamlit application
├── requirements.txt       # Dependencies
├── README.md             # This file
├── LICENSE               # MIT License
├── .gitignore            # Git ignore rules
├── .streamlit/           # Streamlit config
│   └── config.toml
├── data/                 # Sample datasets
│   └── sample_messy_data.csv
├── src/                  # Core modules
│   ├── __init__.py
│   ├── config.py
│   ├── exceptions.py
│   ├── file_loader.py
│   ├── profiler.py
│   ├── quality_score.py
│   ├── missing_values.py
│   ├── duplicates.py
│   ├── anomalies.py
│   ├── format_checks.py
│   ├── validation.py
│   ├── cleaning.py
│   ├── reporting.py
│   └── utils.py
├── tests/                # Unit tests
│   ├── conftest.py
│   ├── test_*.py
└── docs/                 # Documentation
    ├── ARCHITECTURE.md
    ├── DATA_QUALITY_METHODOLOGY.md
    └── SCREENSHOTS.md
```

## Data Quality Methodology

The application evaluates data quality across four dimensions:
- **Completeness** (35%): Measures missing values
- **Uniqueness** (25%): Detects duplicate records
- **Validity** (25%): Assesses conformance to validation rules
- **Consistency** (15%): Identifies format and type inconsistencies

Outlier detection uses IQR (interquartile range) and Z-score methods. All cleaning operations are non-destructive and require explicit confirmation.

## Privacy & Security

- All processing happens locally in-memory
- No data is sent to external services
- No code execution on user-uploaded content
- Only upload CSV files you have permission to analyze

## Known Limitations

- Large datasets (>10M rows) may require more memory/time
- Date parsing for ambiguous formats requires user guidance
- Some statistical methods assume certain data distributions

## License

MIT License - see LICENSE file for details.

## Author

[Author Name]
