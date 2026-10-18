"""Data profiling engine."""

from typing import Any

import numpy as np
import pandas as pd


class Profiler:
    """Dataset profiler."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.profile = {}

    def profile_dataset(self) -> dict[str, Any]:
        """Generate complete dataset profile."""
        if self.df.empty:
            return self._empty_profile()

        profile = {
            "shape": self.df.shape,
            "n_rows": len(self.df),
            "n_cols": len(self.df.columns),
            "total_cells": len(self.df) * len(self.df.columns),
            "columns": list(self.df.columns),
            "missing_summary": self._missing_summary(),
            "duplicates": self._duplicate_summary(),
            "types": self._type_summary(),
            "memory_usage_mb": self.df.memory_usage(deep=True).sum() / (1024**2),
            "column_profiles": [self._profile_column(col) for col in self.df.columns],
        }
        profile["missing_cells"] = profile["missing_summary"]["total_missing"]
        profile["missing_percent"] = profile["missing_summary"]["total_missing_percent"]
        return profile

    def _empty_profile(self) -> dict[str, Any]:
        return {
            "shape": (0, 0),
            "n_rows": 0,
            "n_cols": 0,
            "total_cells": 0,
            "missing_cells": 0,
            "missing_percent": 0,
            "columns": [],
            "column_profiles": [],
        }

    def _missing_summary(self) -> dict[str, Any]:
        total_missing = self.df.isnull().sum().sum()
        total_cells = len(self.df) * len(self.df.columns)
        return {
            "total_missing": int(total_missing),
            "total_missing_percent": round(
                (total_missing / total_cells * 100) if total_cells > 0 else 0, 2
            ),
            "columns_with_missing": int((self.df.isnull().sum() > 0).sum()),
        }

    def _duplicate_summary(self) -> dict[str, Any]:
        n_duplicates = self.df.duplicated().sum()
        return {
            "n_full_duplicates": int(n_duplicates),
            "full_duplicates_percent": round(
                (n_duplicates / len(self.df) * 100) if len(self.df) > 0 else 0, 2
            ),
        }

    def _type_summary(self) -> dict[str, Any]:
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        datetime_cols = []
        for col in self.df.columns:
            try:
                if pd.api.types.is_datetime64_any_dtype(
                    self.df[col]
                ) or self._is_date_like(self.df[col]):
                    datetime_cols.append(col)
            except Exception:
                pass
        object_cols = [
            c
            for c in self.df.columns
            if c not in numeric_cols and c not in datetime_cols
        ]
        return {
            "numeric": len(numeric_cols),
            "categorical_or_text": len(object_cols),
            "date_like": len(datetime_cols),
        }

    def _is_date_like(self, series) -> bool:
        # simple heuristic for strings that parse as dates
        sample = series.dropna().astype(str).head(5)
        if sample.empty:
            return False
        parsed = 0
        for v in sample:
            try:
                pd.to_datetime(v, errors="raise")
                parsed += 1
            except Exception:
                pass
        return parsed >= 3 if len(sample) >= 3 else parsed > 0

    def _profile_column(self, col) -> dict[str, Any]:
        s = self.df[col]
        profile = {
            "name": col,
            "non_null_count": int(s.notna().sum()),
            "missing_count": int(s.isna().sum()),
            "missing_percent": round((s.isna().mean() * 100) if len(s) > 0 else 0, 2),
            "unique_count": int(s.nunique(dropna=True)),
            "uniqueness_percent": round(
                (s.nunique(dropna=True) / len(s) * 100) if len(s) > 0 else 0, 2
            ),
            "dtype": str(s.dtype),
            "examples": [str(x) for x in s.dropna().head(3).tolist()],
        }
        # numeric stats
        if pd.api.types.is_numeric_dtype(s):
            try:
                profile.update(
                    {
                        "min": float(s.min()),
                        "max": float(s.max()),
                        "mean": float(s.mean()),
                        "median": float(s.median()),
                        "std": float(s.std()) if len(s.dropna()) > 1 else 0,
                    }
                )
                # quantiles
                try:
                    profile["q25"] = float(s.quantile(0.25))
                    profile["q50"] = float(s.quantile(0.5))
                    profile["q75"] = float(s.quantile(0.75))
                except Exception:
                    pass
            except Exception:
                pass
        # top values for categorical
        if not pd.api.types.is_numeric_dtype(s):
            vc = s.value_counts(dropna=True).head(5)
            profile["top_values"] = [
                {"value": str(k), "count": int(v)} for k, v in vc.items()
            ]
        return profile
