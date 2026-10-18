"""Reporting utilities."""

import io
from datetime import datetime

import pandas as pd

from .utils import safe_json_dumps


class Reporter:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def generate_report(self, metadata: dict = None, **components) -> dict:
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "source": metadata or {},
            "dataset": {
                "shape": self.df.shape,
                "n_rows": len(self.df),
                "n_cols": len(self.df.columns),
                "columns": list(self.df.columns),
            },
            "components": components,
        }
        return report

    @staticmethod
    def to_json(report: dict) -> str:
        return safe_json_dumps(report, indent=2)

    @staticmethod
    def to_csv_bytes(df: pd.DataFrame) -> bytes:
        buffer = io.BytesIO()
        df.to_csv(buffer, index=False, encoding="utf-8")
        buffer.seek(0)
        return buffer.getvalue()
