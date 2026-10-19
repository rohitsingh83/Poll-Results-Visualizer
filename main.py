"""
main.py
Poll Results Visualizer — End-to-End Automated Pipeline Runner

Executes all project phases sequentially:
  Phase 1 & 2: Synthetic Poll Dataset Generation & Inspection
  Phase 3:     Data Cleaning, Standardization & Feature Engineering
  Phase 4 & 5: Statistical Aggregation, Vote Share & Cross-Tab Analysis
  Phase 6:     Multi-Chart Visualization Generation (9 PNG Charts)
  Phase 7:     Automated Executive Insights Report Generation
"""

import os
import sys
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


from src.data_generator import generate_synthetic_poll_data
from src.data_cleaner import clean_poll_data
from src.analyzer import generate_executive_insights
from src.visualizer import generate_all_charts


def run_pipeline() -> None:
    print("=" * 78)
    print("📊 POLL RESULTS VISUALIZER — END-TO-END ANALYTICS PIPELINE")
    print("=" * 78)

    # -------------------------------------------------------------------------
    # STEP 1: Generate or Load Raw Poll Dataset
    # -------------------------------------------------------------------------
    raw_csv_path = "data/poll_data.csv"
    clean_csv_path = "data/cleaned_poll_data.csv"

    print("\n[Phase 2] Generating synthetic poll dataset with realistic survey noise...")
    df_raw = generate_synthetic_poll_data(output_path=raw_csv_path)
    print(f"✅ Raw dataset saved to '{raw_csv_path}' ({len(df_raw)} total rows)")

    print("\n🔍 Raw Dataset Preview (First 5 Rows):")
    print(df_raw.head().to_string(index=False))

    print("\n❓ Missing Values in Raw Dataset:")
    print(df_raw.isnull().sum().to_string())

    print("\n🧾 Raw Unique Poll Options (Before Standardization):")
    print(df_raw["Preferred Tool"].dropna().unique())

    # -------------------------------------------------------------------------
    # STEP 2: Clean & Preprocess Poll Data
    # -------------------------------------------------------------------------
    print("\n" + "-" * 78)
    print("[Phase 3] Cleaning & Preprocessing Poll Data...")
    df_clean, cleaning_stats = clean_poll_data(
        input_path=raw_csv_path,
        output_path=clean_csv_path,
    )
    print(f"✅ Cleaned dataset saved to '{clean_csv_path}'")
    for k, v in cleaning_stats.items():
        print(f"   • {k}: {v}")

    print("\n🧾 Standardized Unique Poll Options (After Cleanup):")
    print(df_clean["Preferred Tool"].unique())

    # -------------------------------------------------------------------------
    # STEP 3: Statistical Analysis & Automated Insights
    # -------------------------------------------------------------------------
    print("\n" + "-" * 78)
    print("[Phase 4 & 5] Computing Vote Shares, Regional Cross-Tabs & Executive Insights...")
    insights = generate_executive_insights(df_clean, cleaning_stats, output_dir="outputs")

    print("\n📈 Option-Wise Vote Share Summary Table:")
    print(insights["vote_summary"].to_string(index=False))

    print("\n🌍 Regional Breakdown Summary Table:")
    reg_cols = [
        "Region",
        "Total_Responses",
        "Region_Share_Pct",
        "Leading_Tool",
        "Leading_Tool_Votes",
        "Leading_Tool_Share_Pct",
        "Region_Avg_Satisfaction",
    ]
    print(insights["regional_summary"][reg_cols].to_string(index=False))

    # -------------------------------------------------------------------------
    # STEP 4: Generate All Visualizations
    # -------------------------------------------------------------------------
    print("\n" + "-" * 78)
    print("[Phase 6] Generating 9 Publication-Quality Charts in 'images/'...")
    chart_paths = generate_all_charts(df_clean, image_dir="images")
    for idx, path in enumerate(chart_paths, 1):
        print(f"   [{idx}/9] Saved chart -> {path}")

    # -------------------------------------------------------------------------
    # STEP 5: Print Headline Executive Insights
    # -------------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("💡 HEADLINE EXECUTIVE INSIGHTS")
    print("=" * 78)
    print(
        f"🏆 Winning Option      : {insights['winner_tool']} "
        f"({insights['winner_votes']} votes | {insights['winner_pct']}% share)"
    )
    print(
        f"🥈 Runner-Up Option    : {insights['runner_up_tool']} "
        f"({insights['runner_up_votes']} votes | {insights['runner_up_pct']}% share)"
    )
    print(
        f"📊 Victory Margin      : +{insights['lead_margin_votes']} votes "
        f"(+{insights['lead_margin_pct']}% lead)"
    )
    print(f"⭐ Mean Satisfaction   : {insights['overall_satisfaction']} / 5.00")
    print(f"👍 Recommend Rate (Yes): {insights['overall_recommend_pct']}%")
    print(
        f"📅 Peak Response Day   : {insights['peak_date']} "
        f"({insights['peak_date_count']} submissions)"
    )
    print(f"📄 Full Report Saved   : {insights['report_path']}")
    print("=" * 78)
    print("🚀 Run `streamlit run app.py` to launch the interactive web dashboard!")


if __name__ == "__main__":
    run_pipeline()
