"""Recommendations page."""

import streamlit as st

from data import queries
from dashboard_pages.shared import render_hero, render_metric_card
from formatters import safe_decimal_format, safe_percent_format


def show_recommendations():
    render_hero(
        "Investment Recommendations",
        "Filter the model outputs by ticker, sector, recommendation type, or risk band, then open a stock to inspect the detailed rationale behind each signal.",
        eyebrow="Filterable Signal Library",
    )

    recommendations = queries.get_recommendations()

    if recommendations.empty:
        st.warning("No recommendations available")
        return

    positive_share = (recommendations['Recommendation'] == 'BUY').mean() * 100
    risk_share = (recommendations['Risk_Level'] == 'HIGH').mean() * 100

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        render_metric_card("Signal breadth", f"{len(recommendations):,}", "Total recommendation rows available for review", accent="blue")
    with col_b:
        render_metric_card("BUY ratio", f"{positive_share:.1f}%", "Share of the universe currently flagged as BUY", accent="green")
    with col_c:
        render_metric_card("High-risk share", f"{risk_share:.1f}%", "Portion of stocks carrying a HIGH risk tag", accent="red")

    st.markdown('<div class="section-header">Filter Recommendations</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        tickers = ['All'] + sorted(recommendations['Ticker'].unique().tolist())
        selected_ticker = st.selectbox("Ticker", tickers)

    with col2:
        sectors = ['All'] + sorted(recommendations['Sector'].unique().tolist())
        selected_sector = st.selectbox("Sector", sectors)

    with col3:
        rec_types = ['All'] + sorted(recommendations['Recommendation'].unique().tolist())
        selected_rec = st.selectbox("Recommendation", rec_types)

    with col4:
        risk_levels = ['All'] + sorted(recommendations['Risk_Level'].unique().tolist())
        selected_risk = st.selectbox("Risk Level", risk_levels)

    filtered = recommendations.copy()
    if selected_ticker != 'All':
        filtered = filtered[filtered['Ticker'] == selected_ticker]
    if selected_sector != 'All':
        filtered = filtered[filtered['Sector'] == selected_sector]
    if selected_rec != 'All':
        filtered = filtered[filtered['Recommendation'] == selected_rec]
    if selected_risk != 'All':
        filtered = filtered[filtered['Risk_Level'] == selected_risk]

    st.markdown(f'<div class="section-header">Results ({len(filtered)} stocks)</div>', unsafe_allow_html=True)

    if filtered.empty:
        st.info("No recommendations match the selected filters")
        return

    display_df = filtered[[
        'Ticker', 'Sector', 'Close', 'Predicted_Return',
        'Recommendation', 'Confidence_Score', 'Risk_Level'
    ]].copy()

    display_df.columns = ['Ticker', 'Sector', 'Price ($)', 'Predicted Return', 'Recommendation', 'Confidence', 'Risk']
    display_df['Predicted Return'] = display_df['Predicted Return'].apply(safe_percent_format)
    display_df['Price ($)'] = display_df['Price ($)'].apply(lambda x: safe_decimal_format(x, prefix='$'))
    display_df['Confidence'] = display_df['Confidence'].apply(lambda x: safe_decimal_format(x, decimals=0, suffix='/10'))

    st.dataframe(display_df, use_container_width=True, height=400)

    st.markdown(
        """
        <div class="callout-box">
            <strong>Table tip:</strong> Use the expanders below for the model explanation. The table is designed for scanning; the expander view is where the decision rationale, risk level, and return profile are detailed.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-header">Detailed Analysis</div>', unsafe_allow_html=True)
    for _, row in filtered.iterrows():
        with st.expander(f"{row['Ticker']} - {row['Recommendation']}"):
            col_a, col_b = st.columns([1, 2])
            with col_a:
                st.metric("Price", safe_decimal_format(row['Close'], prefix='$'))
                st.metric("Predicted Return", safe_percent_format(row['Predicted_Return']))
                st.metric("Confidence", safe_decimal_format(row['Confidence_Score'], decimals=0, suffix='/10'))
            with col_b:
                st.markdown(f"**Sector:** {row['Sector']}")
                st.markdown(f"**Risk Level:** {row['Risk_Level']}")
                st.markdown(f"**Volatility:** {safe_percent_format(row['Volatility'])}")
                st.info(f"**Analysis:** {row['Explanation']}")
