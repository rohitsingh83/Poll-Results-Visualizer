"""
src/data_generator.py
Generates a realistic synthetic poll dataset simulating a Google Forms / SurveyMonkey export
with intentional real-world data quality issues (duplicates, missing values, casing noise)
so the data cleaning pipeline can be demonstrated authentically.
"""

import os
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd


def generate_synthetic_poll_data(
    output_path: str = "data/poll_data.csv",
    n_clean_rows: int = 500,
    n_duplicates: int = 12,
    n_missing_rows: int = 13,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generate realistic survey/poll responses with demographic, regional, temporal,
    Likert-scale, binary (Yes/No), and open-ended text feedback columns.

    Parameters
    ----------
    output_path : str
        File path where the raw CSV will be saved.
    n_clean_rows : int
        Number of valid base respondent records.
    n_duplicates : int
        Number of accidental double-submission rows to inject.
    n_missing_rows : int
        Number of incomplete rows (missing Preferred Tool or Satisfaction) to inject.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        The raw generated DataFrame (including injected noise).
    """
    np.random.seed(seed)
    random.seed(seed)

    age_groups = ["18-24", "25-34", "35-44", "45-54", "55+"]
    age_weights = [0.34, 0.36, 0.17, 0.09, 0.04]

    genders = ["Female", "Male", "Non-Binary / Prefer not to say"]
    gender_weights = [0.46, 0.49, 0.05]

    regions = ["South", "West", "North", "East", "Central"]
    region_weights = [0.28, 0.24, 0.22, 0.15, 0.11]

    roles = [
        "Student",
        "Data Analyst",
        "Business Analyst",
        "Software Engineer",
        "Research Analyst",
    ]
    role_weights = [0.35, 0.25, 0.18, 0.12, 0.10]

    # Regional & demographic conditional tool preferences to create discoverable insights
    tools = ["Python", "Power BI", "SQL", "Excel", "Tableau", "R"]

    # Open-ended feedback templates grouped by satisfaction level (1-5)
    feedback_templates = {
        5: [
            "Great tool, very useful for automating daily data analysis and interactive dashboards!",
            "Super helpful! Outstanding visualization library support and fast data processing.",
            "Excellent performance on large datasets, community support and documentation are top notch.",
            "Best workflow for end-to-end survey analysis, reporting, and executive storytelling.",
            "Extremely intuitive and powerful; saved our analytics team hours of manual reporting work.",
            "Love the flexibility, clean charts, and seamless integration with modern data pipelines.",
        ],
        4: [
            "Very reliable and practical for weekly reporting, though advanced customization takes practice.",
            "Good balance of speed and visualization quality; great for team collaboration and insights.",
            "Strong tool for data cleaning and dashboarding, would love more built-in survey templates.",
            "Works well for most business analytics tasks and stakeholder presentations.",
            "Helpful and efficient for exploratory data analysis and quick statistical summaries.",
        ],
        3: [
            "Decent features overall, but has a moderate learning curve for beginners.",
            "Average experience; gets the job done but formatting complex charts takes extra time.",
            "Good for basic tables and charts, needs improvement in real-time collaboration features.",
            "Useful for standard reporting, though performance slows down with large CSV files.",
        ],
        2: [
            "Needs improvement in user interface and error messages; setup felt complicated.",
            "Steep learning curve and documentation could be much clearer for new analysts.",
            "Limited customization options without writing extra configuration code; somewhat slow.",
        ],
        1: [
            "Difficult to configure and frequent crashes on older laptops; needs major improvement.",
            "Frustrating experience with data import errors and rigid chart formatting options.",
        ],
    }

    # Base start date (30-day polling window)
    start_date = datetime(2026, 9, 1, 8, 0, 0)
    question_text = "Which primary data analysis & visualization tool do you prefer most?"

    records = []
    for i in range(1, n_clean_rows + 1):
        resp_id = f"RESP-{1000 + i}"
        age = np.random.choice(age_groups, p=age_weights)
        gender = np.random.choice(genders, p=gender_weights)
        region = np.random.choice(regions, p=region_weights)
        role = np.random.choice(roles, p=role_weights)

        # Conditional tool probability based on age & region for realistic patterns
        if age in ["18-24", "25-34"] and region in ["South", "West"]:
            tool_probs = [0.40, 0.20, 0.16, 0.10, 0.09, 0.05]
        elif role == "Business Analyst" or age in ["35-44", "45-54"]:
            tool_probs = [0.22, 0.28, 0.18, 0.17, 0.11, 0.04]
        elif role == "Research Analyst":
            tool_probs = [0.35, 0.12, 0.13, 0.12, 0.10, 0.18]
        else:
            tool_probs = [0.33, 0.21, 0.17, 0.14, 0.10, 0.05]

        tool = np.random.choice(tools, p=tool_probs)

        # Conditional satisfaction score (1 to 5)
        if tool in ["Python", "Power BI"]:
            sat_probs = [0.02, 0.05, 0.15, 0.42, 0.36]
        elif tool in ["SQL", "Tableau"]:
            sat_probs = [0.03, 0.07, 0.20, 0.43, 0.27]
        else:
            sat_probs = [0.05, 0.11, 0.28, 0.36, 0.20]

        satisfaction = int(np.random.choice([1, 2, 3, 4, 5], p=sat_probs))
        recommend = "Yes" if satisfaction >= 4 or (satisfaction == 3 and random.random() < 0.65) else "No"

        # Generate timestamp with realistic campaign spikes (e.g. email reminders on days 5, 14, 22)
        day_offset = int(np.random.choice(
            range(30),
            p=_get_daily_weights(30)
        ))
        hour_offset = int(np.random.choice(range(8, 22)))
        minute_offset = random.randint(0, 59)
        second_offset = random.randint(0, 59)
        ts = start_date + timedelta(
            days=day_offset,
            hours=hour_offset - 8,
            minutes=minute_offset,
            seconds=second_offset,
        )

        # Pick feedback template and personalize slightly
        base_feedback = random.choice(feedback_templates[satisfaction])
        if random.random() < 0.45:
            feedback = f"{base_feedback} ({tool} user in {region} region)."
        else:
            feedback = base_feedback

        # Inject realistic text formatting noise into ~8% of rows (to demonstrate str.strip().str.title())
        noisy_tool = tool
        if random.random() < 0.08:
            noise_variants = {
                "Python": ["  python ", "PYTHON", "python"],
                "Power BI": ["power bi", "  Power Bi ", "POWER BI"],
                "SQL": ["sql", " Sql  ", "SQL "],
                "Excel": ["excel", " EXCEL ", "Excel  "],
                "Tableau": ["tableau", " TABLEAU", "  Tableau"],
                "R": [" r ", "R  "],
            }
            noisy_tool = random.choice(noise_variants[tool])

        records.append(
            {
                "Respondent_ID": resp_id,
                "Timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "Age Group": age,
                "Gender": gender,
                "Region": region,
                "Role": role,
                "Question": question_text,
                "Preferred Tool": noisy_tool,
                "Satisfaction (1-5)": satisfaction,
                "Recommend": recommend,
                "Feedback": feedback,
            }
        )

    # Inject incomplete rows (missing Preferred Tool or Satisfaction)
    for j in range(1, n_missing_rows + 1):
        resp_id = f"RESP-{2000 + j}"
        ts = start_date + timedelta(days=random.randint(0, 29), hours=random.randint(1, 10))
        missing_type = j % 3
        records.append(
            {
                "Respondent_ID": resp_id,
                "Timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "Age Group": random.choice(age_groups),
                "Gender": random.choice(genders),
                "Region": random.choice(regions),
                "Role": random.choice(roles),
                "Question": question_text,
                "Preferred Tool": np.nan if missing_type in (0, 2) else "Python",
                "Satisfaction (1-5)": np.nan if missing_type in (1, 2) else 4,
                "Recommend": "Yes",
                "Feedback": np.nan if missing_type == 2 else "Submitted incomplete form accidentally.",
            }
        )

    # Inject exact duplicate rows (simulating double-click on submit button)
    duplicate_samples = random.sample(records[:n_clean_rows], n_duplicates)
    records.extend(duplicate_samples)

    # Shuffle chronologically by Timestamp
    df_raw = pd.DataFrame(records)
    df_raw = df_raw.sort_values("Timestamp").reset_index(drop=True)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_raw.to_csv(output_path, index=False)
    return df_raw


def _get_daily_weights(n_days: int) -> np.ndarray:
    """Create realistic daily poll submission weights with reminder campaign spikes."""
    weights = np.ones(n_days, dtype=float)
    # Campaign launch & reminder spikes
    for spike_day, boost in [(0, 2.2), (1, 1.9), (6, 2.5), (13, 2.8), (20, 2.4), (27, 2.1)]:
        if spike_day < n_days:
            weights[spike_day] = boost
    return weights / weights.sum()


if __name__ == "__main__":
    df = generate_synthetic_poll_data()
    print(f"Generated raw dataset with {len(df)} rows at data/poll_data.csv")
