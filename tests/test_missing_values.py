import pandas as pd

from src.missing_values import MissingValueAnalyzer


def test_missing_detect():
    df = pd.DataFrame({"a": [1, None, 3], "b": ["x", "", "y"]})
    m = MissingValueAnalyzer(df)
    df_clean, summary = m.detect_missing()
    assert summary["total_missing"] >= 2
