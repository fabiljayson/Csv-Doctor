from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.anomalies import AnomalyDetector
from src.cleaning import CleaningConfig, CleaningEngine
from src.config import APP_CONFIG
from src.duplicates import DuplicateDetector
from src.file_loader import load_csv
from src.format_checks import FormatChecker
from src.missing_values import MissingValueAnalyzer
from src.profiler import Profiler
from src.quality_score import QualityScorer
from src.reporting import Reporter
from src.validation import Validator

st.set_page_config(
    page_title=APP_CONFIG.app_name,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title(APP_CONFIG.app_name)
st.caption(APP_CONFIG.description)


def init_session_state():
    if "original_df" not in st.session_state:
        st.session_state.original_df = None
    if "cleaned_df" not in st.session_state:
        st.session_state.cleaned_df = None
    if "metadata" not in st.session_state:
        st.session_state.metadata = {}
    if "validation_rules" not in st.session_state:
        st.session_state.validation_rules = []
    if "cleaning_ops" not in st.session_state:
        st.session_state.cleaning_ops = []
    if "analysis_done" not in st.session_state:
        st.session_state.analysis_done = False


def reset_state():
    st.session_state.original_df = None
    st.session_state.cleaned_df = None
    st.session_state.metadata = {}
    st.session_state.validation_rules = []
    st.session_state.cleaning_ops = []
    st.session_state.analysis_done = False


def sidebar():
    with st.sidebar:
        st.header("CSV Data Quality Doctor")
        st.markdown("Upload a CSV to analyze data quality")

        # Upload
        uploaded = st.file_uploader("Upload CSV file", type=["csv"])
        if uploaded is not None:
            try:
                # Check if new file
                if st.session_state.metadata.get("original_file_name") != uploaded.name:
                    reset_state()
                df, meta = load_csv(uploaded)
                st.session_state.original_df = df
                st.session_state.cleaned_df = df.copy()
                st.session_state.metadata = meta
                st.session_state.analysis_done = True
                st.success(f"Loaded {len(df)} rows × {len(df.columns)} columns")
            except Exception as e:
                st.error(f"Error loading file: {e}")

        # Sample dataset
        sample_path = Path("data/sample_messy_data.csv")
        if sample_path.exists():
            with open(sample_path, "rb") as f:
                st.download_button(
                    "Download sample dataset", f, "sample_messy_data.csv", "text/csv"
                )
            if st.button("Load sample dataset"):
                try:
                    df = pd.read_csv(sample_path)
                    st.session_state.original_df = df
                    st.session_state.cleaned_df = df.copy()
                    st.session_state.metadata = {
                        "original_file_name": "sample_messy_data.csv"
                    }
                    st.session_state.analysis_done = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

        # Dataset info
        if st.session_state.original_df is not None:
            df = st.session_state.original_df
            st.subheader("Dataset Info")
            st.metric("Rows", len(df))
            st.metric("Columns", len(df.columns))
            st.metric("Cells", len(df) * len(df.columns))
            st.write("Columns:", ", ".join(df.columns.tolist()[:10]))

        st.divider()
        page = st.radio(
            "Navigation",
            [
                "Overview",
                "Data Explorer",
                "Missing Values",
                "Duplicates",
                "Anomalies",
                "Format Checks",
                "Validation",
                "Cleaning Studio",
                "Export Center",
            ],
        )
        st.session_state.page = page


def page_overview():
    if st.session_state.original_df is None:
        st.info("Upload a CSV file to get started")
        return
    df = st.session_state.original_df
    profiler = Profiler(df)
    profile = profiler.profile_dataset()

    # Quality score
    checker = FormatChecker(df)
    format_issues = checker.get_all_issues()
    scorer = QualityScorer(df)
    score = scorer.overall_score(
        format_issues=format_issues,
        validity_evaluated=len(st.session_state.validation_rules) > 0,
        validation_results=None,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall Quality", f"{score['overall_score']:.1f}/100")
    c2.metric("Missing %", f"{profile['missing_percent']:.1f}%")
    c3.metric("Duplicates", profile["duplicates"]["n_full_duplicates"])
    c4.metric("Columns", profile["n_cols"])

    st.subheader("Dataset Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Rows", profile["n_rows"])
        st.metric("Total Columns", profile["n_cols"])
        st.metric("Total Cells", profile["total_cells"])
    with col2:
        st.metric("Missing Cells", profile["missing_summary"]["total_missing"])
        st.metric(
            "Columns with Missing", profile["missing_summary"]["columns_with_missing"]
        )
        st.metric("Full Duplicates", profile["duplicates"]["n_full_duplicates"])

    st.subheader("Recommended Next Steps")
    st.write("- Review Missing Values page to handle missing data")
    st.write("- Check Duplicates for redundant records")
    st.write("- Examine Anomalies for outliers")
    st.write("- Run Format Checks for consistency issues")


def page_data_explorer():
    if st.session_state.original_df is None:
        st.info("Upload a CSV file")
        return
    df = st.session_state.cleaned_df
    st.subheader("Data Explorer")
    st.dataframe(df, use_container_width=True, height=400)
    st.write(f"Showing {len(df)} rows")


def page_missing_values():
    if st.session_state.original_df is None:
        st.info("Upload a CSV file")
        return
    df = st.session_state.original_df
    analyzer = MissingValueAnalyzer(df)
    df_cleaned_detect, summary = analyzer.detect_missing()

    st.subheader("Missing Values")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Missing", summary["total_missing"])
    c2.metric("Missing %", f"{summary['total_missing_percent']:.2f}%")
    c3.metric("Cols with Missing", summary["columns_with_missing"])

    st.write("Per-column missing values")
    missing_df = pd.DataFrame(
        {
            "Column": summary["per_column"].keys(),
            "Missing": summary["per_column"].values(),
            "%": [
                summary["per_column_percent"][k] for k in summary["per_column"].keys()
            ],
        }
    )
    st.dataframe(missing_df, use_container_width=True)

    # Chart
    if missing_df["Missing"].sum() > 0:
        fig = px.bar(
            missing_df.sort_values("Missing", ascending=False),
            x="Column",
            y="Missing",
            title="Missing Values by Column",
        )
        st.plotly_chart(fig, use_container_width=True)


def page_duplicates():
    if st.session_state.original_df is None:
        st.info("Upload a CSV file")
        return
    df = st.session_state.original_df
    detector = DuplicateDetector(df)
    dups, info = detector.detect_exact_duplicates()
    st.subheader("Duplicates")
    c1, c2 = st.columns(2)
    c1.metric("Exact Duplicate Rows", info["n_exact_duplicates"])
    c2.metric("Duplicate Groups", info["n_unique_duplicate_groups"])
    if not dups.empty:
        st.write("Duplicate rows (showing first few):")
        st.dataframe(dups.head(20), use_container_width=True)


def page_anomalies():
    if st.session_state.original_df is None:
        st.info("Upload a CSV file")
        return
    df = st.session_state.original_df
    detector = AnomalyDetector(df)
    num_cols = detector.get_numeric_columns()
    st.subheader("Anomalies & Outliers")
    if not num_cols:
        st.info("No numeric columns found")
        return
    col = st.selectbox("Select numeric column", num_cols)
    if st.button("Detect IQR Outliers"):
        out, res = detector.detect_iqr(col)
        if "error" in res:
            st.warning(res["error"])
        else:
            st.write(res)
            if not out.empty:
                st.dataframe(out.head(10), use_container_width=True)
    if st.button("Detect Z-score Outliers"):
        out, res = detector.detect_zscore(col)
        if "error" in res:
            st.warning(res["error"])
        else:
            st.write(res)
            if not out.empty:
                st.dataframe(out.head(10), use_container_width=True)


def page_format_checks():
    if st.session_state.original_df is None:
        st.info("Upload a CSV file")
        return
    df = st.session_state.original_df
    checker = FormatChecker(df)
    issues = checker.get_all_issues()
    st.subheader("Format Checks")
    for cat, data in issues.items():
        with st.expander(f"{cat.replace('_', ' ').title()} ({data['count']})"):
            st.json(data["issues"])


def page_validation():
    if st.session_state.original_df is None:
        st.info("Upload a CSV file")
        return
    df = st.session_state.original_df
    st.subheader("Validation Rules")
    st.info("Configure validation rules (basic interface)")
    validator = Validator(df)
    if st.session_state.validation_rules:
        results = validator.validate_rules(st.session_state.validation_rules)
        st.write(results)


def page_cleaning_studio():
    if st.session_state.original_df is None:
        st.info("Upload a CSV file")
        return
    st.subheader("Cleaning Studio")
    df = st.session_state.cleaned_df
    st.write(f"Current shape: {df.shape}")
    if st.button("Trim whitespace"):
        config = CleaningConfig([{"type": "trim_whitespace"}])
        engine = CleaningEngine(st.session_state.original_df)
        res = engine.apply(config)
        st.session_state.cleaned_df = res["cleaned"]
        st.success("Applied trim whitespace")
        st.rerun()
    if st.button("Reset to original"):
        st.session_state.cleaned_df = st.session_state.original_df.copy()
        st.rerun()


def page_export_center():
    if st.session_state.original_df is None:
        st.info("Upload a CSV file")
        return
    df_clean = st.session_state.cleaned_df
    df_orig = st.session_state.original_df
    st.subheader("Export Center")

    # CSV export
    csv_data = Reporter.to_csv_bytes(df_clean)
    st.download_button("Download Cleaned CSV", csv_data, "cleaned_data.csv", "text/csv")

    # JSON report
    profiler = Profiler(df_orig)
    profile = profiler.profile_dataset()
    checker = FormatChecker(df_orig)
    format_issues = checker.get_all_issues()
    scorer = QualityScorer(df_orig)
    score = scorer.overall_score(format_issues=format_issues, validity_evaluated=False)
    reporter = Reporter(df_orig)
    report = reporter.generate_report(
        metadata=st.session_state.metadata,
        profile=profile,
        quality_score=score,
        format_issues=format_issues,
    )
    json_data = reporter.to_json(report)
    st.download_button(
        "Download Quality Report (JSON)",
        json_data,
        "quality_report.json",
        "application/json",
    )


def main():
    init_session_state()
    sidebar()
    page = st.session_state.get("page", "Overview")
    if page == "Overview":
        page_overview()
    elif page == "Data Explorer":
        page_data_explorer()
    elif page == "Missing Values":
        page_missing_values()
    elif page == "Duplicates":
        page_duplicates()
    elif page == "Anomalies":
        page_anomalies()
    elif page == "Format Checks":
        page_format_checks()
    elif page == "Validation":
        page_validation()
    elif page == "Cleaning Studio":
        page_cleaning_studio()
    elif page == "Export Center":
        page_export_center()


if __name__ == "__main__":
    main()
