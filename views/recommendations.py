"""Recommendations dashboard view."""

import pandas as pd
import plotly.express as px
from views.shared import (
    _layout,
    _sidebar,
    _fig_div,
    _fmt_percent,
    _fmt_number,
    _to_float,
    _generate_insight,
    page_card_grid,
    page_table
)

def page_recommendations(recommendations: pd.DataFrame) -> str:
    top_rows = recommendations.head(12).copy() if recommendations is not None and not recommendations.empty else pd.DataFrame()
    display_rows = top_rows.copy()
    if not top_rows.empty:
        display_rows = top_rows.assign(
            Close=top_rows['Close'].apply(lambda x: _fmt_number(x, prefix='$')),
            Predicted_Return=top_rows['Predicted_Return'].apply(_fmt_percent),
            Volatility=top_rows['Volatility'].apply(lambda x: f"{_to_float(x)/100:.4f}"),
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
          <strong>Recommendation library:</strong> This page shows the top names returned by the model. Use the table to scan by ticker, sector, return, confidence, volatility, and risk level.
        </div>
        <div class='section-title'>Top Recommendations</div>
        {_fig_div(px.bar(recommendations.head(12) if recommendations is not None and not recommendations.empty else recommendations.head(1), x='Ticker', y='Predicted_Return', color='Ticker', title='Top Recommendations', color_discrete_sequence=px.colors.qualitative.Safe) if recommendations is not None and not recommendations.empty else None, 'rec_bar')}
        <div class='card-shell mt-3'>
          <h3 class='section-title mt-0'>Recommendation Table</h3>
          {page_table(display_rows, ['Ticker', 'Sector', 'Close', 'Predicted_Return', 'Recommendation', 'Confidence_Score', 'Risk_Level', 'Volatility']) if not display_rows.empty else '<div class="empty-state">No recommendations available.</div>'}
        </div>
        """,
        _sidebar("Recommendations"),
    )
