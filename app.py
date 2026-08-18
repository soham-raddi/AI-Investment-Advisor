"""AI-Powered Investment Advisor - Databricks App

Production-style interactive application for investment recommendations
built on top of the Databricks Lakehouse Medallion Architecture.
"""

import streamlit as st
import streamlit.components.v1 as components
import sys
from pathlib import Path
import traceback
from urllib.parse import parse_qs

# Add local modules to path
sys.path.insert(0, str(Path(__file__).parent))

# Try to import page modules with error handling
try:
    from html_renderer import (
        page_about,
        page_market_analytics,
        page_model_performance,
        page_overview,
        page_recommendations,
        page_stock_explorer,
    )
    from data import queries
    IMPORTS_SUCCESSFUL = True
    IMPORT_ERROR = None
except Exception as e:
    IMPORTS_SUCCESSFUL = False
    IMPORT_ERROR = str(e)
    IMPORT_TRACEBACK = traceback.format_exc()


# Page configuration
st.set_page_config(
    page_title="AI Investment Advisor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

NAV_ITEMS = [
    ("📈 Overview", "Cross-market snapshot and top signals"),
    ("📋 Recommendations", "Filterable list with explanations"),
    ("🔍 Stock Explorer", "Single-stock deep dive"),
    ("📊 Market Analytics", "Sector and risk-return view"),
    ("🤖 Model Performance", "Model comparison and metrics"),
    ("ℹ️ About", "Methodology and architecture"),
]

css_path = Path(__file__).with_name("styles.css")
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
else:
    st.warning("styles.css was not found; using default Streamlit styling.")


def render_import_error():
    """Display import errors in the app shell."""
    st.error("Failed to load application modules")
    st.code(IMPORT_ERROR or "Unknown import error")
    if 'IMPORT_TRACEBACK' in globals():
        st.text(IMPORT_TRACEBACK)


def _page_from_query() -> str:
    query = parse_qs(st.query_params.to_dict().get("page", ["📈 Overview"])[0]) if False else None
    return st.query_params.get("page", "📈 Overview")


def render_page_error(error, page):
    """Display a readable error panel and separate likely Databricks-side issues."""
    message = str(error)
    databricks_signals = [
        "Databricks client",
        "Query execution failed",
        "warehouse",
        "statement_execution",
        "workspace.investment_db",
        "permission",
        "auth",
        "schema",
        "table",
        "does not exist",
        "not found",
    ]
    likely_databricks = any(signal.lower() in message.lower() for signal in databricks_signals)

    st.markdown(
        f"""
        <div class="callout-box" style="background: linear-gradient(135deg, rgba(214,39,40,0.12), rgba(31,119,180,0.08)); border-color: rgba(214,39,40,0.22);">
            <strong>Unable to render {page}</strong><br/>
            {"This looks like a Databricks-side issue (connection, permissions, warehouse, or table/schema mismatch)." if likely_databricks else "This looks like a local app-side issue."}
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.expander("Show diagnostics", expanded=False).write(
        {
            "page": page,
            "error": message,
            "likely_databricks_side": likely_databricks,
        }
    )


def render_sidebar(selected_page):
    """Render the sidebar navigation and status panel."""
    if "selected_page" not in st.session_state:
        st.session_state.selected_page = selected_page

    st.sidebar.markdown(
        """
        <div class="sidebar-panel">
            <div class="sidebar-brand">
                <h3>AI Investment Advisor</h3>
                <p>Bootstrap-powered dashboards for screening, analysis, and model governance.</p>
            </div>
            <div class="sidebar-section">
                <h4>Navigation</h4>
                <div class="nav-tip">Use the page buttons below. Each page renders as a complete Bootstrap HTML view.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        """
        <div class="sidebar-panel" style="margin-top: 14px;">
            <div class="sidebar-section" style="border-top: none; padding-top: 0; margin-top: 0;">
                <h4>Databricks SQL</h4>
                <div class="nav-tip">Live warehouse-backed data, rendered through the HTML dashboard shell.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page_labels = [label for label, _ in NAV_ITEMS]
    for label, description in NAV_ITEMS:
        if st.sidebar.button(label, key=f"nav_{label}", use_container_width=True):
            st.session_state.selected_page = label
        if st.session_state.selected_page == label:
            st.sidebar.markdown(f"<div class='nav-tip'><strong>{description}</strong></div>", unsafe_allow_html=True)

    st.sidebar.markdown(
        """
        <div class="sidebar-panel">
            <div class="sidebar-section" style="border-top: none; padding-top: 0; margin-top: 0;">
                <h4>Signal guide</h4>
                <div class="nav-tip"><span style='color:#2ca02c; font-weight:700'>BUY</span> stronger upside potential</div>
                <div class="nav-tip"><span style='color:#ff7f0e; font-weight:700'>HOLD</span> wait for a cleaner setup</div>
                <div class="nav-tip"><span style='color:#d62728; font-weight:700'>AVOID</span> higher risk or weaker outlook</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return st.session_state.selected_page


def main():
    """Main application entry point."""
    page = render_sidebar("📈 Overview")

    if not IMPORTS_SUCCESSFUL:
        render_import_error()
        return

    try:
        if page == "📈 Overview":
            summary = queries.get_recommendation_summary()
            recommendations = queries.get_recommendations()
            sectors = queries.get_sector_analysis()
            rec_dist = queries.get_recommendation_distribution()
            risk_return = queries.get_risk_return_data()
            html = page_overview(summary, recommendations, sectors, rec_dist, risk_return)
        elif page == "📋 Recommendations":
            recommendations = queries.get_recommendations()
            html = page_recommendations(recommendations)
        elif page == "🔍 Stock Explorer":
            stock_list = queries.get_stock_list()
            selected_ticker = stock_list.iloc[0]['Ticker'] if not stock_list.empty else ""
            stock_recommendation = queries.get_stock_recommendation(selected_ticker) if selected_ticker else None
            stock_features = queries.get_stock_features(selected_ticker) if selected_ticker else None
            html = page_stock_explorer(stock_recommendation, stock_features, selected_ticker)
        elif page == "📊 Market Analytics":
            sectors = queries.get_sector_analysis()
            recommendations = queries.get_recommendations()
            risk_return = queries.get_risk_return_data()
            html = page_market_analytics(sectors, recommendations, risk_return)
        elif page == "🤖 Model Performance":
            models = queries.get_model_comparison()
            html = page_model_performance(models)
        elif page == "ℹ️ About":
            html = page_about()
        else:
            html = page_overview(queries.get_recommendation_summary(), queries.get_recommendations(), queries.get_sector_analysis(), queries.get_recommendation_distribution(), queries.get_risk_return_data())

        components.html(html, height=1800, scrolling=True)
    except Exception as error:
        render_page_error(error, page)


if __name__ == "__main__":
    main()
