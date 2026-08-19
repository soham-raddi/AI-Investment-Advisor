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

# Load .env file variables manually into os.environ
def load_env():
    import os
    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip()

load_env()

# Try to import page modules with error handling
try:
    from views import (
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
    page_icon=":trending_up:",
    layout="wide",
    initial_sidebar_state="expanded"
)

NAV_ITEMS = [
    ("Overview", "Cross-market snapshot and top signals"),
    ("Recommendations", "Filterable list with explanations"),
    ("Stock Explorer", "Single-stock deep dive"),
    ("Market Analytics", "Sector and risk-return view"),
    ("Model Performance", "Model comparison and metrics"),
    ("AI Chatbot", "Ask questions about your investments"),
    ("About", "Methodology and architecture"),
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
            <div class="sidebar-section" style="border-top: 1px solid rgba(255,255,255,0.08); padding-top: 10px; margin-top: 10px;">
                <h4>Volatility Guide</h4>
                <div class="nav-tip" style="line-height:1.4">Volatility represents stock price dispersion over time:</div>
                <div class="nav-tip"><span style='color:#2ca02c; font-weight:700'>Low (&lt;0.0150)</span> Stable / steadier movement</div>
                <div class="nav-tip"><span style='color:#ff7f0e; font-weight:700'>Medium (0.0150-0.0300)</span> Moderate price swings</div>
                <div class="nav-tip"><span style='color:#d62728; font-weight:700'>High (&gt;0.0300)</span> Extreme swings, high risk/reward</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return st.session_state.selected_page


def main():
    """Main application entry point."""
    page = render_sidebar("Overview")

    if not IMPORTS_SUCCESSFUL:
        render_import_error()
        return

    try:
        if page == "Overview":
            summary = queries.get_recommendation_summary()
            recommendations = queries.get_recommendations()
            sectors = queries.get_sector_analysis()
            rec_dist = queries.get_recommendation_distribution()
            risk_return = queries.get_risk_return_data()
            html = page_overview(summary, recommendations, sectors, rec_dist, risk_return)
        elif page == "Recommendations":
            recommendations = queries.get_recommendations()
            html = page_recommendations(recommendations)
        elif page == "Stock Explorer":
            stock_list = queries.get_stock_list()
            if not stock_list.empty:
                tickers = stock_list['Ticker'].tolist()
                ticker_names = {
                    "AAPL": "Apple",
                    "MSFT": "Microsoft",
                    "GOOGL": "Google",
                    "AMZN": "Amazon",
                    "TSLA": "Tesla",
                    "META": "Meta",
                    "NVDA": "NVIDIA",
                    "NFLX": "Netflix",
                    "JPM": "JPMorgan",
                    "WMT": "Walmart"
                }
                selected_ticker = st.selectbox(
                    "Choose a Stock to Explore", 
                    options=tickers,
                    format_func=lambda x: f"{x} ({ticker_names.get(x, '')})"
                )
            else:
                selected_ticker = ""
            stock_recommendation = queries.get_stock_recommendation(selected_ticker) if selected_ticker else None
            stock_features = queries.get_stock_features(selected_ticker) if selected_ticker else None
            html = page_stock_explorer(stock_recommendation, stock_features, selected_ticker)
        elif page == "Market Analytics":
            sectors = queries.get_sector_analysis()
            recommendations = queries.get_recommendations()
            risk_return = queries.get_risk_return_data()
            html = page_market_analytics(sectors, recommendations, risk_return)
        elif page == "Model Performance":
            models = queries.get_model_comparison()
            html = page_model_performance(models)
        elif page == "AI Chatbot":
            show_chatbot()
            return
        elif page == "About":
            html = page_about()
        else:
            html = page_overview(queries.get_recommendation_summary(), queries.get_recommendations(), queries.get_sector_analysis(), queries.get_recommendation_distribution(), queries.get_risk_return_data())

        components.html(html, height=1800, scrolling=True)
    except Exception as error:
        render_page_error(error, page)


def show_chatbot():
    st.header("AI Investment Assistant")
    st.subheader("Ask questions about your investments")

    from components.chatbot import InvestmentChatbot

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_ticker" not in st.session_state:
        st.session_state.current_ticker = None

    chatbot = InvestmentChatbot()

    # Sidebar context configuration
    st.sidebar.markdown("<div class='sidebar-section'><h4>Context</h4></div>", unsafe_allow_html=True)
    stock_list = queries.get_stock_list()
    tickers = ["None - General Questions"]
    if not stock_list.empty:
        tickers.extend(stock_list['Ticker'].tolist())

    # Find proper default index
    default_idx = 0
    if st.session_state.current_ticker in tickers:
        default_idx = tickers.index(st.session_state.current_ticker)

    selected_ticker = st.sidebar.selectbox(
        "Focus Stock Context",
        options=tickers,
        index=default_idx
    )

    if selected_ticker == "None - General Questions":
        st.session_state.current_ticker = None
    else:
        st.session_state.current_ticker = selected_ticker

    # Display focus stock metrics
    if st.session_state.current_ticker:
        rec_df = queries.get_stock_recommendation(st.session_state.current_ticker)
        if rec_df is not None and not rec_df.empty:
            row = rec_df.iloc[0]
            vol_dec = float(row.get('Volatility', 0.0)) / 100
            st.sidebar.markdown(
                f"""
                <div class="sidebar-panel" style="margin-top: 10px; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 10px;">
                    <div style="font-weight: 700; color: #fff;">{row.get('Ticker')} Metrics:</div>
                    <div class="nav-tip">Price: <strong>${float(row.get('Close', 0.0)):.2f}</strong></div>
                    <div class="nav-tip">Return: <strong>{float(row.get('Predicted_Return', 0.0)):.2%}</strong></div>
                    <div class="nav-tip">Volatility: <strong>{vol_dec:.4f}</strong></div>
                    <div class="nav-tip">Risk Level: <strong>{row.get('Risk_Level')}</strong></div>
                </div>
                """,
                unsafe_allow_html=True
            )

    if st.sidebar.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # Display conversation history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Example questions
    if not st.session_state.messages:
        st.write("Click an example question to start:")
        col1, col2 = st.columns(2)
        examples = [
            "High volatility, high return - should I buy?",
            "What's your best recommendation?",
            "How do you balance risk and return?",
            "Explain this recommendation"
        ]

        if col1.button(examples[0], use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": examples[0]})
            with st.chat_message("user"):
                st.write(examples[0])
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    res = chatbot.generate_response(examples[0], st.session_state.messages[:-1], st.session_state.current_ticker)
                    st.write(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
            st.rerun()

        if col1.button(examples[1], use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": examples[1]})
            with st.chat_message("user"):
                st.write(examples[1])
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    res = chatbot.generate_response(examples[1], st.session_state.messages[:-1], st.session_state.current_ticker)
                    st.write(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
            st.rerun()

        if col2.button(examples[2], use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": examples[2]})
            with st.chat_message("user"):
                st.write(examples[2])
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    res = chatbot.generate_response(examples[2], st.session_state.messages[:-1], st.session_state.current_ticker)
                    st.write(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
            st.rerun()

        if col2.button(examples[3], use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": examples[3]})
            with st.chat_message("user"):
                st.write(examples[3])
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    res = chatbot.generate_response(examples[3], st.session_state.messages[:-1], st.session_state.current_ticker)
                    st.write(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
            st.rerun()

    user_input = st.chat_input("Ask a question...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                res = chatbot.generate_response(user_input, st.session_state.messages[:-1], st.session_state.current_ticker)
                st.write(res)
        st.session_state.messages.append({"role": "assistant", "content": res})
        st.rerun()


if __name__ == "__main__":
    main()
