import streamlit as st
import pandas as pd

from cleaner import (
    load_csv,
    profile_data,
    clean_column_names,
    remove_empty_rows_columns,
    missing_value_report,
    fill_missing_values,
    remove_duplicate_rows,
    convert_numeric_columns,
    convert_date_columns,
    clean_text_whitespace,
    convert_empty_strings_to_nan,
    standardize_missing_values,
    find_out_of_range_values,
    replace_out_of_range_values,
    find_invalid_categories,
    normalize_text_case,
    find_outliers
)


st.title("DataClean")
st.write(
    "Clean, validate, analyze, and download your CSV data."
)

st.header("Upload your dataset")


uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["csv"]
)


if uploaded_file is not None:

    try:

        
         # Load CSV
        if (
            "df" not in st.session_state
            or st.session_state.get("uploaded_file_name")
            != uploaded_file.name
        ):

            df = load_csv(uploaded_file)

            # Initial preprocessing
            df = clean_column_names(df)
            df = remove_empty_rows_columns(df)
            df = clean_text_whitespace(df)
            df = convert_empty_strings_to_nan(df)
            df = standardize_missing_values(df)
            df = convert_numeric_columns(df)
            df = convert_date_columns(df)

            st.session_state["original_df"] = df.copy()

            st.session_state["df"] = df
            st.session_state["uploaded_file_name"] = uploaded_file.name

        df = st.session_state["df"]
        if "cleaning_log" not in st.session_state:
           st.session_state["cleaning_log"] = []

        # Structural cleaning
        df = clean_column_names(df)
        df = remove_empty_rows_columns(df)

        # Text cleaning
        df = clean_text_whitespace(df)
        df = convert_empty_strings_to_nan(df)
        df = standardize_missing_values(df)

        df = convert_numeric_columns(df)
        df = convert_date_columns(df)

        # Dataset profile
        profile = profile_data(df)

        st.success("CSV loaded successfully!")
        st.subheader("Dataset Information")

        st.write("Rows:", profile["rows"])
        st.write("Columns:", profile["columns"])


        # Dataset Profile
        profile_table = pd.DataFrame({
            "Data Type": df.dtypes.astype(str),
            "Missing": df.isna().sum(),
            "Unique": df.nunique()
        })

        st.subheader("Dataset Profile")
        st.dataframe(profile_table)


        # Missing Value Report
        missing_report = missing_value_report(df)

        st.subheader("Missing Value Report")
        st.dataframe(missing_report)


        # Missing Value Cleaning
        st.subheader("Missing Value Cleaning")

        numeric_strategy = st.selectbox(
            "Numeric columns",
            ["median", "mean", "leave_missing"]
        )

        categorical_strategy = st.selectbox(
            "Categorical columns",
            ["mode", "unknown", "leave_missing"]
        )

        if st.button("Clean Missing Values"):

            df = fill_missing_values(
                df,
                numeric_strategy=numeric_strategy,
                categorical_strategy=categorical_strategy
            )
            st.session_state["df"] = df
            st.session_state["cleaning_log"].append(
              f"Missing values cleaned: numeric={numeric_strategy}, "
              f"categorical={categorical_strategy}"
                )

            st.success("Missing values cleaned successfully!")

            updated_report = missing_value_report(df)

            st.subheader("Updated Missing Value Report")
            st.dataframe(updated_report)

            st.subheader("Cleaned Dataset")
            st.dataframe(df)


        # Duplicate Rows
        st.subheader("Duplicate Rows")

        duplicate_count = df.duplicated().sum()

        st.write("Duplicate rows found:", duplicate_count)

        if duplicate_count > 0:

            if st.button("Remove Duplicate Rows"):

                df, removed_duplicates = remove_duplicate_rows(df)
                st.session_state["df"] = df
                st.session_state["cleaning_log"].append(
                     f"Removed {removed_duplicates} duplicate rows."
                  )

                st.success(
                    f"Removed {removed_duplicates} duplicate rows."
                )

                st.dataframe(df)

        else:

            st.success("No duplicate rows found.")

        # Value Validation
        st.subheader("Value Validation")

        numeric_columns = df.select_dtypes(
            include="number"
        ).columns.tolist()

        if numeric_columns:

            selected_column = st.selectbox(
                "Select a numeric column to validate",
                numeric_columns
            )

            minimum = st.number_input(
                "Minimum acceptable value",
                value=0.0
            )

            maximum = st.number_input(
                "Maximum acceptable value",
                value=100.0
            )

            
            if st.button("Check Invalid Values"):

              invalid_values = find_out_of_range_values(
                  df,
                  selected_column,
                  minimum,
                  maximum
              )

              st.session_state["invalid_values"] = invalid_values

              if invalid_values.empty:

                   st.success("No out-of-range values found.")

              else:

                 st.warning(
                      f"Found {len(invalid_values)} out-of-range values."
                   )

                 st.dataframe(invalid_values)


# Replace invalid values
            if (
                "invalid_values" in st.session_state
                 and not st.session_state["invalid_values"].empty
              ):

                 if st.button("Replace Invalid Values with Missing"):

                  df = replace_out_of_range_values(
                     df,
                      selected_column,
                      minimum,
                       maximum
                 )

                  st.session_state["df"] = df
                  st.session_state["cleaning_log"].append(
                     f"Replaced invalid values in '{selected_column}' "
                     f"outside the range {minimum} to {maximum} with missing values."
                       )
                  st.session_state.pop("invalid_values")

                  st.success(
                         "Invalid values were replaced with missing values."
                         )

                  st.dataframe(df)
              

        else:
            st.info("No numeric columns available for validation.")


        # Category Validation
        st.subheader("Category Validation")

        categorical_columns = df.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()

        if categorical_columns:

            selected_category_column = st.selectbox(
                "Select a categorical column",
                categorical_columns
            )

            allowed_values_text = st.text_input(
                "Enter allowed values separated by commas"
            )

            if st.button("Check Invalid Categories"):

                allowed_values = [
                    value.strip()
                    for value in allowed_values_text.split(",")
                    if value.strip()
                ]

                invalid_categories = find_invalid_categories(
                    df,
                    selected_category_column,
                    allowed_values
                )

                if invalid_categories.empty:
                    st.success("No invalid categories found.")

                else:
                    st.warning(
                        f"Found {len(invalid_categories)} invalid values."
                    )

                    st.dataframe(invalid_categories)

        else:
            st.info("No categorical columns available for validation.")   


        # Category Normalization
        st.subheader("Category Normalization")

        text_columns = df.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()

        if text_columns:

            selected_text_column = st.selectbox(
                "Select a text column",
                text_columns
            )

            case = st.selectbox(
                "Select text case",
                ["lower", "upper", "title"]
            )

            if st.button("Normalize Text"):

                df = normalize_text_case(
                    df,
                    selected_text_column,
                    case
                )
                st.session_state["df"] = df
                st.session_state["cleaning_log"].append(
                   f"Normalized '{selected_text_column}' to {case} case."
                     )
                st.success(
                    f"Text in '{selected_text_column}' "
                    f"was normalized to {case} case."
                )

                st.dataframe(df)

        else:
            st.info("No text columns available for normalization.") 


        # Outlier Detection
        st.subheader("Outlier Detection")

        numeric_columns = df.select_dtypes(
            include="number"
        ).columns.tolist()

        if numeric_columns:

            selected_outlier_column = st.selectbox(
                "Select a numeric column for outlier detection",
                numeric_columns
            )

            if st.button("Find Outliers"):

                outliers, Q1, Q3, IQR, lower_bound, upper_bound = find_outliers(
                    df,
                    selected_outlier_column
                )
                st.write("Q1:", Q1)
                st.write("Q3:", Q3)
                st.write("IQR:", IQR)
                st.write("Lower Boundary:", lower_bound)
                st.write("Upper Boundary:", upper_bound)

                if outliers.empty:

                    st.success(
                        "No potential outliers found."
                    )

                else:

                    st.warning(
                        f"Found {len(outliers)} potential outliers."
                    )

                    st.dataframe(outliers)

        else:

            st.info(
                "No numeric columns available for outlier detection."
            )
        # Cleaning Log
        st.subheader("Cleaning Log")

        if st.session_state["cleaning_log"]:

            for log in st.session_state["cleaning_log"]:
                st.write("✓", log)

        else:

            st.info("No cleaning operations performed yet.")   

         # Current Cleaned Dataset
        st.subheader("Current Cleaned Dataset")

        st.dataframe(
            st.session_state["df"],
            use_container_width=True
        )

        # Data Quality Summary
        st.subheader("Data Quality Summary")

        original_df = st.session_state["original_df"]
        current_df = st.session_state["df"]

        summary = pd.DataFrame({
            "Metric": [
                "Rows",
                "Columns",
                "Missing Values",
                "Duplicate Rows"
            ],
            "Before": [
                len(original_df),
                len(original_df.columns),
                original_df.isna().sum().sum(),
                original_df.duplicated().sum()
            ],
            "After": [
                len(current_df),
                len(current_df.columns),
                current_df.isna().sum().sum(),
                current_df.duplicated().sum()
            ]
        })

        st.dataframe(summary, hide_index=True)


        # Download Cleaned CSV
        st.subheader("Download")

        cleaned_csv = current_df.to_csv(index=False)

        st.download_button(
            label="Download Cleaned CSV",
            data=cleaned_csv,
            file_name="cleaned_data.csv",
            mime="text/csv"
        )


        # Download Cleaning Report
        cleaning_report = "\n".join(
            f"- {log}"
            for log in st.session_state["cleaning_log"]
        )

        st.download_button(
            label="Download Cleaning Report",
            data=cleaning_report,
            file_name="cleaning_report.txt",
            mime="text/plain"
        )

        # Reset Dataset
        if st.button("Reset Dataset"):

            if "original_df" in st.session_state:
                st.session_state["df"] = st.session_state["original_df"].copy()

            st.session_state["cleaning_log"] = []

            if "invalid_values" in st.session_state:
                st.session_state.pop("invalid_values")

            st.success("Dataset has been reset.")

    except ValueError as e:

        st.error(str(e))