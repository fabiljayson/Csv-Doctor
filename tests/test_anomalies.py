import pandas as pd

from src.anomalies import AnomalyDetector


def test_iqr_basic():
    df = pd.DataFrame({"a": [1, 2, 3, 4, 5, 100]})
    ad = AnomalyDetector(df)
    out, res = ad.detect_iqr("a")
    assert "n_outliers" in res
