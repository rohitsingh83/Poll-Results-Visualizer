"""
src/data_cleaner.py
Cleans and preprocesses raw poll data:
1. Removes duplicate submissions
2. Handles missing values in critical fields
3. Standardizes categorical text responses (strips whitespace, normalizes casing)
4. Converts data types (numeric Likert scale, datetime Timestamp)
5. Engineers analytical features (Date, Day of Week, Feedback Length, Word Count, Sentiment)
6. Exports cleaned dataset to data/cleaned_poll_data.csv
"""

import os
from typing import Dict, Tuple
import pandas as pd


CANONICAL_TOOL_MAP = {
    "Python": "Python",
    "Power Bi": "Power BI",
    "Sql": "SQL",
    "Excel": "Excel",
    "Tableau": "Tableau",
    "R": "R",
}


def classify_feedback_sentiment(row: pd.Series) -> str:
    """Classify feedback sentiment using rating + keyword heuristics."""
    rating = row.get("Satisfaction (1-5)", 3)
    text = str(row.get("Feedback", "")).lower()

    positive_words = ["great", "super", "excellent", "best", "love", "helpful", "intuitive", "strong", "reliable"]
    negative_words = ["difficult", "frustrating", "crashes", "steep", "slow", "complicated"]

    if rating >= 4 or any(w in text for w in positive_words):
        if rating <= 2 or any(w in text for w in negative_words):
            return "Neutral"
        return "Positive"
    elif rating <= 2 or any(w in text for w in negative_words):
        return "Constructive / Negative"
    return "Neutral"


def clean_poll_data(
    input_path: str = "data/poll_data.csv",
    output_path: str = "data/cleaned_poll_data.csv",
) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Execute the complete Step 4 data cleaning and preprocessing pipeline.

    Returns
    -------
    Tuple[pd.DataFrame, Dict[str, int]]
        Cleaned DataFrame and a summary dictionary of cleaning metrics.
    """
    df_raw = pd.read_csv(input_path)
    initial_rows = len(df_raw)
    initial_missing = int(df_raw.isnull().sum().sum())
    unique_tools_before = df_raw["Preferred Tool"].dropna().nunique()

    # Step 1: Remove duplicate entries
    df = df_raw.drop_duplicates().copy()
    duplicates_removed = initial_rows - len(df)

    # Step 2: Handle missing values in critical columns
    before_drop_na = len(df)
    df = df.dropna(subset=["Preferred Tool", "Satisfaction (1-5)"]).copy()
    missing_rows_dropped = before_drop_na - len(df)

    # Fill any missing open-ended feedback with a clean default string
    df["Feedback"] = df["Feedback"].fillna("No additional comment provided.")

    # Step 3: Standardize categorical responses
    df["Preferred Tool"] = (
        df["Preferred Tool"]
        .astype(str)
        .str.strip()
        .str.title()
        .replace(CANONICAL_TOOL_MAP)
    )
    df["Region"] = df["Region"].astype(str).str.strip().str.title()
    df["Gender"] = df["Gender"].astype(str).str.strip()
    df["Age Group"] = df["Age Group"].astype(str).str.strip()

    unique_tools_after = df["Preferred Tool"].nunique()

    # Step 4: Convert data types
    df["Satisfaction (1-5)"] = pd.to_numeric(df["Satisfaction (1-5)"], errors="coerce")
    df = df.dropna(subset=["Satisfaction (1-5)"]).copy()
    df["Satisfaction (1-5)"] = df["Satisfaction (1-5)"].astype(int)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    # Step 5: Feature Engineering
    df["Date"] = df["Timestamp"].dt.strftime("%Y-%m-%d")
    df["Day_of_Week"] = df["Timestamp"].dt.day_name()
    df["Feedback Length"] = df["Feedback"].astype(str).apply(len)
    df["Feedback Word Count"] = df["Feedback"].astype(str).apply(lambda s: len(s.split()))
    df["Sentiment"] = df.apply(classify_feedback_sentiment, axis=1)

    # Sort cleanly by Timestamp
    df = df.sort_values("Timestamp").reset_index(drop=True)

    # Step 6: Save cleaned dataset
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    audit_stats = {
        "initial_rows": initial_rows,
        "duplicates_removed": duplicates_removed,
        "missing_rows_dropped": missing_rows_dropped,
        "final_clean_rows": len(df),
        "initial_missing_cells": initial_missing,
        "final_missing_cells": int(df.isnull().sum().sum()),
        "unique_tools_before_standardization": unique_tools_before,
        "unique_tools_after_standardization": unique_tools_after,
    }

    return df, audit_stats


if __name__ == "__main__":
    cleaned_df, stats = clean_poll_data()
    print("Cleaning Audit Summary:", stats)
