"""Model performance page."""

import streamlit as st

from components import charts
from data import queries
from dashboard_pages.shared import render_hero


def show_model_performance():
    render_hero(
        "Model Performance",
        "Review the evaluation metrics that back the recommendation engine and compare how the candidate models perform on the held-out test set.",
        eyebrow="Model Governance",
    )

    models = queries.get_model_comparison()

    if models.empty:
        st.warning("No model performance data available")
        return

    st.markdown('<div class="section-header">Model Evaluation Metrics</div>', unsafe_allow_html=True)

    best_model = models.iloc[0]
    st.success(f"**Best Performing Model: {best_model['Model']}** (Highest R² Score)")

    st.markdown(
        """
        <div class="callout-box">
            <strong>What this page adds:</strong> It explains how the recommendation engine was selected, what the error metrics mean, and how to interpret the model comparison charts before trusting the output.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.dataframe(
            models.style.highlight_max(subset=['R2'], color='lightgreen')
                       .highlight_min(subset=['RMSE', 'MAE'], color='lightgreen'),
            use_container_width=True,
            hide_index=True
        )

    with col2:
        st.markdown("""
        **Metric Definitions:**

        * **RMSE** (Root Mean Squared Error): Measures average prediction error. Lower is better.
        * **MAE** (Mean Absolute Error): Average absolute difference between predicted and actual values. Lower is better.
        * **R²** (R-Squared): Proportion of variance explained by the model. Higher is better (max 1.0).
        """)

    st.markdown('<div class="section-header">Visual Comparison</div>', unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(charts.create_model_comparison_bar(models), use_container_width=True)
    with col4:
        st.plotly_chart(charts.create_r2_bar(models), use_container_width=True)

    st.markdown('<div class="section-header">Key Insights</div>', unsafe_allow_html=True)
    st.info("""
    The models were trained on historical stock data using Spark MLlib.
    Performance metrics are calculated on a held-out test set.
    The best-performing model is used to generate investment recommendations.
    """)
