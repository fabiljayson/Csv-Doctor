"""Format checks and consistency analysis."""

import pandas as pd


class FormatChecker:
    """Check for inconsistent formats."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.issues = []

    def check_whitespace(self) -> dict:
        """Check for leading/trailing whitespace in strings."""
        issues = []
        for col in self.df.columns:
            if self.df[col].dtype == object:
                for idx, val in self.df[col].dropna().items():
                    s = str(val)
                    if s != s.strip():
                        issues.append(
                            {
                                "col": col,
                                "index": idx,
                                "value": s,
                                "issue": "leading_trailing_space",
                            }
                        )
                        break  # just sample
        return {"issues": issues[:10], "count": len(issues)}

    def check_case_inconsistency(self) -> dict:
        """Check for case inconsistencies in categorical values."""
        issues = []
        for col in self.df.columns:
            if self.df[col].dtype == object:
                values = self.df[col].dropna().astype(str)
                lower_map = {}
                for v in values:
                    lower_map.setdefault(v.lower().strip(), set()).add(v)
                for k, variants in lower_map.items():
                    if len(variants) > 1:
                        issues.append(
                            {
                                "col": col,
                                "value": k,
                                "variants": list(variants),
                                "issue": "case_variants",
                            }
                        )
                        break
        return {"issues": issues[:10], "count": len(issues)}

    def check_empty_strings(self) -> dict:
        """Check for empty strings."""
        issues = []
        for col in self.df.columns:
            if self.df[col].dtype == object:
                mask = self.df[col].astype(str).str.strip() == ""
                if mask.sum() > 0:
                    issues.append(
                        {"col": col, "count": int(mask.sum()), "issue": "empty_strings"}
                    )
        return {"issues": issues[:10], "count": len(issues)}

    def check_date_format(self) -> dict:
        """Check date formats."""
        issues = []
        patterns = [
            r"\d{4}-\d{2}-\d{2}",
            r"\d{2}/\d{2}/\d{4}",
            r"\d{2}-\d{2}-\d{4}",
        ]
        for col in self.df.columns:
            if self.df[col].dtype == object:
                parsed = 0
                total = self.df[col].dropna().shape[0]
                if total > 0:
                    for v in self.df[col].dropna().astype(str).head(10):
                        try:
                            pd.to_datetime(v, errors="raise")
                            parsed += 1
                        except Exception:
                            pass
                    if parsed < total * 0.5 and total > 0:
                        issues.append(
                            {
                                "col": col,
                                "parsed_count": parsed,
                                "total": total,
                                "issue": "date_parse_issues",
                            }
                        )
        return {"issues": issues[:10], "count": len(issues)}

    def check_numeric_strings(self) -> dict:
        """Check for numeric values stored as strings."""
        issues = []
        for col in self.df.columns:
            if self.df[col].dtype == object:
                count = 0
                sample = []
                for v in self.df[col].dropna().astype(str).head(20):
                    # remove common formatting
                    cleaned = (
                        v.strip().replace(",", "").replace("$", "").replace(" ", "")
                    )
                    try:
                        float(cleaned)
                        count += 1
                        if len(sample) < 3:
                            sample.append(v)
                    except Exception:
                        pass
                if (
                    count > 0
                    and count == len(self.df[col].dropna().astype(str).head(20))
                    and len(self.df[col].dropna()) > 0
                ):
                    issues.append(
                        {
                            "col": col,
                            "count": len(self.df[col].dropna()),
                            "sample": sample,
                            "issue": "numeric_as_string",
                        }
                    )
        return {"issues": issues[:10], "count": len(issues)}

    def check_mixed_types(self) -> dict:
        """Check for mixed data types."""
        issues = []
        for col in self.df.columns:
            if self.df[col].dtype == object:
                types = set()
                for v in self.df[col].dropna().astype(str).head(100):
                    cleaned = v.strip()
                    if cleaned == "":
                        continue
                    # check numeric
                    try:
                        float(cleaned.replace(",", ""))
                        types.add("numeric")
                        continue
                    except Exception:
                        pass
                    # check date-like
                    try:
                        pd.to_datetime(cleaned, errors="raise")
                        types.add("date")
                        continue
                    except Exception:
                        pass
                    types.add("text")
                if len(types) > 1:
                    issues.append(
                        {"col": col, "types": list(types), "issue": "mixed_types"}
                    )
        return {"issues": issues[:10], "count": len(issues)}

    def get_all_issues(self) -> dict:
        return {
            "whitespace": self.check_whitespace(),
            "case": self.check_case_inconsistency(),
            "empty_strings": self.check_empty_strings(),
            "dates": self.check_date_format(),
            "numeric_strings": self.check_numeric_strings(),
            "mixed_types": self.check_mixed_types(),
        }
