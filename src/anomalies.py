"""Anomaly and outlier detection."""

import numpy as np
import pandas as pd

from .config import APP_CONFIG


class AnomalyDetector:
    """Detect numerical anomalies and outliers."""

    def __init__(self, df: pd.DataFrame, config: dict | None = None):
        self.df = df.copy()
        self.config = config or {}
        self.iqr_mult = self.config.get(
            "iqr_multiplier", APP_CONFIG.anomaly.iqr_multiplier
        )
        self.z_thresh = self.config.get(
            "zscore_threshold", APP_CONFIG.anomaly.zscore_threshold
        )

    def detect_iqr(self, column: str) -> tuple[pd.DataFrame, dict]:
        """Detect outliers using IQR method."""
        if column not in self.df.columns or not pd.api.types.is_numeric_dtype(
            self.df[column]
        ):
            return pd.DataFrame(), {"error": "Invalid numeric column"}
        s = self.df[column].dropna()
        if len(s) < 4:
            return pd.DataFrame(), {"error": "Insufficient data"}
        q1 = s.quantile(0.25)
        q3 = s.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            return pd.DataFrame(), {"error": "Zero IQR", "outliers": 0}
        lower = q1 - self.iqr_mult * iqr
        upper = q3 + self.iqr_mult * iqr
        out_mask = (self.df[column] < lower) | (self.df[column] > upper)
        outliers = self.df[out_mask].copy()
        outliers["_anomaly_reason"] = "IQR"
        outliers["_anomaly_value"] = self.df.loc[out_mask, column]
        return outliers, {
            "method": "IQR",
            "column": column,
            "q1": float(q1),
            "q3": float(q3),
            "iqr": float(iqr),
            "lower": float(lower),
            "upper": float(upper),
            "multiplier": self.iqr_mult,
            "n_outliers": int(out_mask.sum()),
            "percent": round((out_mask.mean() * 100) if len(out_mask) > 0 else 0, 2),
        }

    def detect_zscore(self, column: str) -> tuple[pd.DataFrame, dict]:
        """Detect outliers using Z-score."""
        if column not in self.df.columns or not pd.api.types.is_numeric_dtype(
            self.df[column]
        ):
            return pd.DataFrame(), {"error": "Invalid numeric column"}
        s = self.df[column].dropna()
        if len(s) < APP_CONFIG.anomaly.min_observations:
            return pd.DataFrame(), {"error": "Insufficient data"}
        mean = s.mean()
        std = s.std()
        if std == 0 or pd.isna(std):
            return pd.DataFrame(), {"error": "Zero variance", "outliers": 0}
        zscores = np.abs((self.df[column] - mean) / std)
        out_mask = zscores > self.z_thresh
        outliers = self.df[out_mask].copy()
        outliers["_anomaly_reason"] = "Z-score"
        return outliers, {
            "method": "Z-score",
            "column": column,
            "mean": float(mean),
            "std": float(std),
            "threshold": self.z_thresh,
            "n_outliers": int(out_mask.sum()),
            "percent": round((out_mask.mean() * 100) if len(out_mask) > 0 else 0, 2),
        }

    def get_numeric_columns(self) -> list[str]:
        return self.df.select_dtypes(include=[np.number]).columns.tolist()
