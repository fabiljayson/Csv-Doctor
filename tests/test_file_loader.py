import io

import pytest

from src.file_loader import load_csv


def test_load_valid_csv():
    data = "a,b\n1,2\n3,4"
    f = io.StringIO(data)
    f.name = "test.csv"
    df, meta = load_csv(f)
    assert len(df) == 2
    assert len(df.columns) == 2


def test_empty_file():
    from src.exceptions import EmptyFileError

    f = io.StringIO("")
    f.name = "empty.csv"
    with pytest.raises(EmptyFileError):
        load_csv(f)
