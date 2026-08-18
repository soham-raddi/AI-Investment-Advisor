"""Bootstrap HTML rendering for the investment advisor dashboard."""

from __future__ import annotations

import base64
import json
from pathlib import Path

import pandas as pd
import plotly.express as px


def _to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _fmt_percent(value):
    try:
        return f"{float(value):.2%}"
    except (TypeError, ValueError):
        return "N/A"


def _fmt_number(value, decimals=2, prefix="", suffix=""):
    try:
        return f"{prefix}{float(value):.{decimals}f}{suffix}"
    except (TypeError, ValueError):
        return "N/A"


def _safe_text(value):
    if value is None:
        return ""
    return str(value)


def _df_records(df: pd.DataFrame) -> list[dict]:
    if df is None or df.empty:
        return []
    return json.loads(df.fillna("").to_json(orient="records"))


def _plotly_div(chart_html: str, element_id: str) -> str:
    if not chart_html:
        return f"<div class='empty-state'>No chart data available.</div>"
    return f"<div class='chart-shell' id='{element_id}'>{chart_html}</div>"


def _fig_div(fig, element_id: str) -> str:
    if fig is None:
        return "<div class='empty-state'>No chart data available.</div>"
    return f"<div class='chart-shell' id='{element_id}'></div><script>(function(){{const figure={fig.to_json()};Plotly.newPlot('{element_id}', figure.data, figure.layout, {{responsive:true, displayModeBar:false}});}})();</script>"


def _plotly_chart_script(fig, element_id: str) -> str:
    payload = fig.to_json()
    return f"""
    <div class='chart-shell' id='{element_id}'></div>
    <script>
      (function() {{
        const figure = {payload};
        Plotly.newPlot('{element_id}', figure.data, figure.layout, {{responsive: true, displayModeBar: false}});
      }})();
    </script>
    """


def _layout(title: str, subtitle: str, content: str, sidebar_html: str, theme: str = "blue") -> str:
    theme_class = f"theme-{theme}"
    return f"""
    <!doctype html>
    <html lang='en'>
    <head>
      <meta charset='utf-8'>
      <meta name='viewport' content='width=device-width, initial-scale=1'>
      <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css' rel='stylesheet'>
      <script src='https://cdn.plot.ly/plotly-2.32.0.min.js'></script>
      <style>
        :root {{
          --bg: #eef4fb;
          --surface: rgba(255,255,255,0.96);
          --panel: #0d1b33;
          --panel-2: #12284a;
          --text: #0f2747;
          --muted: #5e6f82;
          --accent: #1f77b4;
          --accent-2: #2ca02c;
          --accent-3: #ff7f0e;
          --accent-4: #d62728;
        }}
        body {{
          margin: 0;
          background:
            radial-gradient(circle at top left, rgba(31,119,180,.16), transparent 28%),
            radial-gradient(circle at top right, rgba(46,160,67,.11), transparent 24%),
            linear-gradient(180deg, #f7fbff 0%, #edf3f9 45%, #e5ebf3 100%);
          color: var(--text);
          font-family: Inter, Segoe UI, Arial, sans-serif;
        }}
        .app-shell {{ min-height: 100vh; }}
        .brand {{ background: linear-gradient(135deg, #102648, #173d70); border-radius: 24px; padding: 20px; box-shadow: 0 16px 34px rgba(0,0,0,.18); }}
        .brand h1 {{ font-size: 1.35rem; margin: 0 0 6px 0; font-weight: 800; }}
        .brand p {{ margin: 0; color: rgba(255,255,255,.82); line-height: 1.55; }}
        .nav-group {{ margin-top: 18px; }}
        .nav-label {{ color: rgba(255,255,255,.66); letter-spacing: .14em; font-size: .72rem; text-transform: uppercase; margin-bottom: 10px; }}
        .nav-btn {{
          display: block; width: 100%; text-align: left; text-decoration: none; color: #fff; background: rgba(255,255,255,.05);
          border: 1px solid rgba(255,255,255,.08); border-radius: 16px; padding: 12px 14px; margin-bottom: 10px;
          transition: .18s ease; font-weight: 600;
        }}
        .nav-btn:hover, .nav-btn.active {{ background: rgba(31,119,180,.24); border-color: rgba(31,119,180,.44); color: #fff; transform: translateX(2px); }}
        .nav-desc {{ display:block; color: rgba(255,255,255,.72); font-size: .84rem; font-weight: 400; margin-top: 4px; line-height: 1.4; }}
        .legend-card, .view-card {{ background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.08); border-radius: 18px; padding: 14px; margin-top: 14px; }}
        .legend-title {{ color: rgba(255,255,255,.74); font-size: .72rem; text-transform: uppercase; letter-spacing: .14em; margin-bottom: 8px; }}
        .legend-item {{ font-size: .9rem; margin-bottom: 6px; color: rgba(255,255,255,.88); }}
        .app-main {{ padding: 24px; min-width: 0; }}
        .hero {{
          background: linear-gradient(135deg, #102648 0%, #1f77b4 100%); color: white; border-radius: 28px; padding: 28px;
          box-shadow: 0 20px 40px rgba(15,39,71,.18); margin-bottom: 18px;
        }}
        .hero .eyebrow {{ text-transform: uppercase; letter-spacing: .18em; font-size: .72rem; color: rgba(255,255,255,.78); }}
        .hero h2 {{ margin: 10px 0 8px 0; font-size: 2rem; font-weight: 800; }}
        .hero p {{ margin: 0; max-width: 80ch; color: rgba(255,255,255,.88); line-height: 1.6; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 14px; margin: 18px 0; }}
        .metric {{ background: var(--surface); border-radius: 20px; padding: 18px; border-top: 4px solid var(--accent); box-shadow: 0 12px 26px rgba(15,39,71,.06); }}
        .metric .label {{ font-size: .74rem; letter-spacing: .12em; text-transform: uppercase; color: #64768a; margin-bottom: 8px; }}
        .metric .value {{ font-size: 1.9rem; font-weight: 800; color: #0f2747; line-height: 1.05; }}
        .metric .sub {{ margin-top: 8px; color: #637386; line-height: 1.45; font-size: .92rem; }}
        .section-title {{ font-size: 1.45rem; font-weight: 800; color: #132238; margin: 26px 0 14px; border-bottom: 1px solid rgba(31,119,180,.2); padding-bottom: 10px; }}
        .card-shell {{ background: var(--surface); border-radius: 22px; padding: 18px; box-shadow: 0 12px 28px rgba(15,39,71,.06); border: 1px solid rgba(15,39,71,.06); }}
        .signal-card {{ border-radius: 20px; padding: 18px; margin-bottom: 14px; border: 1px solid rgba(15,39,71,.06); box-shadow: 0 10px 22px rgba(15,39,71,.05); }}
        .signal-buy {{ background: linear-gradient(135deg, rgba(46,160,67,.12), rgba(46,160,67,.04)); border-top: 4px solid #2ca02c; }}
        .signal-avoid {{ background: linear-gradient(135deg, rgba(214,39,40,.12), rgba(214,39,40,.04)); border-top: 4px solid #d62728; }}
        .signal-card h4 {{ margin: 0 0 10px 0; color: #0f2747; font-size: 1.05rem; }}
        .signal-row {{ display:flex; justify-content:space-between; gap:14px; font-size:.94rem; color:#516173; margin-top:6px; }}
        .pill {{ display:inline-flex; align-items:center; padding: 6px 10px; border-radius: 999px; font-size:.78rem; font-weight:700; }}
        .pill-buy {{ background: rgba(46,160,67,.12); color:#1f7a33; }}
        .pill-hold {{ background: rgba(255,127,14,.14); color:#b85c00; }}
        .pill-avoid {{ background: rgba(214,39,40,.12); color:#b42318; }}
        .table-wrap {{ overflow:auto; border-radius: 18px; }}
        table {{ width:100%; border-collapse: separate; border-spacing: 0; }}
        thead th {{ background:#0f2747; color:#fff; padding: 12px 14px; position: sticky; top:0; }}
        tbody td {{ background: white; padding: 12px 14px; border-bottom: 1px solid #e7edf5; color:#20324a; }}
        tbody tr:hover td {{ background:#f6f9fc; }}
        .empty-state {{ background:white; border-radius:18px; padding:18px; color:#5d7085; }}
        .chart-shell {{ background: white; border-radius: 18px; padding: 8px; box-shadow: 0 12px 24px rgba(15,39,71,.06); margin-bottom: 14px; }}
        .two-col {{ display:grid; grid-template-columns: 1.2fr .8fr; gap: 14px; }}
        .three-col {{ display:grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }}
        .four-col {{ display:grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }}
        .muted {{ color: #637386; }}
        @media (max-width: 1180px) {{ .metric-grid, .four-col {{ grid-template-columns: repeat(2,1fr); }} .two-col {{ grid-template-columns: 1fr; }} .three-col {{ grid-template-columns: repeat(2,1fr); }} }}
        @media (max-width: 900px) {{ .metric-grid, .three-col, .four-col {{ grid-template-columns: 1fr; }} }}
      </style>
    </head>
    <body class='{theme_class}'>
      <div class='app-shell'>
        <main class='app-main'>
          <div class='card-shell mb-4'>
            <div class='d-flex flex-wrap align-items-center justify-content-between gap-3'>
              <div>
                <div class='legend-title' style='color:#637386'>Current view</div>
                <strong style='font-size:1.02rem;color:#0f2747'>{_safe_text(sidebar_html)}</strong>
              </div>
              <div class='muted'>Databricks SQL-backed dashboard shell</div>
            </div>
          </div>
          <div class='hero'>
            <div class='eyebrow'>AI Investment Advisor</div>
            <h2>{title}</h2>
            <p>{subtitle}</p>
          </div>
          {content}
        </main>
      </div>
      <script src='https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js'></script>
    </body>
    </html>
    """


def _sidebar(active_page: str) -> str:
    return active_page


def page_card_grid(metrics_data: list[tuple[str, str, str, str]]) -> str:
    cards = []
    for label, value, subtitle, accent in metrics_data:
        cards.append(
            f"<div class='metric' style='border-top-color:{accent}'><div class='label'>{label}</div><div class='value'>{value}</div><div class='sub'>{subtitle}</div></div>"
        )
    return f"<div class='metric-grid'>{''.join(cards)}</div>"


def page_table(df: pd.DataFrame, columns: list[str]) -> str:
    if df is None or df.empty:
        return "<div class='empty-state'>No rows available.</div>"
    rows = []
    for _, row in df[columns].iterrows():
        cells = "".join(f"<td>{_safe_text(row[col])}</td>" for col in columns)
        rows.append(f"<tr>{cells}</tr>")
    headers = "".join(f"<th>{col}</th>" for col in columns)
    return f"<div class='table-wrap'><table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"


def page_overview(summary: pd.DataFrame, recommendations: pd.DataFrame, sectors: pd.DataFrame, rec_dist: pd.DataFrame, risk_return_fig) -> str:
    hero_stats = []
    if not summary.empty:
        r = summary.iloc[0]
        hero_stats = [
            ("Market coverage", f"{int(_to_float(r.get('total_stocks'))):,}", "Stocks included in the current universe", "#1f77b4"),
            ("Positive bias", f"{int(_to_float(r.get('buy_count'))):,}", "BUY signals generated by the model", "#2ca02c"),
            ("Neutral stance", f"{int(_to_float(r.get('hold_count'))):,}", "HOLD signals suggesting watchlist candidates", "#ff7f0e"),
            ("Average return", _fmt_percent(r.get('avg_predicted_return')), "Mean predicted upside across the universe", "#5d7085"),
        ]

    buy_rows = recommendations[recommendations['Recommendation'] == 'BUY'].head(5) if not recommendations.empty else pd.DataFrame()
    avoid_rows = recommendations[recommendations['Recommendation'] == 'AVOID'] if not recommendations.empty else pd.DataFrame()
    top_buy = ""
    for _, row in buy_rows.iterrows():
        top_buy += f"""
          <div class='signal-card signal-buy'>
            <h4>{_safe_text(row['Ticker'])} <span class='muted'>({_safe_text(row['Sector'])})</span> <span class='pill pill-buy ms-2'>BUY</span></h4>
            <div class='signal-row'><span>Predicted return</span><strong>{_fmt_percent(row['Predicted_Return'])}</strong></div>
            <div class='signal-row'><span>Confidence</span><strong>{_fmt_number(row['Confidence_Score'], 0, suffix='/10')}</strong></div>
            <div class='signal-row'><span>Risk</span><strong>{_safe_text(row['Risk_Level'])}</strong></div>
          </div>
        """
    if not top_buy:
        top_buy = "<div class='empty-state'>No BUY recommendations available.</div>"

    top_avoid = ""
    for _, row in avoid_rows.iterrows():
        top_avoid += f"""
          <div class='signal-card signal-avoid'>
            <h4>{_safe_text(row['Ticker'])} <span class='muted'>({_safe_text(row['Sector'])})</span> <span class='pill pill-avoid ms-2'>AVOID</span></h4>
            <div class='signal-row'><span>Predicted return</span><strong>{_fmt_percent(row['Predicted_Return'])}</strong></div>
            <div class='signal-row'><span>Confidence</span><strong>{_fmt_number(row['Confidence_Score'], 0, suffix='/10')}</strong></div>
            <div class='signal-row'><span>Risk</span><strong>{_safe_text(row['Risk_Level'])}</strong></div>
          </div>
        """
    if not top_avoid:
        top_avoid = "<div class='empty-state'>No AVOID recommendations available.</div>"

    rec_table = page_table(
        recommendations.assign(
            Close=recommendations['Close'].apply(lambda x: _fmt_number(x, prefix='$')),
            Predicted_Return=recommendations['Predicted_Return'].apply(_fmt_percent),
            Confidence_Score=recommendations['Confidence_Score'].apply(lambda x: _fmt_number(x, 0, suffix='/10')),
        ) if not recommendations.empty else recommendations,
        ['Ticker', 'Sector', 'Close', 'Predicted_Return', 'Recommendation', 'Confidence_Score', 'Risk_Level'] if not recommendations.empty else []
    )

    charts_html = ""
    if rec_dist is not None and not rec_dist.empty:
      fig = px.pie(rec_dist, values='count', names='Recommendation', title='Recommendation Distribution', hole=0.35)
      charts_html += "<div class='card-shell mb-3'><h3 class='section-title mt-0'>Signal Distribution</h3>" + _fig_div(fig, 'overview_rec_dist') + "</div>"
    if sectors is not None and not sectors.empty:
      fig = px.bar(sectors, x='Sector', y='avg_predicted_return', title='Average Predicted Return by Sector', color='avg_predicted_return', color_continuous_scale='RdYlGn')
      charts_html += "<div class='card-shell mb-3'><h3 class='section-title mt-0'>Sector Strength</h3>" + _fig_div(fig, 'overview_sector_bar') + "</div>"
    if risk_return_fig is not None:
      charts_html += "<div class='card-shell'><h3 class='section-title mt-0'>Risk vs Return</h3>" + _fig_div(risk_return_fig, 'overview_risk_return') + "</div>"

    return _layout(
        "Investment Advisor Dashboard",
        "A polished market snapshot with recommendation signals, sector view, and risk-return positioning, designed as a Bootstrap dashboard.",
        f"""
        {page_card_grid(hero_stats)}
        <div class='card-shell mb-4'>
          <strong>How to read this dashboard:</strong> BUY cards point to stronger return setups, AVOID cards flag higher risk or weaker setups, and the charts summarize how the model is distributing those signals across sectors and risk bands.
        </div>
        <div class='two-col'>
          <div>
            <div class='section-title'>Top BUY Recommendations</div>
            {top_buy}
          </div>
          <div>
            <div class='section-title'>Stocks to AVOID</div>
            {top_avoid}
          </div>
        </div>
        <div class='section-title'>Market Analytics</div>
        <div class='card-shell mb-3'>
          <strong>Context:</strong> The charts below show signal distribution, sector performance, and the risk-return tradeoff.
        </div>
        {charts_html}
        <script>
          if (typeof Plotly !== 'undefined') {{
            const recDist = {json.dumps(rec_dist.to_dict('records') if rec_dist is not None and not rec_dist.empty else [])};
            const sectorsData = {json.dumps(sectors.to_dict('records') if sectors is not None and not sectors.empty else [])};
            const riskData = {risk_return_fig.to_json() if risk_return_fig is not None else 'null'};
          }}
        </script>
        <div class='card-shell mt-3'>
          <h3 class='section-title mt-0'>Recommendations Table</h3>
          {rec_table}
        </div>
        """,
        _sidebar("📈 Overview"),
    )


def page_recommendations(recommendations: pd.DataFrame) -> str:
    top_rows = recommendations.head(12).copy() if recommendations is not None and not recommendations.empty else pd.DataFrame()
  display_rows = top_rows.copy()
    if not top_rows.empty:
    display_rows = top_rows.assign(
      Close=top_rows['Close'].apply(lambda x: _fmt_number(x, prefix='$')),
      Predicted_Return=top_rows['Predicted_Return'].apply(_fmt_percent),
      Confidence_Score=top_rows['Confidence_Score'].apply(lambda x: _fmt_number(x, 0, suffix='/10')),
    )
        top_rows = top_rows.assign(
            Close=top_rows['Close'].apply(lambda x: _fmt_number(x, prefix='$')),
            Predicted_Return=top_rows['Predicted_Return'].apply(_fmt_percent),
            Confidence_Score=top_rows['Confidence_Score'].apply(lambda x: _fmt_number(x, 0, suffix='/10')),
        )
    buy_count = int((recommendations['Recommendation'] == 'BUY').sum()) if recommendations is not None and not recommendations.empty else 0
    avoid_count = int((recommendations['Recommendation'] == 'AVOID').sum()) if recommendations is not None and not recommendations.empty else 0
    hold_count = int((recommendations['Recommendation'] == 'HOLD').sum()) if recommendations is not None and not recommendations.empty else 0
    summary_cards = page_card_grid([
        ("Rows", f"{len(recommendations):,}", "Recommendation records available", "#1f77b4"),
        ("BUY", f"{buy_count:,}", "Positive signals", "#2ca02c"),
        ("HOLD", f"{hold_count:,}", "Watchlist signals", "#ff7f0e"),
        ("AVOID", f"{avoid_count:,}", "Risk-off signals", "#d62728"),
    ])
    return _layout(
        "Investment Recommendations",
        "A filterable view of the model outputs with detailed reasoning and clean signal styling.",
        f"""
        {summary_cards}
        <div class='card-shell mb-3'>
          <strong>Recommendation library:</strong> This page shows the top names returned by the model. Use the table to scan by ticker, sector, return, confidence, and risk level.
        </div>
        <div class='section-title'>Top Recommendations</div>
        {_fig_div(px.bar(recommendations.head(12) if recommendations is not None and not recommendations.empty else recommendations.head(1), x='Ticker', y='Predicted_Return', color='Recommendation', title='Top Recommendations') if recommendations is not None and not recommendations.empty else None, 'rec_bar')}
        <div class='card-shell mt-3'>
          <h3 class='section-title mt-0'>Recommendation Table</h3>
          {page_table(display_rows, ['Ticker', 'Sector', 'Close', 'Predicted_Return', 'Recommendation', 'Confidence_Score', 'Risk_Level']) if not display_rows.empty else '<div class="empty-state">No recommendations available.</div>'}
        </div>
        """,
        _sidebar("📋 Recommendations"),
    )


def page_stock_explorer(stock_recommendation: pd.DataFrame | None = None, stock_features: pd.DataFrame | None = None, selected_ticker: str = "") -> str:
    feature_rows = stock_features.copy() if stock_features is not None else pd.DataFrame()
    rec_row = stock_recommendation.iloc[0] if stock_recommendation is not None and not stock_recommendation.empty else None
    metrics_cards = []
    if rec_row is not None:
        metrics_cards = [
            ("Current Price", _fmt_number(rec_row.get('Close'), prefix='$'), "Latest close price", "#1f77b4"),
            ("Predicted Return", _fmt_percent(rec_row.get('Predicted_Return')), "Model-estimated upside", "#2ca02c"),
            ("Confidence", _fmt_number(rec_row.get('Confidence_Score'), 0, suffix='/10'), "Signal confidence", "#ff7f0e"),
            ("Risk", _safe_text(rec_row.get('Risk_Level')), "Risk classification", "#d62728"),
        ]
    price_fig = px.line(feature_rows, x='Date', y='Close', title='Historical Closing Price') if not feature_rows.empty else None
    return _layout(
        f"Stock Explorer{f' - {selected_ticker}' if selected_ticker else ''}",
        "Single-stock deep dive with historical price action, returns, volatility, and technical indicators.",
        f"""
        {page_card_grid(metrics_cards) if metrics_cards else '<div class="empty-state">Select a stock to view detailed metrics.</div>'}
        <div class='card-shell mb-3'>
          <strong>Stock profile:</strong> {selected_ticker or 'Select a ticker from the app shell'}
        </div>
        <div class='section-title'>Price History</div>
        {_fig_div(price_fig, 'stock_price')}
        <div class='two-col'>
          <div class='card-shell'>
            <h3 class='section-title mt-0'>Technical Summary</h3>
            {page_table(feature_rows.tail(12).assign(Close=feature_rows.tail(12)['Close'].apply(lambda x: _fmt_number(x, prefix='$')) if not feature_rows.empty else []), ['Date', 'Close', 'Daily_Return', 'Volatility', 'SMA_7', 'SMA_30']) if not feature_rows.empty else '<div class="empty-state">No historical rows available.</div>'}
          </div>
          <div class='card-shell'>
            <h3 class='section-title mt-0'>Analysis</h3>
            <div class='empty-state'>This section is designed for JS-enhanced annotations and model notes. It can be extended with richer overlays if you want the selected ticker to be query-driven.</div>
          </div>
        </div>
        """,
        _sidebar("🔍 Stock Explorer"),
    )


def page_market_analytics(sectors: pd.DataFrame | None = None, recommendations: pd.DataFrame | None = None, risk_return_fig=None) -> str:
    sector_fig = px.bar(sectors, x='Sector', y='avg_predicted_return', color='avg_predicted_return', color_continuous_scale='RdYlGn', title='Sector Performance') if sectors is not None and not sectors.empty else None
    risk_fig = risk_return_fig
  numeric_recommendations = pd.DataFrame()
  if recommendations is not None and not recommendations.empty:
    numeric_recommendations = recommendations.copy()
    numeric_recommendations['Predicted_Return'] = pd.to_numeric(numeric_recommendations['Predicted_Return'], errors='coerce')
    numeric_recommendations = numeric_recommendations.dropna(subset=['Predicted_Return'])
  top_perf = numeric_recommendations.nlargest(5, 'Predicted_Return') if not numeric_recommendations.empty else pd.DataFrame()
  bottom_perf = numeric_recommendations.nsmallest(5, 'Predicted_Return') if not numeric_recommendations.empty else pd.DataFrame()
    return _layout(
      "Market Analytics",
      "Sector and risk-return view built with Bootstrap cards and charts.",
        f"""
        {page_card_grid([
            ("Sectors", f"{len(sectors):,}" if sectors is not None else "0", "Sectors represented in the current universe", "#1f77b4"),
            ("Top names", f"{len(top_perf):,}", "Highest predicted returns", "#2ca02c"),
            ("Bottom names", f"{len(bottom_perf):,}", "Lowest predicted returns", "#d62728"),
            ("Signals", f"{len(recommendations):,}" if recommendations is not None else "0", "Rows available for analysis", "#5d7085"),
        ])}
        <div class='two-col'>
          <div class='card-shell'>
            <h3 class='section-title mt-0'>Sector Performance</h3>
            {_fig_div(sector_fig, 'sector_chart')}
          </div>
          <div class='card-shell'>
            <h3 class='section-title mt-0'>Sector Table</h3>
            {page_table(sectors.assign(avg_predicted_return=sectors['avg_predicted_return'].apply(_fmt_percent), avg_volatility=sectors['avg_volatility'].apply(_fmt_percent)) if sectors is not None and not sectors.empty else sectors, ['Sector', 'stock_count', 'avg_predicted_return', 'avg_volatility']) if sectors is not None and not sectors.empty else '<div class="empty-state">No sector data available.</div>'}
          </div>
        </div>
        <div class='two-col mt-3'>
          <div class='card-shell'>
            <h3 class='section-title mt-0'>Top 5 Performers</h3>
            {page_table(top_perf.assign(Predicted_Return=top_perf['Predicted_Return'].apply(_fmt_percent)) if not top_perf.empty else top_perf, ['Ticker', 'Sector', 'Predicted_Return', 'Recommendation']) if not top_perf.empty else '<div class="empty-state">No top performers available.</div>'}
          </div>
          <div class='card-shell'>
            <h3 class='section-title mt-0'>Bottom 5 Performers</h3>
            {page_table(bottom_perf.assign(Predicted_Return=bottom_perf['Predicted_Return'].apply(_fmt_percent)) if not bottom_perf.empty else bottom_perf, ['Ticker', 'Sector', 'Predicted_Return', 'Recommendation']) if not bottom_perf.empty else '<div class="empty-state">No bottom performers available.</div>'}
          </div>
        </div>
        <div class='card-shell mt-3'>
          <h3 class='section-title mt-0'>Risk vs Return</h3>
          {_fig_div(risk_fig, 'risk_return_chart')}
        </div>
        """,
        _sidebar("📊 Market Analytics"),
    )


def page_model_performance(models: pd.DataFrame | None = None) -> str:
    fig = px.bar(models, x='Model', y='R2', color='R2', color_continuous_scale='RdYlGn', title='R² Scores') if models is not None and not models.empty else None
    return _layout(
        "Model Performance",
        "Model comparison and evaluation metrics, styled as a governance dashboard.",
        f"""
        {page_card_grid([
            ("Models", f"{len(models):,}" if models is not None else "0", "Candidate models evaluated", "#1f77b4"),
            ("Best R²", _fmt_number(models['R2'].max(), 3) if models is not None and not models.empty else "N/A", "Highest score", "#2ca02c"),
            ("Lowest RMSE", _fmt_number(models['RMSE'].min(), 3) if models is not None and not models.empty else "N/A", "Best error rate", "#ff7f0e"),
            ("Lowest MAE", _fmt_number(models['MAE'].min(), 3) if models is not None and not models.empty else "N/A", "Best absolute error", "#d62728"),
        ])}
        <div class='two-col'>
          <div class='card-shell'>
            <h3 class='section-title mt-0'>Evaluation Table</h3>
            {page_table(models.assign(RMSE=models['RMSE'].apply(lambda x: _fmt_number(x, 4)), MAE=models['MAE'].apply(lambda x: _fmt_number(x, 4)), R2=models['R2'].apply(lambda x: _fmt_number(x, 4))) if models is not None and not models.empty else models, ['Model', 'RMSE', 'MAE', 'R2']) if models is not None and not models.empty else '<div class="empty-state">No model data available.</div>'}
          </div>
          <div class='card-shell'>
            <h3 class='section-title mt-0'>Governance Notes</h3>
            <div class='empty-state'>This page is a Bootstrap dashboard view for model selection, error comparisons, and ranking. Add more model diagnostics here if you want ROC or residual analysis.</div>
          </div>
        </div>
        <div class='card-shell mt-3'>
          <h3 class='section-title mt-0'>R² Comparison</h3>
          {_fig_div(fig, 'model_r2_chart')}
        </div>
        """,
        _sidebar("🤖 Model Performance"),
    )


def page_about() -> str:
    return _layout(
        "About & Methodology",
        "A bootstrap-styled method and architecture page.",
        """
        <div class='three-col'>
          <div class='card-shell'>
            <h3 class='section-title mt-0'>Architecture</h3>
            <p>The app is intended to sit on top of a Databricks lakehouse pipeline, with data served from SQL warehouse tables and rendered through a Bootstrap HTML shell.</p>
          </div>
          <div class='card-shell'>
            <h3 class='section-title mt-0'>Methodology</h3>
            <p>Signals are derived from historical features, predicted returns, confidence scores, and risk levels. The dashboard separates signal views from model governance views.</p>
          </div>
          <div class='card-shell'>
            <h3 class='section-title mt-0'>UI System</h3>
            <p>Bootstrap cards, CSS utility classes, and Plotly charts are used to create a more deliberate visual hierarchy than default Streamlit widgets.</p>
          </div>
        </div>
        <div class='card-shell mt-3'>
          <h3 class='section-title mt-0'>Pipeline Flow</h3>
          <div class='empty-state'>Yahoo Finance → Bronze → Silver → Gold → MLflow → Model Registry → Recommendation Engine → SQL Warehouse → Dashboard</div>
        </div>
        <div class='card-shell mt-3'>
          <h3 class='section-title mt-0'>Disclaimer</h3>
          <div class='empty-state'>This application is for research and educational use. Predictions are not guaranteed future performance and should be validated against other sources before making investment decisions.</div>
        </div>
        """,
        _sidebar("ℹ️ About"),
    )