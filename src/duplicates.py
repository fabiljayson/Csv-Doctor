"""Duplicate detection."""

import pandas as pd


class DuplicateDetector:
    """Detect and handle duplicates."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def detect_exact_duplicates(self) -> tuple[pd.DataFrame, dict]:
        """Detect completely duplicated rows."""
        duplicated_mask = self.df.duplicated(keep=False)
        duplicates = self.df[duplicated_mask].copy()
        return duplicates, {
            "n_exact_duplicates": int(duplicated_mask.sum()),
            "n_duplicate_rows": int(duplicated_mask.sum()),
            "n_unique_duplicate_groups": len(duplicates) if not duplicates.empty else 0,
        }

    def detect_key_duplicates(
        self, key_columns: list[str]
    ) -> tuple[pd.DataFrame, dict]:
        """Detect duplicates based on key columns."""
        if not key_columns or any(c not in self.df.columns for c in key_columns):
            return pd.DataFrame(), {"error": "Invalid key columns"}
        duplicated_mask = self.df.duplicated(subset=key_columns, keep=False)
        duplicates = self.df[duplicated_mask].copy()
        return duplicates, {
            "key_columns": key_columns,
            "n_key_duplicates": int(duplicated_mask.sum()),
            "n_groups": int(self.df[duplicated_mask].groupby(key_columns).ngroups)
            if not duplicates.empty
            else 0,
        }

    @staticmethod
    def remove_duplicates(
        df: pd.DataFrame, keep: str = "first", subset: list[str] | None = None
    ) -> pd.DataFrame:
        """Remove duplicates. keep can be 'first', 'last', or 'none'."""
        if keep == "none":
            return df[~df.duplicated(subset=subset, keep=False)].copy()
        return df.drop_duplicates(subset=subset, keep=keep).copy()
