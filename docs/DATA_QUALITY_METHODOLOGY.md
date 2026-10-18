# Data Quality Methodology

## Missing Values

- Detected via pandas null checks (NaN, None, NaT)
- Configurable token list for string representations
- Metrics: count, percentage per column and overall

## Duplicates

- Exact row duplicates
- Key-based duplicates on selected columns
- Strategies: keep first/last, remove all

## Anomaly Detection

### IQR Method
Q1 = 25th percentile, Q3 = 75th percentile, IQR = Q3 - Q1  
Lower = Q1 - 1.5*IQR, Upper = Q3 + 1.5*IQR

### Z-Score
z = |(x - μ)/σ|, flag if z > threshold (default 3.0)

Notes: Methods assume approximate distribution; outliers are not necessarily errors.

## Format Consistency

- Whitespace: leading/trailing spaces
- Case: case-variant categories
- Mixed types: detecting numeric/text/date mixtures
- Date formats: validation via parsing attempts
- Numeric strings: detect numerics stored as text

## Validation Rules

Supported: required, min/max (numeric), categorical allowed values, string length, regex pattern, uniqueness.

## Quality Score Formula

Default weights:
- Completeness: 35%
- Uniqueness: 25%
- Validity: 25%
- Consistency: 15%

Score = sum(score_dim * weight_dim) for evaluated dimensions. If validity not evaluated, score reflects available dimensions proportionally.

## Limitations

- IQR/Z-score work best for roughly symmetric distributions
- Ambiguous dates may need explicit format
- Small samples can give unreliable statistics
- Domain knowledge required for appropriate cleaning decisions
