"""Data cleaning engine."""

import pandas as pd

from .duplicates import DuplicateDetector
from .missing_values import MissingValueAnalyzer


class CleaningConfig:
    def __init__(self, operations: list[dict] | None = None):
        self.operations = operations or []

    def add_operation(self, op: dict):
        self.operations.append(op)


class CleaningEngine:
    def __init__(self, df: pd.DataFrame):
        self.original = df.copy()
        self.cleaned = df.copy()
        self.history = []

    def apply(self, config: CleaningConfig) -> dict:
        self.cleaned = self.original.copy()
        self.history = []
        for op in config.operations:
            op_type = op.get("type")
            try:
                if op_type == "missing":
                    strategy = op.get("strategy", "keep")
                    result = MissingValueAnalyzer.apply_cleaning(
                        self.cleaned, strategy, **op.get("params", {})
                    )
                    self.history.append({"op": op_type, "strategy": strategy})
                    self.cleaned = result
                elif op_type == "duplicates":
                    keep = op.get("keep", "first")
                    subset = op.get("subset")
                    before = len(self.cleaned)
                    self.cleaned = DuplicateDetector.remove_duplicates(
                        self.cleaned, keep=keep, subset=subset
                    )
                    self.history.append(
                        {
                            "op": op_type,
                            "keep": keep,
                            "rows_removed": before - len(self.cleaned),
                        }
                    )
                elif op_type == "trim_whitespace":
                    for col in self.cleaned.columns:
                        if (
                            pd.api.types.is_string_dtype(self.cleaned[col])
                            or self.cleaned[col].dtype == object
                        ):
                            self.cleaned[col] = (
                                self.cleaned[col].astype(str).str.strip()
                            )
                            self.cleaned[col] = self.cleaned[col].replace({"": pd.NA})
                    self.history.append(
                        {"op": op_type, "cols": list(self.cleaned.columns)}
                    )
                elif op_type == "normalize_case":
                    case = op.get("case", "lower")
                    for col in self.cleaned.columns:
                        if (
                            pd.api.types.is_string_dtype(self.cleaned[col])
                            or self.cleaned[col].dtype == object
                        ):
                            if case == "lower":
                                self.cleaned[col] = (
                                    self.cleaned[col]
                                    .astype(str)
                                    .str.lower()
                                    .str.strip()
                                )
                            elif case == "upper":
                                self.cleaned[col] = (
                                    self.cleaned[col]
                                    .astype(str)
                                    .str.upper()
                                    .str.strip()
                                )
                            elif case == "title":
                                self.cleaned[col] = (
                                    self.cleaned[col]
                                    .astype(str)
                                    .str.title()
                                    .str.strip()
                                )
                    self.history.append({"op": op_type, "case": case})
                elif op_type == "to_numeric":
                    cols = op.get("columns", [])
                    for c in cols:
                        if c in self.cleaned.columns:
                            self.cleaned[c] = pd.to_numeric(
                                self.cleaned[c].astype(str).str.replace(",", ""),
                                errors="coerce",
                            )
                    self.history.append({"op": op_type, "cols": cols})
                elif op_type == "to_datetime":
                    cols = op.get("columns", [])
                    for c in cols:
                        if c in self.cleaned.columns:
                            self.cleaned[c] = pd.to_datetime(
                                self.cleaned[c], errors="coerce"
                            )
                    self.history.append({"op": op_type, "cols": cols})
            except Exception as e:
                self.history.append({"op": op_type, "error": str(e)})
        return {
            "cleaned": self.cleaned,
            "history": self.history,
            "original_shape": self.original.shape,
            "cleaned_shape": self.cleaned.shape,
        }

    def reset(self):
        self.cleaned = self.original.copy()
        self.history = []
