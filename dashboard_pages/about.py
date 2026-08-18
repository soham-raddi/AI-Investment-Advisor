"""About and methodology page."""

import streamlit as st

from dashboard_pages.shared import render_hero


def show_about():
    render_hero(
        "About & Methodology",
        "This application is built on a Databricks-style Lakehouse pipeline with MLflow tracking, model scoring, and a Streamlit front end for exploring the results.",
        eyebrow="System Overview",
    )

    st.markdown('<div class="section-header">System Architecture</div>', unsafe_allow_html=True)

    st.markdown("""
    This AI-Powered Investment Advisor is built on the **Databricks Lakehouse Medallion Architecture**.

    ### Data Pipeline Flow

    ```
    Yahoo Finance API
            ↓
    📦 Bronze Layer (Raw Data Ingestion)
            ↓
    🧹 Silver Layer (Data Cleaning & Validation)
            ↓
    ✨ Gold Layer (Feature Engineering)
            ↓
        ┌───────┴───────┐
        ↓               ↓
    🤖 Spark ML      📊 SQL Analytics
        ↓
    📈 MLflow Tracking
        ↓
    🎯 Registered Model
        ↓
    💡 Recommendation Engine
        ↓
    📋 Recommendations Table
        ↓
    🗄️ SQL Warehouse
        ↓
    📱 Databricks App (This Interface)
    ```
    """)

    st.markdown('<div class="section-header">Layer Descriptions</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Bronze Layer**
        * Raw data ingestion from Yahoo Finance
        * Historical stock prices and volumes
        * Minimal transformation
        * Data lineage tracking

        **Silver Layer**
        * Data cleaning and validation
        * Handling missing values
        * Data type standardization
        * Quality checks
        """)

    with col2:
        st.markdown("""
        **Gold Layer**
        * Feature engineering
        * Technical indicators (SMA, volatility)
        * Return calculations
        * ML-ready datasets

        **ML Pipeline**
        * Spark MLlib for distributed training
        * Multiple model comparison
        * MLflow for experiment tracking
        * Automated model selection
        """)

    st.markdown('<div class="section-header">Recommendation Logic</div>', unsafe_allow_html=True)

    st.markdown("""
    Investment recommendations are generated using the following logic:

    * **BUY**: Predicted return > threshold AND high confidence AND acceptable risk
    * **HOLD**: Moderate predicted return OR medium confidence
    * **AVOID**: Negative predicted return OR high risk

    Each recommendation includes:
    * Predicted return percentage
    * Confidence score (0-10)
    * Risk level (LOW/MEDIUM/HIGH)
    * Detailed explanation
    """)

    st.markdown('<div class="section-header">Technologies Used</div>', unsafe_allow_html=True)

    col3, col4, col5 = st.columns(3)

    with col3:
        st.markdown("""
        **Data Platform**
        * Databricks Lakehouse
        * Unity Catalog
        * Delta Lake
        * SQL Warehouse
        """)

    with col4:
        st.markdown("""
        **ML & Analytics**
        * Spark MLlib
        * MLflow
        * PySpark
        * SQL
        """)

    with col5:
        st.markdown("""
        **Application**
        * Databricks Apps
        * Streamlit
        * Plotly
        * Python
        """)

    st.markdown('<div class="section-header">⚠️ Disclaimer</div>', unsafe_allow_html=True)

    st.warning("""
    **Important Notice:**

    This investment advisor is powered by machine learning models and is intended for
    **research and educational purposes only**.

    * Predictions are based on historical data and may not reflect future performance
    * Stock market investing involves risk, including potential loss of principal
    * This is NOT guaranteed financial advice
    * Always consult with a qualified financial advisor before making investment decisions
    * Past performance does not guarantee future results

    Use this tool as one of many inputs in your investment research process.
    """)
