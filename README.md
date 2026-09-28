# DataClean

DataClean is a Streamlit-based CSV data cleaning and validation application.

It helps users inspect, clean, validate, analyze, and download CSV datasets without writing Python code.

## Features

- CSV file upload
- Dataset profiling
- Missing-value detection
- Missing-value cleaning
- Duplicate-row detection and removal
- Automatic numeric type conversion
- Date type conversion
- Text whitespace cleaning
- Standardization of common missing-value markers
- Numeric range validation
- Invalid-value replacement
- Category validation
- Text case normalization
- IQR-based outlier detection
- Cleaning activity log
- Before-and-after data quality summary
- Cleaned CSV download
- Cleaning report download
- Dataset reset functionality

## Technologies

- Python
- Pandas
- Streamlit

## Project Structure

```text
DataClean/
├── app.py
├── cleaner.py
├── requirements.txt
└── README.md