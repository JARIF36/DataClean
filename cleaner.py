import pandas as pd
import re

def load_csv(file):
   try: 
    df = pd.read_csv(file)
    if df.empty:
      raise ValueError(f"The csv file is empty")
      
    return df
   except Exception as e:
     raise ValueError(f"Could not Read the CSV file :{e}")
   
def profile_data(df):
    profile = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": df.columns.tolist(),
        "data_types": df.dtypes.astype(str).to_dict(),
        "missing_values": df.isna().sum().to_dict(),
        "duplicate_rows": df.duplicated().sum(),
        "unique_values": df.nunique().to_dict()
    }

    return profile



def clean_column_names(df):
    df = df.copy()

    cleaned_columns = []

    for column in df.columns:
        column = str(column).strip().lower()
        column = re.sub(r"[^a-z0-9]+", "_", column)
        column = column.strip("_")
        cleaned_columns.append(column)

    df.columns = cleaned_columns

    return df

def remove_empty_rows_columns(df):
    df = df.copy()

    # Remove rows where every value is missing
    df = df.dropna(axis=0, how="all")

    # Remove columns where every value is missing
    df = df.dropna(axis=1, how="all")

    return df

def missing_value_report(df):
    missing_count = df.isna().sum()
    missing_percentage = (missing_count / len(df)) * 100

    report = pd.DataFrame({
        "Missing Values": missing_count,
        "Missing Percentage": missing_percentage
    })

    return report

def fill_missing_values(df, numeric_strategy="median", categorical_strategy="mode"):
    df = df.copy()

    numeric_columns = df.select_dtypes(include="number").columns
    categorical_columns = df.select_dtypes(exclude="number").columns

    if numeric_strategy == "mean":
        for column in numeric_columns:
            df[column] = df[column].fillna(df[column].mean())

    elif numeric_strategy == "median":
        for column in numeric_columns:
            df[column] = df[column].fillna(df[column].median())

    if categorical_strategy == "mode":
        for column in categorical_columns:
            mode = df[column].mode()

            if not mode.empty:
                df[column] = df[column].fillna(mode.iloc[0])

    elif categorical_strategy == "unknown":
        for column in categorical_columns:
            df[column] = df[column].fillna("Unknown")

    return df

def remove_duplicate_rows(df):
    df = df.copy()

    duplicate_count = df.duplicated().sum()

    df = df.drop_duplicates()

    return df, duplicate_count

def convert_numeric_columns(df):
    df = df.copy()

    for column in df.columns:

        if df[column].dtype == "object":

            if is_identifier_column(column):
                continue

            converted = pd.to_numeric(
                df[column],
                errors="coerce"
            )

            valid_values = converted.notna().sum()
            original_values = df[column].notna().sum()

            if original_values > 0:
                conversion_rate = valid_values / original_values

                if conversion_rate >= 0.95:
                    df[column] = converted

    return df

def is_identifier_column(column_name):
    identifier_patterns = [
        r"(^|_)id($|_)",
        r"(^|_)code($|_)",
        r"(^|_)phone($|_)",
        r"(^|_)mobile($|_)",
        r"(^|_)zip($|_)",
        r"(^|_)postal($|_)"
    ]

    column_name = str(column_name).lower()

    for pattern in identifier_patterns:
        if re.search(pattern, column_name):
            return True

    return False

def is_date_column(column_name):
    date_keywords = [
        "date",
        "time",
        "created",
        "updated",
        "year",
        "month"
    ]

    column_name = str(column_name).lower()

    for keyword in date_keywords:
        if keyword in column_name:
            return True

    return False

def convert_date_columns(df):
    df = df.copy()

    for column in df.columns:

        if df[column].dtype == "object":

            if is_date_column(column):

                converted = pd.to_datetime(
                    df[column],
                    errors="coerce"
                )

                valid_values = converted.notna().sum()
                original_values = df[column].notna().sum()

                if original_values > 0:
                    conversion_rate = valid_values / original_values

                    if conversion_rate >= 0.95:
                        df[column] = converted

    return df

def clean_text_whitespace(df):
    df = df.copy()

    text_columns = df.select_dtypes(include="object").columns

    for column in text_columns:
        df[column] = df[column].str.strip()

    return df

def convert_empty_strings_to_nan(df):
    df = df.copy()

    text_columns = df.select_dtypes(include="object").columns

    for column in text_columns:
        df[column] = df[column].replace("", pd.NA)

    return df

def standardize_missing_values(df):
    df = df.copy()

    missing_markers = [
        "NA",
        "N/A",
        "na",
        "n/a",
        "NULL",
        "null",
        "None",
        "none"
    ]

    df = df.replace(missing_markers, pd.NA)

    return df

def find_out_of_range_values(df, column, minimum=None, maximum=None):
    invalid_mask = pd.Series(False, index=df.index)

    if minimum is not None:
        invalid_mask = invalid_mask | (df[column] < minimum)

    if maximum is not None:
        invalid_mask = invalid_mask | (df[column] > maximum)

    return df.loc[invalid_mask, [column]]

def replace_out_of_range_values(
    df,
    column,
    minimum=None,
    maximum=None
):
    df = df.copy()

    invalid_mask = pd.Series(False, index=df.index)

    if minimum is not None:
        invalid_mask = invalid_mask | (df[column] < minimum)

    if maximum is not None:
        invalid_mask = invalid_mask | (df[column] > maximum)

    df.loc[invalid_mask, column] = pd.NA

    return df

def find_invalid_categories(df, column, allowed_values):
    invalid_mask = ~df[column].isin(allowed_values)

    return df.loc[invalid_mask, [column]]

def normalize_text_case(df, column, case="lower"):
    df = df.copy()

    if case == "lower":
        df[column] = df[column].str.lower()

    elif case == "upper":
        df[column] = df[column].str.upper()

    elif case == "title":
        df[column] = df[column].str.title()

    return df

def find_outliers(df, column):

    valid_values = df[column].dropna()

    if len(valid_values) < 4:
        raise ValueError(
            f"Not enough valid values in '{column}' "
            "to perform outlier detection."
        )

    if valid_values.nunique() <= 1:
        raise ValueError(
            f"'{column}' does not contain enough variation "
            "to detect outliers."
        )

    Q1 = valid_values.quantile(0.25)
    Q3 = valid_values.quantile(0.75)

    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    outlier_mask = (
        (df[column] < lower_bound) |
        (df[column] > upper_bound)
    )

    outliers = df.loc[outlier_mask, [column]]

    return outliers, Q1, Q3, IQR, lower_bound, upper_bound