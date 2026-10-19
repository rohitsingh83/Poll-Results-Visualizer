"""
app.py
Poll Results Visualizer — Interactive Streamlit Web Dashboard (Step 6)
Launch command: streamlit run app.py
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st
from wordcloud import WordCloud, STOPWORDS

from src.data_generator import generate_synthetic_poll_data
from src.data_cleaner import clean_poll_data
from src.analyzer import (
    compute_vote_share_summary,
    compute_regional_breakdown,
    compute_demographic_breakdown,
)

st.set_page_config(
    page_title="Poll Results Visualizer | Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

TOOL_COLORS = {
    "Python": "#2563EB",
    "Power BI": "#0D9488",
    "SQL": "#7C3AED",
    "Excel": "#EA580C",
    "Tableau": "#D97706",
    "R": "#DC2626",
}


@st.cache_data
def load_default_data() -> pd.DataFrame:
    """Load cleaned poll data, generating it first if not present."""
    clean_path = "data/cleaned_poll_data.csv"
    raw_path = "data/poll_data.csv"
    if not os.path.exists(clean_path):
        if not os.path.exists(raw_path):
            generate_synthetic_poll_data(output_path=raw_path)
        clean_poll_data(input_path=raw_path, output_path=clean_path)
    df = pd.read_csv(clean_path)
    return df


def main() -> None:
    # Header Banner
    st.title("📊 Poll Results Visualizer — Interactive Survey & Poll Analytics")
    st.markdown(
        "**Industry-Oriented Survey Data Pipeline:** Ingests poll/survey exports (Google Forms, CSV, or synthetic datasets), "
        "cleans noisy responses, computes vote share percentages, and visualizes multi-dimensional insights."
    )

    # Sidebar Data Source & Filters
    st.sidebar.header("📂 1. Data Source")
    uploaded_file = st.sidebar.file_uploader(
        "Upload Custom Poll CSV (Optional)",
        type=["csv"],
        help="Upload a Google Forms / CSV export with columns like Preferred Tool, Satisfaction (1-5), Region, Age Group, Feedback.",
    )

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        if "Preferred Tool" in df.columns:
            df["Preferred Tool"] = df["Preferred Tool"].astype(str).str.strip().str.title()
        if "Timestamp" in df.columns and "Date" not in df.columns:
            df["Date"] = pd.to_datetime(df["Timestamp"], errors="coerce").dt.strftime("%Y-%m-%d")
        if "Feedback" in df.columns and "Feedback Length" not in df.columns:
            df["Feedback Length"] = df["Feedback"].fillna("").astype(str).apply(len)
        st.sidebar.success(f"Loaded custom file ({len(df)} rows)")
    else:
        df = load_default_data()
        st.sidebar.info(f"Using Cleaned Poll Dataset ({len(df)} validated responses)")

    st.sidebar.markdown("---")
    st.sidebar.header("🔍 2. Filter Poll Responses")

    all_tools = sorted(df["Preferred Tool"].dropna().unique().tolist())
    selected_tools = st.sidebar.multiselect(
        "Select Preferred Tool(s):",
        options=all_tools,
        default=all_tools,
    )

    all_regions = sorted(df["Region"].dropna().unique().tolist()) if "Region" in df.columns else []
    selected_regions = (
        st.sidebar.multiselect("Select Region(s):", options=all_regions, default=all_regions)
        if all_regions
        else []
    )

    all_ages = sorted(df["Age Group"].dropna().unique().tolist()) if "Age Group" in df.columns else []
    selected_ages = (
        st.sidebar.multiselect("Select Age Group(s):", options=all_ages, default=all_ages)
        if all_ages
        else []
    )

    all_genders = sorted(df["Gender"].dropna().unique().tolist()) if "Gender" in df.columns else []
    selected_genders = (
        st.sidebar.multiselect("Select Gender(s):", options=all_genders, default=all_genders)
        if all_genders
        else []
    )

    min_sat, max_sat = st.sidebar.slider(
        "Satisfaction Rating Range (1–5):",
        min_value=1,
        max_value=5,
        value=(1, 5),
    )

    # Apply Filters
    filtered_df = df[df["Preferred Tool"].isin(selected_tools)].copy()
    if all_regions:
        filtered_df = filtered_df[filtered_df["Region"].isin(selected_regions)]
    if all_ages:
        filtered_df = filtered_df[filtered_df["Age Group"].isin(selected_ages)]
    if all_genders:
        filtered_df = filtered_df[filtered_df["Gender"].isin(selected_genders)]
    filtered_df = filtered_df[
        (filtered_df["Satisfaction (1-5)"] >= min_sat)
        & (filtered_df["Satisfaction (1-5)"] <= max_sat)
    ]

    if filtered_df.empty:
        st.warning("No poll responses match the selected filter criteria. Please broaden your sidebar filters.")
        return

    # -------------------------------------------------------------------------
    # Executive KPI Cards
    # -------------------------------------------------------------------------
    total_votes = len(filtered_df)
    top_tool_series = filtered_df["Preferred Tool"].value_counts()
    leading_tool = top_tool_series.idxmax()
    leading_votes = int(top_tool_series.max())
    leading_pct = round(leading_votes / total_votes * 100, 1)
    avg_satisfaction = round(float(filtered_df["Satisfaction (1-5)"].mean()), 2)
    rec_rate = (
        round(float((filtered_df["Recommend"] == "Yes").mean() * 100), 1)
        if "Recommend" in filtered_df.columns
        else 0.0
    )
    avg_fb_len = round(float(filtered_df["Feedback Length"].mean()), 1)

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("🗳️ Validated Votes", f"{total_votes:,}", f"{round(total_votes/len(df)*100, 1)}% of total")
    kpi2.metric("🏆 Leading Option", f"{leading_tool}", f"{leading_votes} votes ({leading_pct}%)")
    kpi3.metric("⭐ Avg Satisfaction", f"{avg_satisfaction} / 5.0", "Likert Scale")
    kpi4.metric("👍 Recommend (Yes)", f"{rec_rate}%", "Approval Rate")
    kpi5.metric("💬 Avg Feedback Length", f"{avg_fb_len} chars", "Open-Text Depth")

    st.markdown("---")

    # -------------------------------------------------------------------------
    # Interactive Tabs
    # -------------------------------------------------------------------------
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📊 1. Vote Share & Overview",
            "🌍 2. Regional & Demographics",
            "📈 3. Ratings & Time Trends",
            "☁️ 4. Feedback Word Cloud & NLP",
            "🗃️ 5. Data Explorer & Export",
        ]
    )

    # TAB 1: Vote Share & Overview
    with tab1:
        col_left, col_right = st.columns([1.15, 1])
        vote_summary = compute_vote_share_summary(filtered_df)

        with col_left:
            st.subheader("Tool Preference — Vote Count & Share (%)")
            fig_bar = px.bar(
                vote_summary,
                x="Preferred Tool",
                y="Votes",
                color="Preferred Tool",
                color_discrete_map=TOOL_COLORS,
                text=vote_summary.apply(lambda r: f"{r['Votes']} ({r['Vote_Share_Pct']}%)", axis=1),
                hover_data=["Vote_Share_Pct", "Avg_Satisfaction", "Recommend_Rate_Pct"],
            )
            fig_bar.update_traces(textposition="outside")
            fig_bar.update_layout(
                yaxis_title="Number of Votes",
                xaxis_title="Preferred Tool",
                showlegend=False,
                height=420,
                margin=dict(t=30, b=20),
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_right:
            st.subheader("Percentage Share Distribution (Donut Chart)")
            fig_pie = px.pie(
                vote_summary,
                names="Preferred Tool",
                values="Votes",
                color="Preferred Tool",
                color_discrete_map=TOOL_COLORS,
                hole=0.42,
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            fig_pie.update_layout(height=420, margin=dict(t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)

        st.subheader("📋 Option-Wise Vote Share & Satisfaction Summary Table")
        st.dataframe(vote_summary, use_container_width=True, hide_index=True)

    # TAB 2: Regional & Demographics
    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🌍 Region-Wise Tool Preference (100% Stacked)")
            reg_ct = (
                pd.crosstab(filtered_df["Region"], filtered_df["Preferred Tool"], normalize="index")
                .mul(100)
                .round(1)
                .reset_index()
                .melt(id_vars="Region", var_name="Preferred Tool", value_name="Share_Pct")
            )
            fig_reg = px.bar(
                reg_ct,
                x="Region",
                y="Share_Pct",
                color="Preferred Tool",
                color_discrete_map=TOOL_COLORS,
                text_auto=".1f",
                barmode="stack",
            )
            fig_reg.update_layout(yaxis_title="Regional Vote Share (%)", height=420)
            st.plotly_chart(fig_reg, use_container_width=True)

        with c2:
            st.subheader("👥 Age Cohort vs. Preferred Tool")
            age_ct = (
                filtered_df.groupby(["Age Group", "Preferred Tool"])
                .size()
                .reset_index(name="Votes")
            )
            fig_age = px.bar(
                age_ct,
                x="Age Group",
                y="Votes",
                color="Preferred Tool",
                color_discrete_map=TOOL_COLORS,
                barmode="group",
            )
            fig_age.update_layout(yaxis_title="Votes", height=420)
            st.plotly_chart(fig_age, use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            st.subheader("🚻 Gender Breakdown by Preferred Tool")
            gen_ct = (
                filtered_df.groupby(["Preferred Tool", "Gender"])
                .size()
                .reset_index(name="Votes")
            )
            fig_gen = px.bar(
                gen_ct,
                x="Preferred Tool",
                y="Votes",
                color="Gender",
                barmode="group",
                color_discrete_sequence=["#3B82F6", "#EC4899", "#8B5CF6"],
            )
            fig_gen.update_layout(height=380)
            st.plotly_chart(fig_gen, use_container_width=True)

        with c4:
            st.subheader("💼 Respondent Role Breakdown")
            role_ct = (
                filtered_df.groupby(["Role", "Preferred Tool"])
                .size()
                .reset_index(name="Votes")
            )
            fig_role = px.bar(
                role_ct,
                x="Role",
                y="Votes",
                color="Preferred Tool",
                color_discrete_map=TOOL_COLORS,
                barmode="stack",
            )
            fig_role.update_layout(height=380)
            st.plotly_chart(fig_role, use_container_width=True)

    # TAB 3: Satisfaction Ratings & Time Trends
    with tab3:
        r1, r2 = st.columns(2)
        with r1:
            st.subheader("⭐ Satisfaction Ratings Distribution (Histogram + KDE)")
            fig_sat, ax_sat = plt.subplots(figsize=(7, 4.2))
            sns.histplot(
                filtered_df["Satisfaction (1-5)"],
                bins=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5],
                kde=True,
                color="#0284C7",
                ax=ax_sat,
            )
            ax_sat.axvline(
                filtered_df["Satisfaction (1-5)"].mean(),
                color="#DC2626",
                linestyle="--",
                linewidth=2,
                label=f"Mean: {filtered_df['Satisfaction (1-5)'].mean():.2f}",
            )
            ax_sat.set_xticks([1, 2, 3, 4, 5])
            ax_sat.set_xlabel("Satisfaction Rating (1-5)")
            ax_sat.set_ylabel("Number of Respondents")
            ax_sat.legend()
            plt.tight_layout()
            st.pyplot(fig_sat)

        with r2:
            st.subheader("📦 Feedback Length vs. Satisfaction Rating (Boxplot)")
            fig_box, ax_box = plt.subplots(figsize=(7, 4.2))
            sns.boxplot(
                x="Satisfaction (1-5)",
                y="Feedback Length",
                hue="Satisfaction (1-5)",
                data=filtered_df,
                palette="coolwarm",
                legend=False,
                ax=ax_box,
            )
            ax_box.set_xlabel("Satisfaction Rating (1-5)")
            ax_box.set_ylabel("Feedback Length (Characters)")
            plt.tight_layout()
            st.pyplot(fig_box)

        st.subheader("📅 Daily Poll Submissions Over Time")
        daily = (
            filtered_df.groupby("Date")
            .size()
            .reset_index(name="Responses")
            .sort_values("Date")
        )
        daily["5-Day Rolling Avg"] = daily["Responses"].rolling(5, min_periods=1).mean().round(2)
        fig_line = px.line(
            daily,
            x="Date",
            y=["Responses", "5-Day Rolling Avg"],
            markers=True,
            color_discrete_map={"Responses": "#2563EB", "5-Day Rolling Avg": "#EA580C"},
        )
        fig_line.update_layout(
            yaxis_title="Number of Submissions",
            xaxis_title="Survey Date",
            height=380,
        )
        st.plotly_chart(fig_line, use_container_width=True)

    # TAB 4: Feedback Word Cloud & Sentiment Explorer
    with tab4:
        wc_col, sent_col = st.columns([1.35, 1])
        with wc_col:
            st.subheader("☁️ Open-Ended Feedback Word Cloud")
            text = " ".join(filtered_df["Feedback"].dropna().astype(str).tolist())
            if text.strip():
                stopwords = set(STOPWORDS).union({"tool", "user", "region", "data", "overall"})
                wordcloud = WordCloud(
                    width=850,
                    height=420,
                    background_color="white",
                    colormap="viridis",
                    stopwords=stopwords,
                ).generate(text)
                fig_wc, ax_wc = plt.subplots(figsize=(9, 4.5))
                ax_wc.imshow(wordcloud, interpolation="bilinear")
                ax_wc.axis("off")
                st.pyplot(fig_wc)
            else:
                st.info("No open-ended feedback available for the current selection.")

        with sent_col:
            st.subheader("💬 Feedback Sentiment Breakdown")
            if "Sentiment" in filtered_df.columns:
                sent_counts = filtered_df["Sentiment"].value_counts().reset_index()
                sent_counts.columns = ["Sentiment", "Count"]
                fig_sent = px.pie(
                    sent_counts,
                    names="Sentiment",
                    values="Count",
                    hole=0.45,
                    color="Sentiment",
                    color_discrete_map={
                        "Positive": "#10B981",
                        "Neutral": "#F59E0B",
                        "Constructive / Negative": "#EF4444",
                    },
                )
                fig_sent.update_layout(height=360)
                st.plotly_chart(fig_sent, use_container_width=True)

        st.subheader("🔎 Browse Individual Open-Ended Respondent Comments")
        st.dataframe(
            filtered_df[
                [
                    "Respondent_ID",
                    "Date",
                    "Preferred Tool",
                    "Region",
                    "Age Group",
                    "Satisfaction (1-5)",
                    "Sentiment",
                    "Feedback",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    # TAB 5: Raw & Cleaned Data Explorer + Export
    with tab5:
        st.subheader("🗃️ Filtered Poll Dataset Preview")
        show_raw = st.checkbox("Show Full Filtered Dataset Table", value=True)
        if show_raw:
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)

        dl1, dl2 = st.columns(2)
        with dl1:
            csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download Filtered Poll Data (CSV)",
                data=csv_bytes,
                file_name="filtered_poll_results.csv",
                mime="text/csv",
            )
        with dl2:
            summary_csv = compute_vote_share_summary(filtered_df).to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download Vote Share Summary Table (CSV)",
                data=summary_csv,
                file_name="vote_share_summary.csv",
                mime="text/csv",
            )


if __name__ == "__main__":
    main()
