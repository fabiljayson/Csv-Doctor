"""Data validation rules."""

import re

import pandas as pd


class ValidationRule:
    """Base validation rule."""

    def __init__(self, name: str, column: str, params: dict = None):
        self.name = name
        self.column = column
        self.params = params or {}

    def validate(self, df: pd.DataFrame) -> dict:
        raise NotImplementedError


class RequiredRule(ValidationRule):
    def validate(self, df: pd.DataFrame) -> dict:
        col = self.column
        if col not in df.columns:
            return {"valid": False, "failures": len(df), "errors": ["Column missing"]}
        failures = (
            df[col].isna().sum()
            + ((df[col].astype(str).str.strip() == "") & (df[col].isna())).sum()
            if False
            else df[col].isna().sum()
        )
        failures = int(df[col].isna().sum())
        return {
            "rule": "required",
            "column": col,
            "total": len(df),
            "failures": failures,
            "failure_percent": round(failures / len(df) * 100) if len(df) > 0 else 0,
            "valid": failures == 0,
        }


class MinMaxRule(ValidationRule):
    def validate(self, df: pd.DataFrame) -> dict:
        col = self.column
        if col not in df.columns:
            return {"valid": False, "failures": len(df)}
        min_v = self.params.get("min")
        max_v = self.params.get("max")
        s = pd.to_numeric(df[col], errors="coerce")
        mask = pd.Series([False] * len(df), index=df.index)
        if min_v is not None:
            mask |= s < min_v
        if max_v is not None:
            mask |= s > max_v
        failures = int(mask.sum())
        return {
            "rule": "minmax",
            "column": col,
            "params": self.params,
            "total": len(df),
            "failures": failures,
            "valid": failures == 0,
        }


class CategoricalRule(ValidationRule):
    def validate(self, df: pd.DataFrame) -> dict:
        col = self.column
        allowed = self.params.get("allowed", [])
        if not allowed:
            return {"valid": True, "failures": 0}
        s = df[col].dropna().astype(str).str.strip()
        mask = ~s.isin([str(a) for a in allowed])
        failures = int(mask.sum())
        return {
            "rule": "categorical",
            "column": col,
            "total": len(df),
            "failures": failures,
            "valid": failures == 0,
        }


class LengthRule(ValidationRule):
    def validate(self, df: pd.DataFrame) -> dict:
        col = self.column
        min_l = self.params.get("min")
        max_l = self.params.get("max")
        s = df[col].dropna().astype(str)
        mask = pd.Series([False] * len(s), index=s.index)
        if min_l is not None:
            mask |= s.str.len() < min_l
        if max_l is not None:
            mask |= s.str.len() > max_l
        failures = int(mask.sum())
        return {
            "rule": "length",
            "column": col,
            "total": len(df),
            "failures": failures,
            "valid": failures == 0,
        }


class PatternRule(ValidationRule):
    def validate(self, df: pd.DataFrame) -> dict:
        col = self.column
        pattern = self.params.get("pattern", "")
        try:
            regex = re.compile(pattern)
        except Exception:
            return {"valid": False, "failures": len(df), "error": "Invalid pattern"}
        s = df[col].dropna().astype(str)
        mask = ~s.apply(lambda x: bool(regex.match(x)) or bool(regex.search(x)))
        failures = int(mask.sum())
        return {
            "rule": "pattern",
            "column": col,
            "total": len(df),
            "failures": failures,
            "valid": failures == 0,
        }


class UniquenessRule(ValidationRule):
    def validate(self, df: pd.DataFrame) -> dict:
        col = self.column
        if col not in df.columns:
            return {"valid": False, "failures": len(df)}
        failures = int(df[col].duplicated(keep=False).sum())
        return {
            "rule": "uniqueness",
            "column": col,
            "total": len(df),
            "failures": failures,
            "valid": failures == 0,
        }


class Validator:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def validate_rules(self, rules: list[dict]) -> dict:
        results = []
        for r in rules:
            rule_type = r.get("type")
            name = r.get("name", rule_type)
            column = r.get("column")
            params = r.get("params", {})
            try:
                if rule_type == "required":
                    results.append(RequiredRule(name, column, params).validate(self.df))
                elif rule_type == "minmax":
                    results.append(MinMaxRule(name, column, params).validate(self.df))
                elif rule_type == "categorical":
                    results.append(
                        CategoricalRule(name, column, params).validate(self.df)
                    )
                elif rule_type == "length":
                    results.append(LengthRule(name, column, params).validate(self.df))
                elif rule_type == "pattern":
                    results.append(PatternRule(name, column, params).validate(self.df))
                elif rule_type == "uniqueness":
                    results.append(
                        UniquenessRule(name, column, params).validate(self.df)
                    )
            except Exception as e:
                results.append({"error": str(e), "rule": rule_type})
        return {"results": results}
