import pandas as pd

from src.validation import Validator


def test_validation_basic():
    df = pd.DataFrame({"a": [1, 2, 3]})
    v = Validator(df)
    res = v.validate_rules([{"type": "required", "column": "a"}])
    assert "results" in res
