"""Stock Explorer dashboard view."""

import pandas as pd
import plotly.graph_objects as go
from views.shared import (
    _layout,
    _sidebar,
    _fig_div,
    _fmt_percent,
    _fmt_number,
    _to_float,
    _safe_text,
    _generate_insight,
    page_card_grid,
    page_table,
    TICKER_NAMES
)

def page_stock_explorer(stock_recommendation: pd.DataFrame | None = None, stock_features: pd.DataFrame | None = None, selected_ticker: str = "") -> str:
    feature_rows = stock_features.copy() if stock_features is not None else pd.DataFrame()
    rec_row = stock_recommendation.iloc[0] if stock_recommendation is not None and not stock_recommendation.empty else None
    metrics_cards = []
    if rec_row is not None:
        metrics_cards = [
            ("Current Price", _fmt_number(rec_row.get('Close'), prefix='$'), "Latest close price", "#1f77b4"),
            ("Predicted Return", _fmt_percent(rec_row.get('Predicted_Return')), "Model-estimated upside", "#2ca02c"),
            ("Volatility", _fmt_percent(rec_row.get('Volatility')), "Stock price fluctuation intensity", "#9b5de5"),
            ("Confidence", _fmt_number(rec_row.get('Confidence_Score'), 0, suffix='/10'), "Signal confidence", "#ff7f0e"),
            ("Risk", _safe_text(rec_row.get('Risk_Level')), "Risk classification", "#d62728"),
        ]
    if not feature_rows.empty:
        fig = go.Figure()
        # Add Candlestick for price action
        fig.add_trace(go.Candlestick(
            x=feature_rows['Date'],
            open=feature_rows['Open'],
            high=feature_rows['High'],
            low=feature_rows['Low'],
            close=feature_rows['Close'],
            name='OHLC Price',
            increasing_line_color='#2ca02c',
            decreasing_line_color='#d62728'
        ))
        # Add SMA_7
        fig.add_trace(go.Scatter(
            x=feature_rows['Date'],
            y=feature_rows['SMA_7'],
            mode='lines',
            name='7-Day SMA',
            line=dict(color='#ff7f0e', width=1.5)
        ))
        # Add SMA_30
        fig.add_trace(go.Scatter(
            x=feature_rows['Date'],
            y=feature_rows['SMA_30'],
            mode='lines',
            name='30-Day SMA',
            line=dict(color='#1f77b4', width=1.5)
        ))
        fig.update_layout(
            title='Historical Price Action & Technical Indicators (Interactive OHLC + Moving Averages)',
            yaxis_title='Price ($)',
            xaxis_title='Date',
            hovermode='x unified',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            margin=dict(t=50, b=100, l=50, r=20)
        )
        # Add rangeslider and rangeselector buttons
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1D", step="day", stepmode="backward"),
                    dict(count=5, label="5D", step="day", stepmode="backward"),
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=3, label="3M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all", label="MAX")
                ]),
                bgcolor="rgba(15, 39, 71, 0.05)",
                activecolor="rgba(31, 119, 180, 0.2)",
                font=dict(color="#0f2747", size=11),
                y=-0.45,
                x=0,
                yanchor="top",
                xanchor="left"
            )
        )
        price_fig = fig
    else:
        price_fig = None
    
    ticker_name = TICKER_NAMES.get(selected_ticker, "")
    display_title = f"Stock Explorer - {selected_ticker} ({ticker_name})" if selected_ticker else "Stock Explorer"
    
    # Format historical rows for display
    display_features = pd.DataFrame()
    if not feature_rows.empty:
        display_features = feature_rows.tail(12).copy()
        display_features = display_features.assign(
            Close=display_features['Close'].apply(lambda x: _fmt_number(x, prefix='$')),
            Daily_Return=display_features['Daily_Return'].apply(_fmt_percent),
            Volatility=display_features['Volatility'].apply(lambda x: f"{_to_float(x)/100:.4f}"),
            SMA_7=display_features['SMA_7'].apply(lambda x: _fmt_number(x, prefix='$')),
            SMA_30=display_features['SMA_30'].apply(lambda x: _fmt_number(x, prefix='$')),
        )

    explanation_html = ""
    if rec_row is not None:
        insight = _generate_insight(rec_row)
        explanation_html = f"""
        <div class='card-shell mb-3' style='border-left: 5px solid var(--accent); background: rgba(31,119,180,0.05);'>
          <h4 class='mt-0' style='color: var(--accent); font-weight: 700;'>Analyst Insight & Strategy</h4>
          <p class='mb-0' style='font-size: 1.05rem; line-height: 1.55; color: #1a304e;'>{insight}</p>
        </div>
        """

    return _layout(
        display_title,
        "Single-stock deep dive with historical price action, returns, volatility, and technical indicators.",
        f"""
        {page_card_grid(metrics_cards) if metrics_cards else '<div class="empty-state">Select a stock to view detailed metrics.</div>'}
        {explanation_html}
        <div class='card-shell mb-3'>
          <strong>Stock profile:</strong> {selected_ticker or 'Select a ticker from the app shell'}
        </div>
        <div class='section-title'>Price History</div>
        {_fig_div(price_fig, 'stock_price')}
        <div class='two-col'>
          <div class='card-shell'>
            <h3 class='section-title mt-0'>Technical Summary</h3>
            {page_table(display_features, ['Date', 'Close', 'Daily_Return', 'Volatility', 'SMA_7', 'SMA_30']) if not display_features.empty else '<div class="empty-state">No historical rows available.</div>'}
          </div>
          <div class='card-shell'>
            <h3 class='section-title mt-0'>Analysis</h3>
            <div class='empty-state'>This section is designed for JS-enhanced annotations and model notes. It can be extended with richer volatility insights to clarify key stock indicators.</div>
          </div>
        </div>
        """,
        _sidebar("Stock Explorer"),
    )
