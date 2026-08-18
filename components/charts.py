"""Chart components for visualizations."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_price_chart(df):
    """Create interactive price over time chart."""
    fig = px.line(
        df, 
        x='Date', 
        y='Close',
        title='Historical Closing Price',
        labels={'Close': 'Price ($)', 'Date': 'Date'}
    )
    fig.update_traces(line_color='#1f77b4', line_width=2)
    fig.update_layout(
        hovermode='x unified',
        plot_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='lightgray'),
        yaxis=dict(showgrid=True, gridcolor='lightgray')
    )
    return fig


def create_return_chart(df):
    """Create daily return chart."""
    fig = go.Figure()
    
    colors = ['green' if x >= 0 else 'red' for x in df['Daily_Return']]
    
    fig.add_trace(go.Bar(
        x=df['Date'],
        y=df['Daily_Return'],
        marker_color=colors,
        name='Daily Return'
    ))
    
    fig.update_layout(
        title='Daily Returns',
        xaxis_title='Date',
        yaxis_title='Return (%)',
        hovermode='x unified',
        plot_bgcolor='white',
        showlegend=False
    )
    return fig


def create_volatility_chart(df):
    """Create volatility over time chart."""
    fig = px.line(
        df,
        x='Date',
        y='Volatility',
        title='Volatility Over Time',
        labels={'Volatility': 'Volatility (%)', 'Date': 'Date'}
    )
    fig.update_traces(line_color='#ff7f0e', line_width=2)
    fig.update_layout(
        hovermode='x unified',
        plot_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='lightgray'),
        yaxis=dict(showgrid=True, gridcolor='lightgray')
    )
    return fig


def create_sma_chart(df):
    """Create chart with price and moving averages."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['Close'],
        mode='lines',
        name='Price',
        line=dict(color='#1f77b4', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['SMA_7'],
        mode='lines',
        name='SMA 7',
        line=dict(color='#2ca02c', width=1.5, dash='dash')
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['SMA_30'],
        mode='lines',
        name='SMA 30',
        line=dict(color='#d62728', width=1.5, dash='dot')
    ))
    
    fig.update_layout(
        title='Price with Moving Averages',
        xaxis_title='Date',
        yaxis_title='Price ($)',
        hovermode='x unified',
        plot_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='lightgray'),
        yaxis=dict(showgrid=True, gridcolor='lightgray')
    )
    return fig


def create_recommendation_pie(df):
    """Create pie chart for recommendation distribution."""
    colors = {'BUY': '#2ca02c', 'HOLD': '#ff7f0e', 'AVOID': '#d62728'}
    fig = px.pie(
        df,
        values='count',
        names='Recommendation',
        title='Recommendation Distribution',
        color='Recommendation',
        color_discrete_map=colors
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig


def create_sector_bar(df):
    """Create bar chart for sector performance."""
    fig = px.bar(
        df,
        x='Sector',
        y='avg_predicted_return',
        title='Average Predicted Return by Sector',
        labels={'avg_predicted_return': 'Avg Predicted Return (%)', 'Sector': 'Sector'},
        color='avg_predicted_return',
        color_continuous_scale='RdYlGn'
    )
    fig.update_layout(
        plot_bgcolor='white',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='lightgray')
    )
    return fig


def create_risk_return_scatter(df):
    """Create risk vs return scatter plot."""
    color_map = {'BUY': '#2ca02c', 'HOLD': '#ff7f0e', 'AVOID': '#d62728'}

    plot_df = df.copy()
    plot_df['Volatility'] = pd.to_numeric(plot_df['Volatility'], errors='coerce')
    plot_df['Predicted_Return'] = pd.to_numeric(plot_df['Predicted_Return'], errors='coerce')
    plot_df = plot_df.dropna(subset=['Volatility', 'Predicted_Return', 'Recommendation'])
    plot_df['Marker_Size'] = plot_df['Predicted_Return'].abs().clip(lower=0.1)
    
    fig = px.scatter(
        plot_df,
        x='Volatility',
        y='Predicted_Return',
        color='Recommendation',
        size='Marker_Size',
        hover_data=['Ticker', 'Sector'],
        title='Risk vs Return Analysis',
        labels={
            'Volatility': 'Risk (Volatility %)',
            'Predicted_Return': 'Predicted Return (%)'
        },
        size_max=18,
        color_discrete_map=color_map
    )
    
    fig.update_layout(
        plot_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='lightgray'),
        yaxis=dict(showgrid=True, gridcolor='lightgray')
    )
    return fig


def create_model_comparison_bar(df):
    """Create bar chart comparing model performance."""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='RMSE',
        x=df['Model'],
        y=df['RMSE'],
        marker_color='#1f77b4'
    ))
    
    fig.add_trace(go.Bar(
        name='MAE',
        x=df['Model'],
        y=df['MAE'],
        marker_color='#ff7f0e'
    ))
    
    fig.update_layout(
        title='Model Performance Comparison (Lower is Better)',
        xaxis_title='Model',
        yaxis_title='Error Metric',
        barmode='group',
        plot_bgcolor='white',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='lightgray')
    )
    return fig


def create_r2_bar(df):
    """Create bar chart for R2 scores."""
    fig = px.bar(
        df,
        x='Model',
        y='R2',
        title='Model R² Scores (Higher is Better)',
        labels={'R2': 'R² Score', 'Model': 'Model'},
        color='R2',
        color_continuous_scale='RdYlGn'
    )
    fig.update_layout(
        plot_bgcolor='white',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='lightgray')
    )
    return fig