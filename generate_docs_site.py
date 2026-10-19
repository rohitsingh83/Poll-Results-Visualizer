"""
generate_docs_site.py
Generates a distinct Clean Tech Kinetic Polling Studio UI for Poll-Results-Visualizer.
Stripe / Linear interactive documentation aesthetic.
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

# Sample 50 respondent records
sample_respondents = clean_df.head(50).to_dict(orient="records")

data_payload = {
    "kpis": {
        "total_responses": len(clean_df),
        "winner_tool": "Python",
        "winner_votes": 151,
        "winner_share": 30.2,
        "runner_up_tool": "Power BI",
        "runner_up_votes": 113,
        "runner_up_share": 22.6,
        "victory_margin": 7.6,
        "mean_satisfaction": 3.91,
        "recommend_rate": 84.0,
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
  <title>PulsePoll &bull; Developer Tooling Market Share & Survey Intelligence</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root {{
      --bg: #080c16;
      --card: #0f172a;
      --card-elevated: #152238;
      --border: #1e293b;
      --border-accent: rgba(99, 102, 241, 0.4);
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --indigo: #6366f1;
      --indigo-glow: rgba(99, 102, 241, 0.2);
      --teal: #14b8a6;
      --amber: #f59e0b;
      --font: 'Plus Jakarta Sans', sans-serif;
      --mono: 'JetBrains Mono', monospace;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      background: var(--bg);
      color: var(--text);
      font-family: var(--font);
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
    }}

    header {{
      border-bottom: 1px solid var(--border);
      padding: 1rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: rgba(8, 12, 22, 0.9);
      backdrop-filter: blur(12px);
      position: sticky;
      top: 0;
      z-index: 50;
    }}

    .logo-area {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}

    .logo-icon {{
      width: 28px;
      height: 28px;
      border-radius: 8px;
      background: linear-gradient(135deg, #6366f1, #a855f7);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.9rem;
    }}

    .logo-title {{
      font-weight: 700;
      font-size: 1rem;
      letter-spacing: -0.02em;
    }}

    .nav-links a {{
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.8125rem;
      margin-left: 1.5rem;
      transition: color 0.15s;
    }}

    .nav-links a:hover {{ color: var(--text); }}

    .wrap {{
      max-width: 1320px;
      margin: 0 auto;
      padding: 2.5rem 1.5rem 5rem;
    }}

    .studio-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      margin-bottom: 2rem;
      flex-wrap: wrap;
      gap: 1.5rem;
    }}

    .studio-header h1 {{
      font-size: 2rem;
      font-weight: 800;
      letter-spacing: -0.03em;
      color: #ffffff;
    }}

    .studio-header p {{
      color: var(--text-muted);
      font-size: 0.9375rem;
      max-width: 650px;
      margin-top: 0.25rem;
    }}

    .live-badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      font-family: var(--mono);
      font-size: 0.75rem;
      background: rgba(20, 184, 166, 0.12);
      border: 1px solid rgba(20, 184, 166, 0.3);
      color: var(--teal);
      padding: 0.35rem 0.75rem;
      border-radius: 9999px;
    }}

    .dot {{
      width: 6px;
      height: 6px;
      background: var(--teal);
      border-radius: 50%;
      box-shadow: 0 0 8px var(--teal);
    }}

    /* Polling Hero Deck */
    .hero-poll-deck {{
      display: grid;
      grid-template-columns: repeat(6, 1fr);
      gap: 0.75rem;
      margin-bottom: 2rem;
    }}

    @media (max-width: 1024px) {{
      .hero-poll-deck {{ grid-template-columns: repeat(3, 1fr); }}
    }}
    @media (max-width: 600px) {{
      .hero-poll-deck {{ grid-template-columns: repeat(2, 1fr); }}
    }}

    .poll-card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 1.15rem 1rem;
      text-align: center;
      cursor: pointer;
      transition: all 0.2s ease;
      position: relative;
      overflow: hidden;
    }}

    .poll-card:hover {{
      border-color: var(--indigo);
      transform: translateY(-2px);
      box-shadow: 0 8px 20px -4px var(--indigo-glow);
    }}

    .poll-rank {{
      position: absolute;
      top: 8px;
      left: 10px;
      font-family: var(--mono);
      font-size: 0.6875rem;
      color: var(--text-dim);
    }}

    .poll-icon {{
      font-size: 1.75rem;
      margin: 0.4rem 0 0.2rem;
    }}

    .poll-name {{
      font-weight: 700;
      font-size: 0.9375rem;
      margin-bottom: 0.2rem;
    }}

    .poll-share {{
      font-family: var(--mono);
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--teal);
    }}

    .poll-votes {{
      font-family: var(--mono);
      font-size: 0.6875rem;
      color: var(--text-dim);
      margin-top: 0.15rem;
    }}

    .poll-btn {{
      margin-top: 0.65rem;
      background: rgba(99, 102, 241, 0.15);
      border: 1px solid rgba(99, 102, 241, 0.3);
      color: #818cf8;
      font-size: 0.6875rem;
      font-weight: 600;
      padding: 0.25rem 0.5rem;
      border-radius: 4px;
      width: 100%;
    }}

    /* Studio 2-Grid */
    .studio-grid {{
      display: grid;
      grid-template-columns: 1.35fr 1fr;
      gap: 1.25rem;
      margin-bottom: 2rem;
    }}

    @media (max-width: 950px) {{
      .studio-grid {{ grid-template-columns: 1fr; }}
    }}

    .studio-panel {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.5rem;
    }}

    .panel-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
    }}

    .panel-title {{
      font-size: 0.9375rem;
      font-weight: 700;
      letter-spacing: -0.01em;
    }}

    /* Table Minimal */
    .t-wrap {{
      overflow-x: auto;
      max-height: 380px;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.8125rem;
    }}

    th {{
      font-family: var(--mono);
      font-size: 0.6875rem;
      color: var(--text-dim);
      text-transform: uppercase;
      padding: 0.6rem 0.75rem;
      border-bottom: 1px solid var(--border);
      text-align: left;
    }}

    td {{
      padding: 0.6rem 0.75rem;
      border-bottom: 1px solid rgba(30, 41, 59, 0.6);
      color: var(--text-muted);
    }}

    tr:hover td {{
      color: var(--text);
      background: rgba(255, 255, 255, 0.02);
    }}

    .status-toast {{
      margin-top: 1rem;
      padding: 0.6rem 1rem;
      background: rgba(20, 184, 166, 0.1);
      border: 1px solid rgba(20, 184, 166, 0.3);
      border-radius: 6px;
      font-size: 0.8125rem;
      color: var(--teal);
      text-align: center;
      font-family: var(--mono);
    }}

    footer {{
      border-top: 1px solid var(--border);
      padding-top: 2rem;
      font-size: 0.75rem;
      color: var(--text-dim);
      display: flex;
      justify-content: space-between;
    }}
  </style>
</head>
<body>

  <header>
    <div class="logo-area">
      <div class="logo-icon">⚡</div>
      <div class="logo-title">PulsePoll Studio</div>
    </div>
    <div class="nav-links">
      <a href="#booth">Voting Station</a>
      <a href="#market">Market Share</a>
      <a href="#regional">Geographic</a>
      <a href="#verbatim">Responses</a>
      <a href="https://github.com/rohitsingh83/Poll-Results-Visualizer" target="_blank">GitHub ↗</a>
    </div>
  </header>

  <div class="wrap">
    <div class="studio-header">
      <div>
        <h1>Survey Intelligence & Opinion Analytics</h1>
        <p>Automated pipeline processing data science tooling preferences (Python, Power BI, SQL, Excel, Tableau, R) with cross-tabulated demographic cohort intelligence.</p>
      </div>
      <div>
        <div class="live-badge">
          <span class="dot"></span>
          <span>{data_payload["kpis"]["total_responses"]} VERIFIED RESPONDENTS</span>
        </div>
      </div>
    </div>

    <!-- Live Polling Station Cards -->
    <div class="hero-poll-deck" id="booth">
      <!-- Populated by JS -->
    </div>

    <div class="status-toast" id="vote-notice">
      Interactive polling station active &bull; Click any card above to cast a live simulated vote!
    </div>

    <div style="height: 2rem;"></div>

    <!-- Studio Grid Row 1 -->
    <div class="studio-grid">
      <div class="studio-panel" id="market">
        <div class="panel-top">
          <div class="panel-title">Primary Tool Market Share Distribution</div>
          <span style="font-family: var(--mono); font-size: 0.75rem; color: var(--text-dim);">VOTE %</span>
        </div>
        <div id="plot-bars" style="width: 100%; height: 320px;"></div>
      </div>

      <div class="studio-panel">
        <div class="panel-top">
          <div class="panel-title">Cumulative Share & Concentration</div>
          <span style="font-family: var(--mono); font-size: 0.75rem; color: var(--text-dim);">DONUT</span>
        </div>
        <div id="plot-donut" style="width: 100%; height: 320px;"></div>
      </div>
    </div>

    <!-- Studio Grid Row 2: Regional & Daily -->
    <div class="studio-grid">
      <div class="studio-panel" id="regional">
        <div class="panel-top">
          <div class="panel-title">Regional Preference Stacked Analysis</div>
          <span style="font-family: var(--mono); font-size: 0.75rem; color: var(--text-dim);">5 ZONES</span>
        </div>
        <div id="plot-regional" style="width: 100%; height: 300px;"></div>
      </div>

      <div class="studio-panel">
        <div class="panel-top">
          <div class="panel-title">Daily Submission Velocity Trend</div>
          <span style="font-family: var(--mono); font-size: 0.75rem; color: var(--text-dim);">PEAK: 36/DAY</span>
        </div>
        <div id="plot-daily" style="width: 100%; height: 300px;"></div>
      </div>
    </div>

    <!-- Verbatim Feedback Table -->
    <div class="studio-panel" id="verbatim">
      <div class="panel-top">
        <div class="panel-title">Respondent Verbatim & Satisfaction Directory</div>
        <input type="text" id="srch-box" placeholder="Filter feedback..." style="background: var(--bg); border: 1px solid var(--border); color: var(--text); padding: 0.25rem 0.6rem; border-radius: 4px; font-size: 0.75rem; width: 180px;" oninput="filterTable()">
      </div>
      <div class="t-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Demographic</th>
              <th>Region</th>
              <th>Role</th>
              <th>Tool</th>
              <th>Rating</th>
              <th>Feedback</th>
            </tr>
          </thead>
          <tbody id="tbl-resp"></tbody>
        </table>
      </div>
    </div>

    <footer>
      <span>PulsePoll Studio &bull; Survey Analytics &copy; 2026 Rohit Singh</span>
      <span>Hosted on GitHub Pages &bull; Plus Jakarta Sans + Plotly.js</span>
    </footer>
  </div>

  <script>
    const DATA = {json.dumps(data_payload)};
    const EMOJIS = {{
      'Python': '🐍',
      'Power BI': '📊',
      'SQL': '🗄️',
      'Excel': '📗',
      'Tableau': '📈',
      'R': '📉'
    }};

    let liveVotes = {{}};
    DATA.vote_summary.forEach(v => {{
      liveVotes[v['Preferred Tool']] = v.Votes;
    }});

    function renderCards() {{
      const deck = document.getElementById('booth');
      deck.innerHTML = '';
      const total = Object.values(liveVotes).reduce((a, b) => a + b, 0);

      DATA.vote_summary.forEach((v, idx) => {{
        const name = v['Preferred Tool'];
        const votes = liveVotes[name];
        const share = (votes / total * 100).toFixed(1);

        const card = document.createElement('div');
        card.className = 'poll-card';
        card.onclick = () => castVote(name);
        card.innerHTML = `
          <div class="poll-rank">#${{idx + 1}}</div>
          <div class="poll-icon">${{EMOJIS[name] || '📊'}}</div>
          <div class="poll-name">${{name}}</div>
          <div class="poll-share">${{share}}%</div>
          <div class="poll-votes">${{votes}} votes</div>
          <button class="poll-btn">+ Vote</button>
        `;
        deck.appendChild(card);
      }});
    }}

    function renderCharts() {{
      const names = DATA.vote_summary.map(v => v['Preferred Tool']);
      const votes = names.map(n => liveVotes[n]);
      const total = votes.reduce((a, b) => a + b, 0);
      const shares = votes.map(v => (v / total * 100).toFixed(1));

      Plotly.newPlot('plot-bars', [{{
        x: names,
        y: votes,
        type: 'bar',
        text: shares.map(s => s + '%'),
        textposition: 'auto',
        marker: {{ color: ['#6366f1', '#14b8a6', '#8b5cf6', '#f59e0b', '#ec4899', '#ef4444'] }}
      }}], {{
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: {{ color: '#94a3b8', family: 'Plus Jakarta Sans', size: 11 }},
        margin: {{ l: 35, r: 10, t: 10, b: 35 }},
        yaxis: {{ gridcolor: '#1e293b' }}
      }}, {{ responsive: true, displayModeBar: false }});

      Plotly.newPlot('plot-donut', [{{
        labels: names,
        values: votes,
        type: 'pie',
        hole: 0.55,
        marker: {{ colors: ['#6366f1', '#14b8a6', '#8b5cf6', '#f59e0b', '#ec4899', '#ef4444'] }}
      }}], {{
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: {{ color: '#94a3b8', family: 'Plus Jakarta Sans', size: 11 }},
        margin: {{ l: 10, r: 10, t: 10, b: 10 }}
      }}, {{ responsive: true, displayModeBar: false }});
    }}

    renderCards();
    renderCharts();

    // Regional plot
    const regNames = DATA.regional_crosstab.map(r => r.Region);
    const tools = ['Python', 'Power BI', 'SQL', 'Excel', 'Tableau', 'R'];
    const rTraces = tools.map((t, i) => ({{
      x: regNames,
      y: DATA.regional_crosstab.map(r => r[t] || 0),
      name: t,
      type: 'bar',
      marker: {{ color: ['#6366f1', '#14b8a6', '#8b5cf6', '#f59e0b', '#ec4899', '#ef4444'][i] }}
    }}));

    Plotly.newPlot('plot-regional', rTraces, {{
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      font: {{ color: '#94a3b8', family: 'Plus Jakarta Sans', size: 10 }},
      margin: {{ l: 30, r: 10, t: 10, b: 35 }},
      barmode: 'stack',
      yaxis: {{ gridcolor: '#1e293b' }},
      legend: {{ orientation: 'h', y: 1.15 }}
    }}, {{ responsive: true, displayModeBar: false }});

    // Daily plot
    Plotly.newPlot('plot-daily', [{{
      x: DATA.daily_trend.map(d => d.Date),
      y: DATA.daily_trend.map(d => d.Submissions),
      type: 'scatter',
      mode: 'lines+markers',
      line: {{ color: '#6366f1', width: 2.5 }},
      marker: {{ size: 5, color: '#14b8a6' }}
    }}], {{
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      font: {{ color: '#94a3b8', family: 'Plus Jakarta Sans', size: 10 }},
      margin: {{ l: 30, r: 10, t: 10, b: 35 }},
      yaxis: {{ gridcolor: '#1e293b' }}
    }}, {{ responsive: true, displayModeBar: false }});

    // Populate feedback table
    const tbl = document.getElementById('tbl-resp');
    function renderFeedback(items) {{
      tbl.innerHTML = '';
      items.forEach(r => {{
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td style="font-family:var(--mono);">${{r.Respondent_ID}}</td>
          <td>${{r['Age Group']}} &bull; ${{r.Gender}}</td>
          <td>${{r.Region}}</td>
          <td>${{r.Role}}</td>
          <td style="font-weight:600; color:var(--text);">${{r['Preferred Tool']}}</td>
          <td>⭐ ${{r['Satisfaction (1-5)']}}</td>
          <td style="max-width:280px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${{r.Feedback}}</td>
        `;
        tbl.appendChild(tr);
      }});
    }}
    renderFeedback(DATA.respondents);

    function filterTable() {{
      const q = document.getElementById('srch-box').value.toLowerCase();
      const filtered = DATA.respondents.filter(r => 
        (r['Preferred Tool'] || '').toLowerCase().includes(q) ||
        (r.Feedback || '').toLowerCase().includes(q) ||
        (r.Role || '').toLowerCase().includes(q)
      );
      renderFeedback(filtered);
    }}

    function castVote(name) {{
      liveVotes[name] = (liveVotes[name] || 0) + 1;
      renderCards();
      renderCharts();
      document.getElementById('vote-notice').innerHTML = 
        `🎉 Successfully recorded a simulated vote for <strong>${{name}}</strong>! Live market shares recomputed.`;
    }}
  </script>
</body>
</html>
"""

os.makedirs("docs", exist_ok=True)
with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated distinct Clean Tech Kinetic Polling docs/index.html ({len(html_content)} bytes)")
