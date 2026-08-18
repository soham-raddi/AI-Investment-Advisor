"""Market analytics page."""

import streamlit as st

from components import charts
from data import queries
from formatters import safe_percent_format
from dashboard_pages.shared import render_hero


def show_market_analytics():
    render_hero(
        "Market Analytics",
        "Compare sector-level performance, review the strongest and weakest names, and inspect the risk-return tradeoff across the recommendation universe.",
        eyebrow="Cross-Section View",
    )

    sectors = queries.get_sector_analysis()
    recommendations = queries.get_recommendations()
    risk_return = queries.get_risk_return_data()

    st.markdown('<div class="section-header">Sector Performance</div>', unsafe_allow_html=True)

    if not sectors.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(charts.create_sector_bar(sectors), use_container_width=True)
        with col2:
            st.dataframe(
                sectors[['Sector', 'stock_count', 'avg_predicted_return', 'avg_volatility']]
                .rename(columns={
                    'stock_count': 'Stocks',
                    'avg_predicted_return': 'Avg Return (%)',
                    'avg_volatility': 'Avg Volatility (%)'
                }),
                use_container_width=True
            )

        top_sector = sectors.sort_values('avg_predicted_return', ascending=False).iloc[0]
        st.markdown(
            f"""
            <div class="callout-box">
                <strong>Best-performing sector:</strong> {top_sector['Sector']} with an average predicted return of {safe_percent_format(top_sector['avg_predicted_return'])}.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-header">Top & Bottom Performers</div>', unsafe_allow_html=True)

    if not recommendations.empty:
        col3, col4 = st.columns(2)

        with col3:
            st.subheader("🏆 Top 5 Performers")
            top_performers = recommendations.nlargest(5, 'Predicted_Return')[[
                'Ticker', 'Sector', 'Predicted_Return', 'Recommendation'
            ]]
            st.dataframe(top_performers, use_container_width=True, hide_index=True)

        with col4:
            st.subheader("⚠️ Bottom 5 Performers")
            bottom_performers = recommendations.nsmallest(5, 'Predicted_Return')[[
                'Ticker', 'Sector', 'Predicted_Return', 'Recommendation'
            ]]
            st.dataframe(bottom_performers, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-header">Risk vs Return Analysis</div>', unsafe_allow_html=True)
    if not risk_return.empty:
        st.plotly_chart(charts.create_risk_return_scatter(risk_return), use_container_width=True)
