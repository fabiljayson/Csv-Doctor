"""CSV file loading utilities."""

import io

import pandas as pd

from .config import APP_CONFIG
from .exceptions import EmptyFileError, FileLoadError, TooLargeFileError


def load_csv(
    file_obj,
    encoding: str = "utf-8",
    delimiter: str = ",",
    header: int | None = 0,
    nrows: int | None = None,
) -> tuple[pd.DataFrame, dict[str, any]]:
    metadata = {
        "encoding": encoding,
        "delimiter": delimiter,
        "header": header,
        "original_file_name": getattr(file_obj, "name", "unknown"),
        "file_size": getattr(file_obj, "size", 0),
        "nrows_read": nrows,
    }

    file_size_mb = (
        metadata["file_size"] / (1024 * 1024) if metadata["file_size"] > 0 else 0
    )
    if file_size_mb > APP_CONFIG.file_upload.max_size_mb:
        raise TooLargeFileError(
            f"File exceeds {APP_CONFIG.file_upload.max_size_mb}MB limit"
        )

    try:
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)
        content = file_obj.read()

        if isinstance(content, bytes):
            if content.startswith(b"\xef\xbb\xbf"):
                encoding = "utf-8-sig"
                metadata["encoding"] = encoding
            content_str = content.decode(encoding, errors="replace")
        else:
            content_str = str(content)

        if not content_str or content_str.strip() == "":
            raise EmptyFileError("File is empty or contains no data")

        try:
            df = pd.read_csv(
                io.StringIO(content_str),
                delimiter=delimiter,
                header=header,
                engine="python",
                on_bad_lines="warn",
                nrows=nrows,
            )
        except pd.errors.EmptyDataError:
            raise EmptyFileError("File is empty or contains no data")

        if df.empty:
            raise EmptyFileError("File is empty or contains no data")

        metadata["nrows"] = len(df)
        metadata["ncols"] = len(df.columns)
        metadata["columns"] = list(df.columns)
        return df, metadata
    except EmptyFileError:
        raise
    except Exception as e:
        raise FileLoadError(f"Failed to load CSV: {e!s}")


def get_csv_preview(file_obj, n_rows: int = 20) -> pd.DataFrame:
    if hasattr(file_obj, "seek"):
        file_obj.seek(0)
    return load_csv(file_obj, nrows=n_rows)[0]
