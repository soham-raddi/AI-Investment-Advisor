"""Shared page helpers for the investment advisor app."""

import streamlit as st

from formatters import safe_decimal_format, safe_percent_format


def to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def render_hero(title, subtitle, eyebrow="Dashboard"):
    st.markdown(
        f"""
        <div class="hero-panel">
            <div class="hero-eyebrow">{eyebrow}</div>
            <div class="hero-title">{title}</div>
            <p class="hero-copy">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label, value, subtitle, accent="blue"):
    accent_color = {
        "blue": "#1f77b4",
        "green": "#2ca02c",
        "orange": "#ff7f0e",
        "red": "#d62728",
        "slate": "#5d7085",
    }.get(accent, "#1f77b4")

    st.markdown(
        f"""
        <div class="metric-card" style="border-top: 4px solid {accent_color}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_recommendation_card(row, tone):
    palette = {
        "buy": {"bg": "linear-gradient(135deg, rgba(46, 204, 113, 0.14), rgba(46, 204, 113, 0.06))", "accent": "#2ca02c"},
        "avoid": {"bg": "linear-gradient(135deg, rgba(214, 39, 40, 0.12), rgba(214, 39, 40, 0.05))", "accent": "#d62728"},
    }
    style = palette.get(tone, palette["buy"])

    st.markdown(
        f"""
        <div class="detail-card" style="background:{style['bg']}; border-top: 4px solid {style['accent']}">
            <h4>{row['Ticker']} <span style="font-weight:400; color:#526170">{row['Sector']}</span></h4>
            <div class="detail-row"><span>Predicted return</span><span><b>{safe_percent_format(row['Predicted_Return'])}</b></span></div>
            <div class="detail-row"><span>Confidence</span><span><b>{safe_decimal_format(row['Confidence_Score'], decimals=0, suffix='/10')}</b></span></div>
            <div class="detail-row"><span>Risk level</span><span><b>{row['Risk_Level']}</b></span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
