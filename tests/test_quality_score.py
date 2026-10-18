import pandas as pd

from src.quality_score import QualityScorer


def test_quality_score_basic():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    scorer = QualityScorer(df)
    res = scorer.overall_score(validity_evaluated=False)
    assert res["overall_score"] >= 0
    assert res["overall_score"] <= 100
