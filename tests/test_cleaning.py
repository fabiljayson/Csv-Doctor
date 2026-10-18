import pandas as pd

from src.cleaning import CleaningConfig, CleaningEngine


def test_cleaning_preserves_original():
    df = pd.DataFrame({"a": [" x ", "y"]})
    ce = CleaningEngine(df)
    config = CleaningConfig([{"type": "trim_whitespace"}])
    res = ce.apply(config)
    assert df.equals(pd.DataFrame({"a": [" x ", "y"]}))  # original unchanged
    assert res["cleaned"].iloc[0]["a"] == "x"
