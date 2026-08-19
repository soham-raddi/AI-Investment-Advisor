"""Shared helpers, variables, and configs for all views."""

from __future__ import annotations
import json
import pandas as pd

TICKER_NAMES = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Google",
    "AMZN": "Amazon",
    "TSLA": "Tesla",
    "META": "Meta",
    "NVDA": "NVIDIA",
    "NFLX": "Netflix",
    "JPM": "JPMorgan",
    "WMT": "Walmart"
}


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


def _generate_insight(row):
    ticker = _safe_text(row.get('Ticker'))
    name = TICKER_NAMES.get(ticker, ticker)
    pred_return = _to_float(row.get('Predicted_Return'))
    vol = _to_float(row.get('Volatility'))
    vol_dec = vol / 100
    risk = _safe_text(row.get('Risk_Level')).upper()
    rec = _safe_text(row.get('Recommendation')).upper()
    
    # Format return as percentage for text
    ret_pct = f"{pred_return:.2%}"
    
    if rec == "BUY":
        if risk == "LOW":
            return f"Strong Buy: {ticker} ({name}) demonstrates highly favorable upward momentum of {ret_pct} backed by a conservative volatility profile ({vol_dec:.4f}). This low-risk profile makes it a stellar core holding for defensive portfolios."
        else:
            return f"Buy: {ticker} ({name}) exhibits robust predicted gains of {ret_pct} with manageable price fluctuations (volatility of {vol_dec:.4f}). Excellent growth prospects with reasonable risk-reward dynamics."
    elif rec == "HOLD":
        return f"Hold: {ticker} ({name}) presents moderate forecasted returns of {ret_pct} alongside standard volatility ({vol_dec:.4f}). Recommend maintaining current exposure while waiting for a stronger entry point."
    elif rec == "AVOID":
        if pred_return < 0:
            return f"Avoid: {ticker} ({name}) displays negative predicted returns ({ret_pct}) combined with elevated price instability (volatility of {vol_dec:.4f}). Recommend capital preservation and avoiding exposure."
        else:
            return f"Speculative / Avoid: {ticker} ({name}) shows positive forecasted return of {ret_pct} but is heavily offset by excessive price swings (volatility of {vol_dec:.4f}). Risk outweighs potential upside."
    else:
        return f"Neutral stance for {ticker}. Volatility is stable at {vol_dec:.4f} with predicted returns of {ret_pct}."


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
    return f"<div class='chart-shell' id='{element_id}'></div><script>drawPlotlyChart('{element_id}', {fig.to_json()});</script>"


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
      <script>
        function drawPlotlyChart(elementId, figure) {{
          if (!figure) return;
          figure.layout = figure.layout || {{}};
          figure.layout.autosize = true;
          delete figure.layout.width;
          delete figure.layout.height;
          figure.layout.margin = figure.layout.margin || {{ t: 40, b: 40, l: 50, r: 20 }};
          setTimeout(() => {{
            const el = document.getElementById(elementId);
            if (el) {{
              Plotly.newPlot(elementId, figure.data, figure.layout, {{responsive: true, displayModeBar: false}});
            }}
          }}, 100);
        }}
      </script>
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
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin: 18px 0; }}
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
        .chart-shell {{ background: white; border-radius: 18px; padding: 8px; box-shadow: 0 12px 24px rgba(15, 39, 71, .06); margin-bottom: 14px; min-height: 480px; }}
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
