"""Utility functions for CSV Data Quality Doctor."""

import json
import math
from datetime import datetime

import numpy as np
import pandas as pd


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy and pandas types."""

    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            if np.isfinite(obj):
                return float(obj)
            return None
        if isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        if isinstance(obj, pd.Timedelta):
            return str(obj)
        if isinstance(obj, (pd.Period,)):
            return str(obj)
        return super().default(obj)


def safe_json_dumps(obj, **kwargs):
    """Safely dump object to JSON."""
    return json.dumps(obj, cls=NumpyEncoder, **kwargs)


def is_nan_like(value):
    """Check if value is NaN-like."""
    try:
        if value is None:
            return True
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            return True
        if isinstance(value, str):
            val = value.strip().lower()
            return val in (
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
            )
        return pd.isna(value)
    except Exception:
        return False


def format_timestamp(dt=None):
    """Format timestamp to ISO format."""
    if dt is None:
        dt = datetime.now()
    return dt.isoformat()


def normalize_column_name(name):
    """Normalize column name."""
    if isinstance(name, str):
        return name.strip()
    return str(name)
