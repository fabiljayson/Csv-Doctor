import pandas as pd

from src.duplicates import DuplicateDetector


def test_duplicates_detect():
    df = pd.DataFrame({"a": [1, 2, 1], "b": ["x", "y", "x"]})
    d = DuplicateDetector(df)
    dups, info = d.detect_exact_duplicates()
    assert info["n_exact_duplicates"] >= 2
