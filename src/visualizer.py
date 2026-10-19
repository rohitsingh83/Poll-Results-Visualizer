"""
src/visualizer.py
Generates publication-quality visualizations for the Poll Results Visualizer project:
1. Bar Chart - Vote Counts & Share (%) per Preferred Tool
2. Pie & Donut Chart - Overall Vote Share & Recommendation Split
3. Regional Stacked Chart - Region-wise Tool Preference Comparison
4. Demographic Comparison Chart - Age Group & Gender Preferences
5. Daily Submissions Trend Line Plot - Responses Over Time
6. Satisfaction Rating Histogram + KDE - Likert Scale (1-5) Distribution
7. Feedback Length vs. Satisfaction Boxplot - Text Engagement by Rating
8. Feedback Word Cloud - Prominent Keywords in Open-Ended Responses
9. Executive Multi-Panel Summary Dashboard Image
"""

import os
from typing import List
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud, STOPWORDS


# Consistent professional color palette
PALETTE_MAIN = ["#2563EB", "#0D9488", "#7C3AED", "#EA580C", "#D97706", "#DC2626"]
TOOL_COLORS = {
    "Python": "#2563EB",
    "Power BI": "#0D9488",
    "SQL": "#7C3AED",
    "Excel": "#EA580C",
    "Tableau": "#D97706",
    "R": "#DC2626",
}


def setup_plot_style() -> None:
    """Configure clean, publication-grade Matplotlib & Seaborn aesthetics."""
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
    plt.rcParams["axes.edgecolor"] = "#CBD5E1"
    plt.rcParams["axes.linewidth"] = 0.8
    plt.rcParams["figure.dpi"] = 150


def plot_preferred_tool_bar(df: pd.DataFrame, out_path: str) -> str:
    """1. Bar Chart – Count & Percentage of Votes per Tool."""
    setup_plot_style()
    counts = df["Preferred Tool"].value_counts()
    pcts = df["Preferred Tool"].value_counts(normalize=True) * 100

    fig, ax = plt.subplots(figsize=(9, 5.2))
    colors = [TOOL_COLORS.get(t, "#2563EB") for t in counts.index]
    bars = ax.bar(counts.index, counts.values, color=colors, edgecolor="#1E293B", linewidth=0.6, width=0.62)

    for bar, count, pct in zip(bars, counts.values, pcts.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height() + max(counts.values) * 0.02,
            f"{count} votes\n({pct:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold",
            color="#0F172A",
        )

    ax.set_title("Poll Results: Most Preferred Data Analysis & Visualization Tools", fontsize=13.5, fontweight="bold", pad=16)
    ax.set_xlabel("Preferred Tool (Poll Option)", fontsize=11, fontweight="bold", labelpad=8)
    ax.set_ylabel("Number of Votes", fontsize=11, fontweight="bold", labelpad=8)
    ax.set_ylim(0, max(counts.values) * 1.18)
    ax.grid(axis="x")
    plt.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    return out_path


def plot_vote_share_pie_donut(df: pd.DataFrame, out_path: str) -> str:
    """2. Pie Chart (Option Vote Share) & Donut Chart (Would Recommend Yes/No)."""
    setup_plot_style()
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.2))

    # Left: Pie Chart of Preferred Tool Share
    counts = df["Preferred Tool"].value_counts()
    colors = [TOOL_COLORS.get(t, "#2563EB") for t in counts.index]
    explode = [0.05 if i == 0 else 0.0 for i in range(len(counts))]

    wedges, texts, autotexts = axes[0].pie(
        counts.values,
        labels=counts.index,
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        explode=explode,
        pctdistance=0.75,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
    )
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontweight("bold")
        autotext.set_fontsize(9.5)
    axes[0].set_title("Option Vote Share Distribution (%)", fontsize=12.5, fontweight="bold")

    # Right: Donut Chart of Binary Recommendation ("Yes" vs "No")
    rec_counts = df["Recommend"].value_counts()
    rec_colors = ["#10B981" if lbl == "Yes" else "#EF4444" for lbl in rec_counts.index]
    wedges2, texts2, autotexts2 = axes[1].pie(
        rec_counts.values,
        labels=[f"Recommend: {lbl}\n({val} votes)" for lbl, val in zip(rec_counts.index, rec_counts.values)],
        autopct="%1.1f%%",
        startangle=90,
        colors=rec_colors,
        pctdistance=0.76,
        wedgeprops={"width": 0.45, "edgecolor": "white", "linewidth": 2},
    )
    for autotext in autotexts2:
        autotext.set_color("white")
        autotext.set_fontweight("bold")
        autotext.set_fontsize(10)
    axes[1].set_title("Would You Recommend This Tool? (Donut Chart)", fontsize=12.5, fontweight="bold")

    plt.suptitle("Poll Share & Binary Recommendation Breakdown", fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_regional_stacked(df: pd.DataFrame, out_path: str) -> str:
    """3. Region-Wise 100% Stacked Bar Chart of Tool Preferences."""
    setup_plot_style()
    ct_pct = pd.crosstab(df["Region"], df["Preferred Tool"], normalize="index") * 100
    ordered_tools = [t for t in ["Python", "Power BI", "SQL", "Excel", "Tableau", "R"] if t in ct_pct.columns]
    ct_pct = ct_pct[ordered_tools]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    bottom = np.zeros(len(ct_pct))
    x = np.arange(len(ct_pct.index))

    for tool in ordered_tools:
        values = ct_pct[tool].values
        bars = ax.bar(
            x,
            values,
            bottom=bottom,
            label=tool,
            color=TOOL_COLORS.get(tool, "#2563EB"),
            edgecolor="white",
            linewidth=1,
            width=0.58,
        )
        for i, val in enumerate(values):
            if val >= 8.0:
                ax.text(
                    x[i],
                    bottom[i] + val / 2.0,
                    f"{val:.1f}%",
                    ha="center",
                    va="center",
                    color="white",
                    fontsize=8.5,
                    fontweight="bold",
                )
        bottom += values

    ax.set_xticks(x)
    ax.set_xticklabels(ct_pct.index, fontsize=10.5, fontweight="bold")
    ax.set_ylabel("Percentage of Regional Votes (%)", fontsize=11, fontweight="bold")
    ax.set_xlabel("Geographic Region", fontsize=11, fontweight="bold")
    ax.set_title("Region-Wise Poll Preference Share (100% Stacked Bar Chart)", fontsize=13, fontweight="bold", pad=15)
    ax.set_ylim(0, 105)
    ax.legend(title="Preferred Tool", bbox_to_anchor=(1.01, 1), loc="upper left", frameon=True)
    ax.grid(axis="x")
    plt.tight_layout()
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_demographic_comparison(df: pd.DataFrame, out_path: str) -> str:
    """4. Demographic Comparison Chart (Age Group & Gender Breakdown)."""
    setup_plot_style()
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.2))

    age_order = [a for a in ["18-24", "25-34", "35-44", "45-54", "55+"] if a in df["Age Group"].unique()]
    tool_order = [t for t in ["Python", "Power BI", "SQL", "Excel", "Tableau", "R"] if t in df["Preferred Tool"].unique()]

    sns.countplot(
        data=df,
        x="Age Group",
        hue="Preferred Tool",
        order=age_order,
        hue_order=tool_order,
        palette=TOOL_COLORS,
        ax=axes[0],
        edgecolor="#1E293B",
        linewidth=0.5,
    )
    axes[0].set_title("Tool Preferences by Age Group", fontsize=12.5, fontweight="bold")
    axes[0].set_xlabel("Respondent Age Cohort", fontsize=10.5, fontweight="bold")
    axes[0].set_ylabel("Number of Votes", fontsize=10.5, fontweight="bold")
    axes[0].legend(title="Tool", fontsize=8.5, title_fontsize=9)

    sns.countplot(
        data=df,
        x="Preferred Tool",
        hue="Gender",
        order=tool_order,
        palette=["#3B82F6", "#EC4899", "#8B5CF6"],
        ax=axes[1],
        edgecolor="#1E293B",
        linewidth=0.5,
    )
    axes[1].set_title("Tool Preferences by Gender", fontsize=12.5, fontweight="bold")
    axes[1].set_xlabel("Preferred Tool", fontsize=10.5, fontweight="bold")
    axes[1].set_ylabel("Number of Votes", fontsize=10.5, fontweight="bold")
    axes[1].legend(title="Gender", fontsize=8.5, title_fontsize=9)

    plt.suptitle("Demographic Cross-Section Analysis (Age Group & Gender)", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_daily_submissions_trend(df: pd.DataFrame, out_path: str) -> str:
    """5. Line Plot – Number of Poll Submissions per Day with Rolling Mean."""
    setup_plot_style()
    daily = df.groupby("Date").size().reset_index(name="Submissions")
    daily["Date_dt"] = pd.to_datetime(daily["Date"])
    daily = daily.sort_values("Date_dt")
    daily["Rolling_5D"] = daily["Submissions"].rolling(window=5, min_periods=1).mean()

    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    ax.plot(
        daily["Date_dt"],
        daily["Submissions"],
        marker="o",
        color="#2563EB",
        linewidth=2.0,
        markersize=5.5,
        label="Daily Responses",
    )
    ax.plot(
        daily["Date_dt"],
        daily["Rolling_5D"],
        linestyle="--",
        color="#EA580C",
        linewidth=2.2,
        label="5-Day Rolling Average",
    )
    ax.fill_between(daily["Date_dt"], daily["Submissions"], color="#2563EB", alpha=0.12)

    # Annotate peak day
    peak_idx = daily["Submissions"].idxmax()
    peak_row = daily.loc[peak_idx]
    ax.annotate(
        f"Peak: {peak_row['Submissions']} votes\n({peak_row['Date']})",
        xy=(peak_row["Date_dt"], peak_row["Submissions"]),
        xytext=(peak_row["Date_dt"], peak_row["Submissions"] + 4),
        ha="center",
        fontsize=9,
        fontweight="bold",
        color="#1E293B",
        arrowprops={"arrowstyle": "->", "color": "#DC2626", "lw": 1.2},
    )

    ax.set_title("Daily Poll Submissions Trend Over 30-Day Survey Window", fontsize=13, fontweight="bold", pad=14)
    ax.set_xlabel("Date", fontsize=11, fontweight="bold")
    ax.set_ylabel("Number of Responses", fontsize=11, fontweight="bold")
    ax.set_ylim(0, daily["Submissions"].max() + 9)
    ax.legend(loc="upper right", frameon=True)
    plt.xticks(rotation=30)
    plt.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    return out_path


def plot_satisfaction_distribution(df: pd.DataFrame, out_path: str) -> str:
    """6. Histogram + KDE – Satisfaction Ratings (1-5) Distribution."""
    setup_plot_style()
    fig, ax = plt.subplots(figsize=(8, 4.8))

    sns.histplot(
        df["Satisfaction (1-5)"],
        bins=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5],
        kde=True,
        color="#0284C7",
        edgecolor="#0F172A",
        alpha=0.75,
        ax=ax,
    )
    mean_val = df["Satisfaction (1-5)"].mean()
    ax.axvline(mean_val, color="#DC2626", linestyle="--", linewidth=2.2, label=f"Mean Rating: {mean_val:.2f} / 5.0")

    rating_counts = df["Satisfaction (1-5)"].value_counts().sort_index()
    for rating, count in rating_counts.items():
        pct = count / len(df) * 100
        ax.text(
            rating,
            count + max(rating_counts.values) * 0.02,
            f"{count} ({pct:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold",
        )

    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_xticklabels(["1 (Very Low)", "2 (Low)", "3 (Neutral)", "4 (High)", "5 (Very High)"])
    ax.set_ylim(0, max(rating_counts.values) * 1.18)
    ax.set_title("Respondent Satisfaction Rating Distribution (1–5 Likert Scale)", fontsize=13, fontweight="bold", pad=14)
    ax.set_xlabel("Satisfaction Rating", fontsize=11, fontweight="bold")
    ax.set_ylabel("Frequency (Number of Respondents)", fontsize=11, fontweight="bold")
    ax.legend(loc="upper left", frameon=True)
    plt.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    return out_path


def plot_feedback_boxplot(df: pd.DataFrame, out_path: str) -> str:
    """7. Boxplot – Feedback Length vs. Satisfaction Level."""
    setup_plot_style()
    fig, ax = plt.subplots(figsize=(8.5, 5))

    sns.boxplot(
        x="Satisfaction (1-5)",
        y="Feedback Length",
        hue="Satisfaction (1-5)",
        data=df,
        palette="coolwarm",
        legend=False,
        width=0.5,
        ax=ax,
    )
    sns.stripplot(
        x="Satisfaction (1-5)",
        y="Feedback Length",
        data=df,
        color="#1E293B",
        alpha=0.25,
        size=4,
        jitter=0.18,
        ax=ax,
    )

    ax.set_title("Open-Ended Feedback Character Length by Satisfaction Level", fontsize=13, fontweight="bold", pad=14)
    ax.set_xlabel("Satisfaction Rating (1 to 5)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Feedback Length (Characters)", fontsize=11, fontweight="bold")
    plt.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    return out_path


def plot_feedback_wordcloud(df: pd.DataFrame, out_path: str) -> str:
    """8. Word Cloud – Common Keywords in Open-Ended Feedback."""
    setup_plot_style()
    text = " ".join(df["Feedback"].dropna().astype(str).tolist())
    custom_stopwords = set(STOPWORDS).union({"tool", "user", "region", "data", "overall"})

    wc = WordCloud(
        width=1000,
        height=480,
        background_color="white",
        colormap="viridis",
        stopwords=custom_stopwords,
        max_words=90,
        random_state=42,
    ).generate(text)

    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("Common Themes & Keywords in Respondent Feedback (Word Cloud)", fontsize=13.5, fontweight="bold", pad=14)
    plt.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    return out_path


def plot_executive_dashboard_summary(df: pd.DataFrame, out_path: str) -> str:
    """9. 4-Panel Executive Dashboard Summary Image for README & Presentations."""
    setup_plot_style()
    fig, axes = plt.subplots(2, 2, figsize=(14, 9.5))

    # Panel 1: Bar Chart of Tool Votes
    counts = df["Preferred Tool"].value_counts()
    colors = [TOOL_COLORS.get(t, "#2563EB") for t in counts.index]
    axes[0, 0].bar(counts.index, counts.values, color=colors, edgecolor="#1E293B")
    for idx, (tool, val) in enumerate(counts.items()):
        pct = val / len(df) * 100
        axes[0, 0].text(idx, val + 3, f"{val} ({pct:.1f}%)", ha="center", fontsize=8.5, fontweight="bold")
    axes[0, 0].set_title("1. Vote Count & Share by Preferred Tool", fontsize=11.5, fontweight="bold")
    axes[0, 0].set_ylabel("Votes")
    axes[0, 0].set_ylim(0, counts.max() * 1.16)

    # Panel 2: Regional Stacked Breakdown
    ct_pct = pd.crosstab(df["Region"], df["Preferred Tool"], normalize="index") * 100
    ordered_tools = [t for t in ["Python", "Power BI", "SQL", "Excel", "Tableau", "R"] if t in ct_pct.columns]
    ct_pct[ordered_tools].plot(
        kind="bar",
        stacked=True,
        color=[TOOL_COLORS[t] for t in ordered_tools],
        ax=axes[0, 1],
        edgecolor="white",
    )
    axes[0, 1].set_title("2. Regional Preference Share (%)", fontsize=11.5, fontweight="bold")
    axes[0, 1].set_ylabel("Share (%)")
    axes[0, 1].tick_params(axis="x", rotation=0)
    axes[0, 1].legend(title="Tool", fontsize=8, bbox_to_anchor=(1.0, 1.0))

    # Panel 3: Satisfaction Distribution
    sns.countplot(
        x="Satisfaction (1-5)",
        hue="Satisfaction (1-5)",
        data=df,
        palette="Blues_d",
        legend=False,
        ax=axes[1, 0],
    )
    axes[1, 0].set_title(
        f"3. Satisfaction Ratings (Mean: {df['Satisfaction (1-5)'].mean():.2f}/5.0)",
        fontsize=11.5,
        fontweight="bold",
    )
    axes[1, 0].set_xlabel("Satisfaction Score (1-5)")
    axes[1, 0].set_ylabel("Respondents")

    # Panel 4: Daily Submissions Trend
    daily = df.groupby("Date").size()
    axes[1, 1].plot(range(len(daily)), daily.values, marker="o", color="#0D9488", linewidth=2)
    axes[1, 1].fill_between(range(len(daily)), daily.values, color="#0D9488", alpha=0.15)
    axes[1, 1].set_title("4. Daily Poll Response Velocity (30 Days)", fontsize=11.5, fontweight="bold")
    axes[1, 1].set_xlabel("Survey Day Index (Day 1 to Day 30)")
    axes[1, 1].set_ylabel("Submissions")

    plt.suptitle(
        f"Poll Results Visualizer — Executive Analytics Snapshot (N = {len(df)} Validated Responses)",
        fontsize=15,
        fontweight="bold",
        y=1.01,
    )
    plt.tight_layout()
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out_path


def generate_all_charts(df: pd.DataFrame, image_dir: str = "images") -> List[str]:
    """Generate all 9 charts and save them to image_dir."""
    os.makedirs(image_dir, exist_ok=True)
    generated = [
        plot_preferred_tool_bar(df, os.path.join(image_dir, "01_preferred_tool_bar_chart.png")),
        plot_vote_share_pie_donut(df, os.path.join(image_dir, "02_vote_share_pie_donut.png")),
        plot_regional_stacked(df, os.path.join(image_dir, "03_regional_preference_stacked.png")),
        plot_demographic_comparison(df, os.path.join(image_dir, "04_demographic_age_gender_chart.png")),
        plot_daily_submissions_trend(df, os.path.join(image_dir, "05_daily_submissions_trend.png")),
        plot_satisfaction_distribution(df, os.path.join(image_dir, "06_satisfaction_distribution.png")),
        plot_feedback_boxplot(df, os.path.join(image_dir, "07_feedback_length_vs_satisfaction_boxplot.png")),
        plot_feedback_wordcloud(df, os.path.join(image_dir, "08_feedback_wordcloud.png")),
        plot_executive_dashboard_summary(df, os.path.join(image_dir, "09_executive_dashboard_summary.png")),
    ]
    return generated


if __name__ == "__main__":
    df_clean = pd.read_csv("data/cleaned_poll_data.csv")
    paths = generate_all_charts(df_clean)
    print(f"Generated {len(paths)} charts:", paths)
