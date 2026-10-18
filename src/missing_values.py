"""Missing value detection and handling."""

import pandas as pd

from .utils import is_nan_like


class MissingValueAnalyzer:
    """Analyze and handle missing values."""

    def __init__(self, df: pd.DataFrame, missing_tokens: list[str] | None = None):
        self.original = df
        self.missing_tokens = missing_tokens or [
            "",
            " ",
            "nan",
            "na",
            "n/a",
            "null",
            "none",
            "unknown",
            "-",
            "?",
            "#n/a",
            "#na",
        ]

    def detect_missing(self) -> tuple[pd.DataFrame, dict]:
        """Detect missing values with custom token handling."""
        df = self.original.copy()
        missing_mask = df.isnull().copy()

        # Check string columns for missing tokens
        for col in df.columns:
            if (
                df[col].dtype == object
                or pd.api.types.is_string_dtype(df[col])
                or isinstance(df[col].dtype, object)
            ):
                mask = df[col].apply(
                    lambda x: (
                        is_nan_like(x)
                        or (
                            isinstance(x, str)
                            and str(x).strip().lower()
                            in [t.lower() for t in self.missing_tokens]
                        )
                    )
                )
                missing_mask.loc[mask, col] = True
                df.loc[mask, col] = pd.NA
        return df, self._summarize(df, missing_mask)

    def _summarize(self, df_clean: pd.DataFrame, missing_mask: pd.DataFrame) -> dict:
        per_col = df_clean.isnull().sum().to_dict()
        per_col_pct = (df_clean.isnull().mean() * 100).to_dict()
        total_missing = df_clean.isnull().sum().sum()
        total = len(df_clean) * len(df_clean.columns)
        return {
            "per_column": {k: int(v) for k, v in per_col.items()},
            "per_column_percent": {
                k: round(float(v), 2) for k, v in per_col_pct.items()
            },
            "total_missing": int(total_missing),
            "total_cells": total,
            "total_missing_percent": round(
                (total_missing / total * 100) if total > 0 else 0, 2
            ),
            "columns_with_missing": sum(1 for v in per_col.values() if v > 0),
            "all_null_columns": [k for k, v in per_col.items() if v == len(df_clean)],
        }

    @staticmethod
    def get_strategies():
        return [
            "keep",
            "drop_rows",
            "drop_columns",
            "fill_mean",
            "fill_median",
            "fill_mode",
            "fill_constant",
            "ffill",
            "bfill",
        ]

    @staticmethod
    def apply_cleaning(df: pd.DataFrame, strategy: str, **kwargs) -> pd.DataFrame:
        df_out = df.copy()
        if strategy == "keep":
            return df_out
        if strategy == "drop_rows":
            return df_out.dropna()
        if strategy == "drop_columns":
            thresh = kwargs.get("threshold", 100)
            if thresh >= 100:
                return df_out.dropna(axis=1, how="all")
            min_non_null = int((1 - thresh / 100) * len(df_out))
            return df_out.dropna(axis=1, thresh=min_non_null)
        if strategy == "fill_mean":
            for col in df_out.select_dtypes(include=["number"]).columns:
                if df_out[col].isna().any():
                    df_out[col] = df_out[col].fillna(df_out[col].mean())
            return df_out
        if strategy == "fill_median":
            for col in df_out.select_dtypes(include=["number"]).columns:
                if df_out[col].isna().any():
                    df_out[col] = df_out[col].fillna(df_out[col].median())
            return df_out
        if strategy == "fill_mode":
            for col in df_out.columns:
                if df_out[col].isna().any():
                    try:
                        mode = df_out[col].mode(dropna=True)
                        if not mode.empty:
                            df_out[col] = df_out[col].fillna(mode.iloc[0])
                    except Exception:
                        pass
            return df_out
        if strategy == "fill_constant":
            value = kwargs.get("value", "Unknown")
            return df_out.fillna(value)
        if strategy == "ffill":
            return df_out.ffill()
        if strategy == "bfill":
            return df_out.bfill()
        return df_out
