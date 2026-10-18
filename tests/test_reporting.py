import pandas as pd

from src.reporting import Reporter


def test_report_json():
    df = pd.DataFrame({"a": [1, 2, 3]})
    r = Reporter(df)
    rep = r.generate_report()
    json_str = r.to_json(rep)
    assert isinstance(json_str, str)
