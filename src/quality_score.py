"""Data quality scoring."""

import pandas as pd

from .config import DEFAULT_QUALITY_WEIGHTS


class QualityScorer:
    def __init__(self, df: pd.DataFrame, weights: dict[str, float] | None = None):
        self.df = df.copy()
        self.weights = weights or DEFAULT_QUALITY_WEIGHTS

    def score_completeness(self) -> dict:
        if self.df.empty:
            return {"score": 0, "missing_percent": 100}
        total_cells = len(self.df) * len(self.df.columns)
        missing = self.df.isnull().sum().sum()
        completeness = 1 - (missing / total_cells) if total_cells > 0 else 0
        return {
            "score": round(completeness * 100, 2),
            "missing_cells": int(missing),
            "total_cells": total_cells,
            "missing_percent": round(missing / total_cells * 100, 2),
        }

    def score_uniqueness(self) -> dict:
        if self.df.empty:
            return {"score": 0, "dup_percent": 100}
        n_rows = len(self.df)
        n_dups = self.df.duplicated().sum()
        uniqueness = 1 - (n_dups / n_rows) if n_rows > 0 else 0
        return {
            "score": round(uniqueness * 100, 2),
            "duplicates": int(n_dups),
            "dup_percent": round(n_dups / n_rows * 100, 2),
        }

    def score_validity(
        self, validation_results: dict | None = None, evaluated: bool = False
    ) -> dict:
        if not evaluated:
            return {
                "score": None,
                "evaluated": False,
                "reason": "No validation rules configured",
            }
        results = validation_results or {}
        total_failures = 0
        total_checks = 0
        for r in results.get("results", []):
            if "failures" in r and "total" in r:
                total_failures += r["failures"]
                total_checks += r["total"]
        if total_checks == 0:
            return {"score": 100.0, "evaluated": True}
        validity = 1 - (total_failures / total_checks)
        return {
            "score": round(validity * 100, 2),
            "evaluated": True,
            "total_failures": total_failures,
            "total_checks": total_checks,
        }

    def score_consistency(self, format_issues: dict | None = None) -> dict:
        # simple heuristic based on detected issues
        if format_issues is None:
            return {"score": 100.0, "issues_count": 0}
        total_issues = 0
        for k, v in format_issues.items():
            total_issues += v.get("count", 0)
        # cap impact
        consistency = max(0, 1 - min(total_issues / 100, 1.0))
        return {
            "score": round(consistency * 100, 2),
            "issues_count": total_issues,
        }

    def overall_score(self, **kwargs) -> dict:
        comp = self.score_completeness()
        uniq = self.score_uniqueness()
        valid = self.score_validity(
            kwargs.get("validation_results"), kwargs.get("validity_evaluated", False)
        )
        cons = self.score_consistency(kwargs.get("format_issues"))

        score_parts = []
        total_w = 0
        if comp["score"] is not None:
            score_parts.append(comp["score"] * self.weights["completeness"])
            total_w += self.weights["completeness"]
        if uniq["score"] is not None:
            score_parts.append(uniq["score"] * self.weights["uniqueness"])
            total_w += self.weights["uniqueness"]
        if valid["score"] is not None:
            score_parts.append(valid["score"] * self.weights["validity"])
            total_w += self.weights["validity"]
        if cons["score"] is not None:
            score_parts.append(cons["score"] * self.weights["consistency"])
            total_w += self.weights["consistency"]

        overall = sum(score_parts) / total_w if total_w > 0 else 0
        return {
            "overall_score": round(overall, 2),
            "completeness": comp,
            "uniqueness": uniq,
            "validity": valid,
            "consistency": cons,
            "weights": self.weights,
        }
