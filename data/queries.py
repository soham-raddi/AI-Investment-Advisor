"""Data query functions for the Investment Advisor app."""

import streamlit as st
from .database import get_database_connection


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_recommendations():
    """Get all investment recommendations."""
    query = """
    SELECT 
        Date,
        Ticker,
        Sector,
        Close,
        Predicted_Return,
        Recommendation,
        Confidence_Score,
        Risk_Level,
        Explanation,
        Volatility
    FROM workspace.investment_db.investment_recommendations
    ORDER BY Predicted_Return DESC
    """
    db = get_database_connection()
    return db.execute_query(query)


@st.cache_data(ttl=300)
def get_recommendation_summary():
    """Get summary statistics for recommendations."""
    query = """
    SELECT 
        COUNT(*) as total_stocks,
        SUM(CASE WHEN Recommendation = 'BUY' THEN 1 ELSE 0 END) as buy_count,
        SUM(CASE WHEN Recommendation = 'HOLD' THEN 1 ELSE 0 END) as hold_count,
        SUM(CASE WHEN Recommendation = 'AVOID' THEN 1 ELSE 0 END) as avoid_count,
        AVG(Predicted_Return) as avg_predicted_return,
        AVG(Confidence_Score) as avg_confidence
    FROM workspace.investment_db.investment_recommendations
    """
    db = get_database_connection()
    return db.execute_query(query)


@st.cache_data(ttl=300)
def get_stock_list():
    """Get list of all stock tickers."""
    query = """
    SELECT DISTINCT Ticker, Sector
    FROM workspace.investment_db.investment_recommendations
    ORDER BY Ticker
    """
    db = get_database_connection()
    return db.execute_query(query)


@st.cache_data(ttl=300)
def get_stock_features(ticker):
    """Get historical features for a specific stock."""
    query = """
    SELECT 
        Date,
        Close,
        High,
        Low,
        Open,
        Volume,
        Ticker,
        Sector,
        Daily_Return,
        SMA_7,
        SMA_30,
        Volatility
    FROM workspace.investment_db.gold_stock_features
    WHERE Ticker = :ticker
    ORDER BY Date
    """
    db = get_database_connection()
    return db.execute_query(query, {'ticker': ticker})


@st.cache_data(ttl=300)
def get_stock_recommendation(ticker):
    """Get recommendation for a specific stock."""
    query = """
    SELECT 
        Date,
        Ticker,
        Sector,
        Close,
        Predicted_Return,
        Recommendation,
        Confidence_Score,
        Risk_Level,
        Explanation,
        Volatility
    FROM workspace.investment_db.investment_recommendations
    WHERE Ticker = :ticker
    """
    db = get_database_connection()
    return db.execute_query(query, {'ticker': ticker})


@st.cache_data(ttl=300)
def get_sector_analysis():
    """Get sector-level analysis."""
    query = """
    SELECT 
        Sector,
        COUNT(*) as stock_count,
        AVG(Predicted_Return) as avg_predicted_return,
        AVG(Volatility) as avg_volatility,
        AVG(Confidence_Score) as avg_confidence
    FROM workspace.investment_db.investment_recommendations
    GROUP BY Sector
    ORDER BY avg_predicted_return DESC
    """
    db = get_database_connection()
    return db.execute_query(query)


@st.cache_data(ttl=300)
def get_model_comparison():
    """Get model performance comparison."""
    query = """
    SELECT 
        Model,
        RMSE,
        MAE,
        R2
    FROM workspace.investment_db.model_comparison
    ORDER BY R2 DESC
    """
    db = get_database_connection()
    return db.execute_query(query)


@st.cache_data(ttl=300)
def get_recommendation_distribution():
    """Get distribution of recommendations."""
    query = """
    SELECT 
        Recommendation,
        COUNT(*) as count
    FROM workspace.investment_db.investment_recommendations
    GROUP BY Recommendation
    """
    db = get_database_connection()
    return db.execute_query(query)


@st.cache_data(ttl=300)
def get_risk_return_data():
    """Get risk vs return data for scatter plot."""
    query = """
    SELECT 
        Ticker,
        Sector,
        Predicted_Return,
        Volatility,
        Risk_Level,
        Recommendation
    FROM workspace.investment_db.investment_recommendations
    """
    db = get_database_connection()
    return db.execute_query(query)