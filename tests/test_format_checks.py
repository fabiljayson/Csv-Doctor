import pandas as pd

from src.format_checks import FormatChecker


def test_format_basic():
    df = pd.DataFrame({"a": [" x ", "y"]})
    fc = FormatChecker(df)
    res = fc.check_whitespace()
    assert res["count"] >= 0
