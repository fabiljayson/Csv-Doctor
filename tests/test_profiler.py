import pandas as pd

from src.profiler import Profiler


def test_profile_basic():
    df = pd.DataFrame({"a": [1, 2, 3, None], "b": ["x", "y", "z", "x"]})
    p = Profiler(df)
    prof = p.profile_dataset()
    assert prof["n_rows"] == 4
    assert prof["n_cols"] == 2
    assert prof["missing_summary"]["total_missing"] == 1
