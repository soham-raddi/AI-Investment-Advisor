"""Stock explorer page."""

import streamlit as st

from components import charts, metrics
from data import queries
from dashboard_pages.shared import render_hero


def show_stock_explorer():
    render_hero(
        "Stock Explorer",
        "Pick one ticker and inspect the full history, volatility, returns, and technical indicators behind the recommendation engine's output.",
        eyebrow="Single-Stock Deep Dive",
    )

    stock_list = queries.get_stock_list()

    if stock_list.empty:
        st.warning("No stocks available")
        return

    selected_ticker = st.selectbox(
        "Select a stock to explore",
        stock_list['Ticker'].tolist(),
        format_func=lambda x: f"{x} - {stock_list[stock_list['Ticker']==x]['Sector'].iloc[0]}"
    )

    stock_rec = queries.get_stock_recommendation(selected_ticker)
    stock_features = queries.get_stock_features(selected_ticker)

    if stock_rec.empty or stock_features.empty:
        st.warning(f"No data available for {selected_ticker}")
        return

    st.markdown(
        f"""
        <div class="callout-box">
            <strong>Selected stock:</strong> {selected_ticker} | <strong>Sector:</strong> {stock_rec.iloc[0]['Sector']} | <strong>Recommendation:</strong> {stock_rec.iloc[0]['Recommendation']}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-header">Stock Overview</div>', unsafe_allow_html=True)
    metrics.display_stock_metrics(stock_rec)

    st.markdown('<div class="section-header">Historical Performance</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["Price", "Returns", "Volatility", "Technical Indicators"])

    with tab1:
        st.plotly_chart(charts.create_price_chart(stock_features), use_container_width=True)

    with tab2:
        st.plotly_chart(charts.create_return_chart(stock_features), use_container_width=True)

    with tab3:
        st.plotly_chart(charts.create_volatility_chart(stock_features), use_container_width=True)

    with tab4:
        st.plotly_chart(charts.create_sma_chart(stock_features), use_container_width=True)
