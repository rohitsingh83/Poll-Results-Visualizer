"""
generate_docs_site.py
Generates a complete, interactive, standalone single-page web application
in docs/index.html for Poll-Results-Visualizer for GitHub Pages.
"""

import json
import os
import pandas as pd
import numpy as np

# Load datasets
clean_df = pd.read_csv("data/cleaned_poll_data.csv")
vote_summary = pd.read_csv("outputs/vote_share_summary.csv")
reg_summary = pd.read_csv("outputs/regional_breakdown.csv")
demo_summary = pd.read_csv("outputs/demographic_breakdown.csv")

# Regional cross-tab
reg_crosstab = pd.crosstab(clean_df["Region"], clean_df["Preferred Tool"]).reset_index()

# Daily trend
clean_df["Date"] = pd.to_datetime(clean_df["Timestamp"]).dt.date.astype(str)
daily_trend = clean_df.groupby("Date").size().reset_index(name="Submissions")

# Sample 80 respondent records
sample_respondents = clean_df.head(80).to_dict(orient="records")

data_payload = {
    "kpis": {
        "total_responses": len(clean_df),
        "raw_responses": 525,
        "duplicates_removed": 12,
        "clean_pct": round(len(clean_df) / 525 * 100, 1),
        "winner_tool": "Python",
        "winner_votes": 151,
        "winner_share": 30.2,
        "runner_up_tool": "Power BI",
        "runner_up_votes": 113,
        "runner_up_share": 22.6,
        "mean_satisfaction": 3.91,
        "recommend_rate": 84.0,
        "peak_day": "2026-09-14",
        "peak_day_votes": 36
    },
    "vote_summary": vote_summary.to_dict(orient="records"),
    "regional_summary": reg_summary.to_dict(orient="records"),
    "regional_crosstab": reg_crosstab.to_dict(orient="records"),
    "demographics": demo_summary.to_dict(orient="records"),
    "daily_trend": daily_trend.to_dict(orient="records"),
    "respondents": sample_respondents
}

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Poll Results Visualizer & Survey Intelligence Suite</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root {{
      --bg-base: #090d16;
      --bg-card: rgba(16, 22, 36, 0.75);
      --bg-card-hover: rgba(24, 32, 52, 0.85);
      --border-card: rgba(255, 255, 255, 0.08);
      --border-accent: rgba(56, 189, 248, 0.3);
      --text-main: #f1f5f9;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --primary: #38bdf8;
      --accent: #818cf8;
      --success: #34d399;
      --warning: #fbbf24;
      --danger: #f87171;
      --font-sans: 'Plus Jakarta Sans', sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      background-color: var(--bg-base);
      color: var(--text-main);
      font-family: var(--font-sans);
      line-height: 1.6;
      background-image: 
        radial-gradient(circle at 20% 15%, rgba(56, 189, 248, 0.08) 0%, transparent 40%),
        radial-gradient(circle at 80% 85%, rgba(129, 140, 248, 0.08) 0%, transparent 40%);
      background-attachment: fixed;
      min-height: 100vh;
    }}

    header {{
      background: rgba(9, 13, 22, 0.85);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border-card);
      position: sticky;
      top: 0;
      z-index: 1000;
      padding: 1rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .logo-container {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}

    .logo-badge {{
      background: linear-gradient(135deg, #38bdf8, #818cf8);
      width: 40px;
      height: 40px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 1.25rem;
      color: #090d16;
    }}

    .logo-text h1 {{
      font-size: 1.15rem;
      font-weight: 700;
      letter-spacing: -0.02em;
    }}

    .logo-text p {{
      font-size: 0.75rem;
      color: var(--text-muted);
    }}

    nav {{
      display: flex;
      gap: 1.25rem;
    }}

    nav a {{
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.875rem;
      font-weight: 500;
      transition: color 0.2s ease;
      cursor: pointer;
    }}

    nav a:hover, nav a.active {{
      color: var(--primary);
    }}

    .container {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 2rem;
    }}

    .hero {{
      text-align: center;
      padding: 2.5rem 1rem 2rem;
    }}

    .hero-badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.35rem 1rem;
      background: rgba(56, 189, 248, 0.1);
      border: 1px solid rgba(56, 189, 248, 0.3);
      border-radius: 9999px;
      font-size: 0.8rem;
      color: var(--primary);
      font-weight: 600;
      margin-bottom: 1rem;
    }}

    .hero h2 {{
      font-size: 2.75rem;
      font-weight: 800;
      letter-spacing: -0.03em;
      margin-bottom: 1rem;
      background: linear-gradient(135deg, #ffffff 30%, #94a3b8 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}

    .hero p {{
      max-width: 750px;
      margin: 0 auto;
      color: var(--text-muted);
      font-size: 1.05rem;
    }}

    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 1.25rem;
      margin-bottom: 2.5rem;
    }}

    .kpi-card {{
      background: var(--bg-card);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border-card);
      border-radius: 14px;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      transition: all 0.3s ease;
    }}

    .kpi-card:hover {{
      border-color: var(--border-accent);
      transform: translateY(-2px);
    }}

    .kpi-title {{
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-dim);
      font-weight: 600;
      margin-bottom: 0.5rem;
    }}

    .kpi-value {{
      font-size: 1.85rem;
      font-weight: 800;
      color: var(--text-main);
      font-family: var(--font-mono);
      letter-spacing: -0.02em;
    }}

    .kpi-subtext {{
      font-size: 0.75rem;
      color: var(--text-muted);
      margin-top: 0.35rem;
    }}

    .section-title {{
      font-size: 1.5rem;
      font-weight: 700;
      margin-bottom: 1.25rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    .grid-2 {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2.5rem;
    }}

    .panel {{
      background: var(--bg-card);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border-card);
      border-radius: 14px;
      padding: 1.5rem;
    }}

    .chart-container {{
      width: 100%;
      height: 380px;
    }}

    .table-wrapper {{
      overflow-x: auto;
      max-height: 450px;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.85rem;
    }}

    th {{
      background: rgba(9, 13, 22, 0.9);
      color: var(--text-dim);
      font-weight: 600;
      padding: 0.75rem 1rem;
      position: sticky;
      top: 0;
      border-bottom: 1px solid var(--border-card);
    }}

    td {{
      padding: 0.65rem 1rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
      color: var(--text-muted);
    }}

    tr:hover td {{
      background: rgba(255, 255, 255, 0.02);
      color: var(--text-main);
    }}

    .pill {{
      display: inline-block;
      padding: 0.2rem 0.6rem;
      border-radius: 6px;
      font-size: 0.75rem;
      font-weight: 600;
    }}

    .tool-Python {{ background: rgba(37, 99, 235, 0.2); color: #60a5fa; border: 1px solid rgba(37, 99, 235, 0.4); }}
    .tool-PowerBI {{ background: rgba(13, 148, 136, 0.2); color: #2dd4bf; border: 1px solid rgba(13, 148, 136, 0.4); }}
    .tool-SQL {{ background: rgba(124, 58, 237, 0.2); color: #c084fc; border: 1px solid rgba(124, 58, 237, 0.4); }}
    .tool-Excel {{ background: rgba(234, 88, 12, 0.2); color: #fb923c; border: 1px solid rgba(234, 88, 12, 0.4); }}
    .tool-Tableau {{ background: rgba(217, 119, 6, 0.2); color: #f59e0b; border: 1px solid rgba(217, 119, 6, 0.4); }}
    .tool-R {{ background: rgba(220, 38, 38, 0.2); color: #f87171; border: 1px solid rgba(220, 38, 38, 0.4); }}

    /* Simulator */
    .vote-sim-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 1rem;
      margin-bottom: 1.5rem;
    }}

    .vote-card {{
      background: rgba(9, 13, 22, 0.6);
      border: 1px solid var(--border-card);
      border-radius: 10px;
      padding: 1rem;
      text-align: center;
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .vote-card:hover, .vote-card.active {{
      border-color: var(--primary);
      transform: scale(1.03);
    }}

    footer {{
      border-top: 1px solid var(--border-card);
      padding: 2rem;
      text-align: center;
      color: var(--text-dim);
      font-size: 0.85rem;
      margin-top: 4rem;
    }}

    footer a {{
      color: var(--primary);
      text-decoration: none;
    }}
  </style>
</head>
<body>

  <header>
    <div class="logo-container">
      <div class="logo-badge">📊</div>
      <div class="logo-text">
        <h1>Poll Results Visualizer</h1>
        <p>Survey Data Cleaning, Multi-Dimensional Cross-Tabs & Statistical Insights</p>
      </div>
    </div>
    <nav>
      <a href="#overview" class="active">Overview</a>
      <a href="#votes">Vote Shares</a>
      <a href="#regional">Regional Breakdown</a>
      <a href="#demographics">Demographics</a>
      <a href="#simulator">Live Poll Booth</a>
      <a href="#respondents">Respondent Ledger</a>
      <a href="https://github.com/rohitsingh83/Poll-Results-Visualizer" target="_blank">GitHub Repo ↗</a>
    </nav>
  </header>

  <div class="container">
    <section class="hero" id="overview">
      <div class="hero-badge">✦ Complete Survey Pipeline & Statistical Visualizer</div>
      <h2>Transform Raw Survey Feedback into Executive Decisions</h2>
      <p>Automated survey standardization, duplicate detection, cross-tabulation across age, gender and regions, satisfaction sentiment correlation, and real-time interactive polling.</p>
    </section>

    <!-- KPI Summary Cards -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-title">Winning Option</div>
        <div class="kpi-value" style="color: #60a5fa;">Python</div>
        <div class="kpi-subtext">{data_payload["kpis"]["winner_votes"]} votes ({data_payload["kpis"]["winner_share"]}%)</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Runner-Up Tool</div>
        <div class="kpi-value" style="color: #2dd4bf;">Power BI</div>
        <div class="kpi-subtext">{data_payload["kpis"]["runner_up_votes"]} votes ({data_payload["kpis"]["runner_up_share"]}%)</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Victory Margin</div>
        <div class="kpi-value">+7.6%</div>
        <div class="kpi-subtext">+38 vote lead over #2</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Mean Satisfaction</div>
        <div class="kpi-value">{data_payload["kpis"]["mean_satisfaction"]} / 5.0</div>
        <div class="kpi-subtext">Net recommend rate: {data_payload["kpis"]["recommend_rate"]}%</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Cleaned Responses</div>
        <div class="kpi-value">{data_payload["kpis"]["total_responses"]}</div>
        <div class="kpi-subtext">95.2% retention from 525 raw</div>
      </div>
    </div>

    <!-- Charts Section 1: Vote Share & Donut -->
    <div class="section-title" id="votes">📈 Tool Preference & Market Share Distribution</div>
    <div class="grid-2">
      <div class="panel">
        <h3 style="font-size: 1.1rem; margin-bottom: 1rem;">Primary Data Tool Share (Vote Share %)</h3>
        <div id="chart-votes" class="chart-container"></div>
      </div>
      <div class="panel">
        <h3 style="font-size: 1.1rem; margin-bottom: 1rem;">Cumulative Share & Donut Breakdown</h3>
        <div id="chart-donut" class="chart-container"></div>
      </div>
    </div>

    <!-- Charts Section 2: Regional & Daily Submissions -->
    <div class="section-title" id="regional">🌍 Regional Tool Preferences & Survey Dynamics</div>
    <div class="grid-2">
      <div class="panel">
        <h3 style="font-size: 1.1rem; margin-bottom: 1rem;">Preferred Tool Breakdown by Region</h3>
        <div id="chart-regional" class="chart-container"></div>
      </div>
      <div class="panel">
        <h3 style="font-size: 1.1rem; margin-bottom: 1rem;">Daily Response Submission Velocity</h3>
        <div id="chart-daily" class="chart-container"></div>
      </div>
    </div>

    <!-- Summary Table: Option-Wise Metrics -->
    <div class="panel" style="margin-bottom: 2.5rem;">
      <h3 style="font-size: 1.1rem; margin-bottom: 1rem;">Detailed Tool Metrics & Satisfaction Benchmark</h3>
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Tool Name</th>
              <th>Total Votes</th>
              <th>Vote Share %</th>
              <th>Cumulative Share %</th>
              <th>Avg Satisfaction</th>
              <th>Recommend Rate %</th>
              <th>Avg Feedback Length</th>
            </tr>
          </thead>
          <tbody id="vote-table-body">
            <!-- populated by JS -->
          </tbody>
        </table>
      </div>
    </div>

    <!-- Interactive Polling Booth -->
    <div class="section-title" id="simulator">🗳️ Interactive Live Polling Booth</div>
    <div class="panel" style="margin-bottom: 2.5rem;">
      <p style="color: var(--text-muted); margin-bottom: 1.5rem; font-size: 0.95rem;">
        Cast an interactive simulated vote below! Watch how the live distribution updates dynamically with real-time recalculation of leading positions and percentage shares.
      </p>

      <div class="vote-sim-grid">
        <div class="vote-card" onclick="castVote('Python')">
          <div style="font-size: 1.8rem; margin-bottom: 0.25rem;">🐍</div>
          <div style="font-weight: 700; color: #60a5fa;">Python</div>
          <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 0.25rem;">Click to Vote</div>
        </div>
        <div class="vote-card" onclick="castVote('Power BI')">
          <div style="font-size: 1.8rem; margin-bottom: 0.25rem;">📊</div>
          <div style="font-weight: 700; color: #2dd4bf;">Power BI</div>
          <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 0.25rem;">Click to Vote</div>
        </div>
        <div class="vote-card" onclick="castVote('SQL')">
          <div style="font-size: 1.8rem; margin-bottom: 0.25rem;">🗄️</div>
          <div style="font-weight: 700; color: #c084fc;">SQL</div>
          <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 0.25rem;">Click to Vote</div>
        </div>
        <div class="vote-card" onclick="castVote('Excel')">
          <div style="font-size: 1.8rem; margin-bottom: 0.25rem;">📗</div>
          <div style="font-weight: 700; color: #fb923c;">Excel</div>
          <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 0.25rem;">Click to Vote</div>
        </div>
        <div class="vote-card" onclick="castVote('Tableau')">
          <div style="font-size: 1.8rem; margin-bottom: 0.25rem;">📈</div>
          <div style="font-weight: 700; color: #f59e0b;">Tableau</div>
          <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 0.25rem;">Click to Vote</div>
        </div>
        <div class="vote-card" onclick="castVote('R')">
          <div style="font-size: 1.8rem; margin-bottom: 0.25rem;">📉</div>
          <div style="font-weight: 700; color: #f87171;">R</div>
          <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 0.25rem;">Click to Vote</div>
        </div>
      </div>

      <div style="text-align: center; color: var(--success); font-weight: 600; font-size: 0.9rem;" id="sim-feedback">
        Simulated live poll ready. Cast a vote to test real-time share recomputation!
      </div>
    </div>

    <!-- Respondent Ledger Explorer -->
    <div class="section-title" id="respondents">📋 Audited Respondent Ledger (Sample 80 Records)</div>
    <div class="panel">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 1rem;">
        <p style="font-size: 0.85rem; color: var(--text-muted);">
          Standardized poll responses with normalized tool names, satisfaction scores, and respondent feedback.
        </p>
        <input type="text" id="search-resp" placeholder="Filter by tool, region, role..." style="background: rgba(9,13,22,0.8); border: 1px solid var(--border-card); color: white; padding: 0.4rem 0.8rem; border-radius: 6px; font-size: 0.85rem; width: 260px;" oninput="filterRespondents()">
      </div>
      <div class="table-wrapper">
        <table id="resp-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Age Group</th>
              <th>Gender</th>
              <th>Region</th>
              <th>Role</th>
              <th>Preferred Tool</th>
              <th>Satisfaction</th>
              <th>Recommend</th>
              <th>Feedback Snippet</th>
            </tr>
          </thead>
          <tbody id="resp-body">
            <!-- populated by JS -->
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <footer>
    <p>Poll Results Visualizer &copy; 2026 Rohit Singh &bull; Engineered with Python, Pandas & Plotly.js &bull; Hosted on GitHub Pages</p>
  </footer>

  <script>
    const DATA = {json.dumps(data_payload)};

    // Current vote count state
    let liveVotes = {{}};
    DATA.vote_summary.forEach(v => {{
      liveVotes[v['Preferred Tool']] = v.Votes;
    }});

    function renderCharts() {{
      const toolNames = DATA.vote_summary.map(v => v['Preferred Tool']);
      const voteCounts = toolNames.map(t => liveVotes[t]);
      const totalVotes = voteCounts.reduce((a, b) => a + b, 0);
      const voteShares = voteCounts.map(v => (v / totalVotes * 100).toFixed(1));

      // Bar Chart
      Plotly.newPlot('chart-votes', [{{
        x: toolNames,
        y: voteCounts,
        type: 'bar',
        text: voteShares.map(s => s + '%'),
        textposition: 'auto',
        marker: {{
          color: ['#2563EB', '#0D9488', '#7C3AED', '#EA580C', '#D97706', '#DC2626']
        }}
      }}], {{
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: {{ color: '#94a3b8', family: 'Plus Jakarta Sans' }},
        margin: {{ l: 40, r: 20, t: 20, b: 40 }},
        yaxis: {{ title: 'Votes Count', gridcolor: 'rgba(255,255,255,0.05)' }}
      }}, {{ responsive: true, displayModeBar: false }});

      // Donut Chart
      Plotly.newPlot('chart-donut', [{{
        labels: toolNames,
        values: voteCounts,
        type: 'pie',
        hole: 0.45,
        marker: {{
          colors: ['#2563EB', '#0D9488', '#7C3AED', '#EA580C', '#D97706', '#DC2626']
        }}
      }}], {{
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: {{ color: '#94a3b8', family: 'Plus Jakarta Sans' }},
        margin: {{ l: 20, r: 20, t: 20, b: 20 }}
      }}, {{ responsive: true, displayModeBar: false }});
    }}

    renderCharts();

    // Regional Stacked Bar Chart
    const regions = DATA.regional_crosstab.map(r => r.Region);
    const tools = ['Python', 'Power BI', 'SQL', 'Excel', 'Tableau', 'R'];
    const regionalTraces = tools.map((t, idx) => ({{
      x: regions,
      y: DATA.regional_crosstab.map(r => r[t] || 0),
      name: t,
      type: 'bar',
      marker: {{
        color: ['#2563EB', '#0D9488', '#7C3AED', '#EA580C', '#D97706', '#DC2626'][idx]
      }}
    }}));

    Plotly.newPlot('chart-regional', regionalTraces, {{
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      font: {{ color: '#94a3b8', family: 'Plus Jakarta Sans' }},
      margin: {{ l: 40, r: 20, t: 20, b: 40 }},
      barmode: 'stack',
      yaxis: {{ title: 'Responses', gridcolor: 'rgba(255,255,255,0.05)' }},
      legend: {{ orientation: 'h', y: 1.1 }}
    }}, {{ responsive: true, displayModeBar: false }});

    // Daily Response Trend
    const dates = DATA.daily_trend.map(d => d.Date);
    const subCounts = DATA.daily_trend.map(d => d.Submissions);

    Plotly.newPlot('chart-daily', [{{
      x: dates,
      y: subCounts,
      type: 'scatter',
      mode: 'lines+markers',
      line: {{ color: '#38bdf8', width: 2.5 }},
      marker: {{ size: 6, color: '#818cf8' }}
    }}], {{
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      font: {{ color: '#94a3b8', family: 'Plus Jakarta Sans' }},
      margin: {{ l: 40, r: 20, t: 20, b: 40 }},
      yaxis: {{ title: 'Daily Submissions', gridcolor: 'rgba(255,255,255,0.05)' }}
    }}, {{ responsive: true, displayModeBar: false }});

    // Populate Vote Summary Table
    const voteTableBody = document.getElementById('vote-table-body');
    DATA.vote_summary.forEach(row => {{
      const tr = document.createElement('tr');
      const toolClass = 'tool-' + row['Preferred Tool'].replace(/\\s+/g, '');
      tr.innerHTML = `
        <td style="font-weight:700; color:white;">#${{row.Rank}}</td>
        <td><span class="pill ${{toolClass}}">${{row['Preferred Tool']}}</span></td>
        <td style="font-weight:600; color:white;">${{row.Votes}}</td>
        <td>${{row.Vote_Share_Pct.toFixed(1)}}%</td>
        <td>${{row.Cumulative_Share_Pct.toFixed(1)}}%</td>
        <td>⭐ ${{row.Avg_Satisfaction.toFixed(2)}}</td>
        <td style="color:${{row.Recommend_Rate_Pct >= 80 ? '#34d399' : '#fbbf24'}}">${{row.Recommend_Rate_Pct.toFixed(1)}}%</td>
        <td>${{row.Avg_Feedback_Length.toFixed(0)}} chars</td>
      `;
      voteTableBody.appendChild(tr);
    }});

    // Populate Respondents Table
    const respBody = document.getElementById('resp-body');
    function renderRespondents(items) {{
      respBody.innerHTML = '';
      items.forEach(r => {{
        const tr = document.createElement('tr');
        const toolClass = 'tool-' + (r['Preferred Tool'] || '').replace(/\\s+/g, '');
        tr.innerHTML = `
          <td style="font-family:var(--font-mono); font-weight:600; color:white;">${{r.Respondent_ID}}</td>
          <td>${{r['Age Group']}}</td>
          <td>${{r.Gender}}</td>
          <td>${{r.Region}}</td>
          <td>${{r.Role}}</td>
          <td><span class="pill ${{toolClass}}">${{r['Preferred Tool']}}</span></td>
          <td>⭐ ${{r['Satisfaction (1-5)']}}</td>
          <td style="color:${{r.Recommend === 'Yes' ? '#34d399' : '#f87171'}}">${{r.Recommend}}</td>
          <td style="max-width:260px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${{r.Feedback}}</td>
        `;
        respBody.appendChild(tr);
      }});
    }}
    renderRespondents(DATA.respondents);

    function filterRespondents() {{
      const q = document.getElementById('search-resp').value.toLowerCase();
      const filtered = DATA.respondents.filter(r => 
        (r['Preferred Tool'] || '').toLowerCase().includes(q) ||
        (r.Region || '').toLowerCase().includes(q) ||
        (r.Role || '').toLowerCase().includes(q) ||
        (r.Feedback || '').toLowerCase().includes(q)
      );
      renderRespondents(filtered);
    }}

    function castVote(tool) {{
      liveVotes[tool] = (liveVotes[tool] || 0) + 1;
      renderCharts();
      document.getElementById('sim-feedback').innerHTML = 
        `🎉 Successfully recorded a simulated vote for <span style="color:white; font-weight:bold;">${{tool}}</span>! Live vote share recomputed.`;
    }}
  </script>
</body>
</html>
"""

os.makedirs("docs", exist_ok=True)
with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated docs/index.html ({len(html_content)} bytes)")
