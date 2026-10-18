"""Configuration settings for CSV Data Quality Doctor."""

from dataclasses import dataclass, field

# File handling
MAX_FILE_SIZE_MB = 200
MAX_ROWS = 10_000_000
SUPPORTED_FORMATS = [".csv"]
DEFAULT_PREVIEW_ROWS = 20
COMMON_ENCODINGS = ["utf-8", "utf-8-sig", "latin1", "cp1252", "iso-8859-1"]
COMMON_DELIMITERS = [",", ";", "\t", "|", ":", " "]

# Missing value tokens
DEFAULT_MISSING_TOKENS = [
    "",
    " ",
    "nan",
    "NaN",
    "NAN",
    "na",
    "NA",
    "n/a",
    "N/A",
    "null",
    "NULL",
    "None",
    "unknown",
    "Unknown",
    "UNKNOWN",
    "-",
    "?",
    "#N/A",
    "#NA",
]

# Quality score weights (sum to 1.0)
DEFAULT_QUALITY_WEIGHTS = {
    "completeness": 0.35,
    "uniqueness": 0.25,
    "validity": 0.25,
    "consistency": 0.15,
}

# Anomaly detection
DEFAULT_IQR_MULTIPLIER = 1.5
DEFAULT_ZSCORE_THRESHOLD = 3.0
MIN_OBSERVATIONS_FOR_ZSCORE = 3

# Date parsing
COMMON_DATE_FORMATS = [
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%Y/%m/%d",
    "%d-%m-%Y",
    "%m-%d-%Y",
    "%Y-%m-%d %H:%M:%S",
    "%d/%m/%Y %H:%M:%S",
    "%Y/%m/%d %H:%M:%S.%f",
    "%d-%m-%Y %H:%M:%S",
    "%d.%m.%Y",
    "%m.%d.%Y",
]


@dataclass
class MissingValueConfig:
    """Configuration for missing value handling."""

    treat_as_missing: list[str] = field(default_factory=lambda: DEFAULT_MISSING_TOKENS)
    show_whitespace_as_missing: bool = True


@dataclass
class FileUploadConfig:
    """Configuration for file upload."""

    max_size_mb: int = MAX_FILE_SIZE_MB
    max_rows: int = MAX_ROWS
    supported_formats: list[str] = field(default_factory=lambda: SUPPORTED_FORMATS)
    default_preview_rows: int = DEFAULT_PREVIEW_ROWS
    common_encodings: list[str] = field(default_factory=lambda: COMMON_ENCODINGS)
    common_delimiters: list[str] = field(default_factory=lambda: COMMON_DELIMITERS)


@dataclass
class QualityScoreConfig:
    """Configuration for quality scoring."""

    weights: dict[str, float] = field(default_factory=lambda: DEFAULT_QUALITY_WEIGHTS)


@dataclass
class AnomalyConfig:
    """Configuration for anomaly detection."""

    iqr_multiplier: float = DEFAULT_IQR_MULTIPLIER
    zscore_threshold: float = DEFAULT_ZSCORE_THRESHOLD
    min_observations: int = MIN_OBSERVATIONS_FOR_ZSCORE


@dataclass
class AppConfig:
    """Main application configuration."""

    file_upload: FileUploadConfig = field(default_factory=FileUploadConfig)
    missing: MissingValueConfig = field(default_factory=MissingValueConfig)
    quality_score: QualityScoreConfig = field(default_factory=QualityScoreConfig)
    anomaly: AnomalyConfig = field(default_factory=AnomalyConfig)
    app_name: str = "CSV Data Quality Doctor"
    version: str = "1.0.0"
    description: str = "Comprehensive CSV data quality analysis and cleaning tool."


APP_CONFIG = AppConfig()
