"""Custom exceptions for CSV Data Quality Doctor."""


class DataQualityException(Exception):
    """Base exception for the application."""


class FileLoadError(DataQualityException):
    """Exception raised when file loading fails."""


class EmptyFileError(FileLoadError):
    """Exception raised for empty files."""


class UnsupportedFormatError(FileLoadError):
    """Exception raised for unsupported formats."""


class TooLargeFileError(FileLoadError):
    """Exception raised for files that exceed size limits."""


class DataProcessingError(DataQualityException):
    """Exception raised during data processing."""


class InvalidConfigError(DataQualityException):
    """Exception raised for invalid configuration."""


class ValidationError(DataQualityException):
    """Exception raised for validation failures."""
