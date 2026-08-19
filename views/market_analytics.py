"""Market Analytics dashboard view."""

import pandas as pd
import plotly.express as px
from views.shared import (
    _layout,
    _sidebar,
    _fig_div,
    _fmt_percent,
    _to_float,
    page_card_grid,
    page_table
)

def page_market_analytics(sectors: pd.DataFrame | None = None, recommendations: pd.DataFrame | None = None, risk_return_fig=None) -> str:
    sector_fig = px.bar(
        sectors, 
        x='Sector', 
        y='avg_predicted_return', 
        color='Sector', 
        title='Sector Performance',
        color_discrete_sequence=px.colors.qualitative.Bold
    ) if sectors is not None and not sectors.empty else None
    risk_fig = px.scatter(
        risk_return_fig,
        x='Volatility',
        y='Predicted_Return',
        color='Recommendation',
        hover_name='Ticker',
        hover_data=['Sector', 'Risk_Level'],
        title='Risk vs Return Profile',
        color_discrete_map={'BUY': '#2ca02c', 'HOLD': '#ff7f0e', 'AVOID': '#d62728'}
    ) if risk_return_fig is not None and not risk_return_fig.empty else None
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
            {page_table(top_perf.assign(Predicted_Return=top_perf['Predicted_Return'].apply(_fmt_percent), Volatility=top_perf['Volatility'].apply(lambda x: f"{_to_float(x)/100:.4f}")) if not top_perf.empty else top_perf, ['Ticker', 'Sector', 'Predicted_Return', 'Volatility', 'Recommendation']) if not top_perf.empty else '<div class="empty-state">No top performers available.</div>'}
          </div>
          <div class='card-shell'>
            <h3 class='section-title mt-0'>Bottom 5 Performers</h3>
            {page_table(bottom_perf.assign(Predicted_Return=bottom_perf['Predicted_Return'].apply(_fmt_percent), Volatility=bottom_perf['Volatility'].apply(lambda x: f"{_to_float(x)/100:.4f}")) if not bottom_perf.empty else bottom_perf, ['Ticker', 'Sector', 'Predicted_Return', 'Volatility', 'Recommendation']) if not bottom_perf.empty else '<div class="empty-state">No bottom performers available.</div>'}
          </div>
        </div>
        <div class='card-shell mt-3'>
          <h3 class='section-title mt-0'>Risk vs Return</h3>
          {_fig_div(risk_fig, 'risk_return_chart')}
        </div>
        """,
        _sidebar("Market Analytics"),
    )
