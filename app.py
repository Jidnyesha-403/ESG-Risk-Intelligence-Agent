import os
import sqlite3
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load local environment variables (if any)
load_dotenv()

# Initialise SQLite history DB on every cold start
from src.utils.history_db import (
    init_db,
    save_report,
    get_all_history,
    get_report_by_id,
    get_company_history,
)
init_db()

# Setup page configuration
st.set_page_config(
    page_title="ESG Risk Intelligence Agent",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Premium CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

    html, body, [class*="css"], .stMarkdown {
        font-family: 'Outfit', sans-serif;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
        color: white !important;
        border: none;
        padding: 0.6rem 2rem;
        font-weight: 600;
        border-radius: 30px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 176, 155, 0.2);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 176, 155, 0.4);
    }

    /* Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.15);
        transition: transform 0.3s ease;
    }
    .metric-card:hover { transform: translateY(-5px); }
    .metric-label {
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #a0aec0;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }
    .metric-value { font-size: 2.2rem; font-weight: 700; }

    /* Risk colors */
    .risk-low    { color: #00e676; text-shadow: 0 0 10px rgba(0,230,118,0.25); }
    .risk-medium { color: #ff9100; text-shadow: 0 0 10px rgba(255,145,0,0.25); }
    .risk-high   { color: #ff1744; text-shadow: 0 0 10px rgba(255,23,68,0.25); }

    /* Report Container */
    .report-container {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.12);
        margin-top: 1.5rem;
    }

    /* Company Context Bar */
    .company-context-bar {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-left: 5px solid #00b09b;
        border-radius: 14px;
        padding: 1.2rem 1.8rem;
        margin-top: 1.2rem;
        margin-bottom: 1.8rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }
    .context-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
    .context-title  { font-size: 1.35rem; font-weight: 700; color: #ffffff; }
    .context-badge  {
        background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
        color: #ffffff; font-size: 0.82rem; font-weight: 600;
        padding: 0.25rem 0.8rem; border-radius: 20px;
        text-transform: uppercase; letter-spacing: 0.8px;
    }
    .context-desc { color: #cbd5e0; font-size: 0.98rem; line-height: 1.5; margin: 0; }

    .css-1d391kg { background-color: #0d1b15; }

    /* ── Compare Mode ──────────────────────────────────────────── */
    .compare-toggle-bar {
        background: linear-gradient(135deg, rgba(0,176,155,0.12) 0%, rgba(150,201,61,0.10) 100%);
        border: 1px solid rgba(0, 176, 155, 0.35);
        border-radius: 16px;
        padding: 0.9rem 1.6rem;
        margin-bottom: 1.6rem;
        display: flex; align-items: center; gap: 0.75rem;
        backdrop-filter: blur(8px);
    }
    .compare-toggle-label { font-size: 1rem; font-weight: 600; color: #e2e8f0; letter-spacing: 0.4px; }
    .compare-toggle-hint  { font-size: 0.82rem; color: #a0aec0; margin-left: auto; }

    .compare-table-wrap {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 20px;
        padding: 1.8rem 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.18);
        margin-top: 1.8rem; margin-bottom: 2rem; overflow-x: auto;
    }
    .compare-table-title { font-size: 1.2rem; font-weight: 700; color: #e2e8f0; margin-bottom: 1.1rem; letter-spacing: 0.5px; }
    .compare-table { width: 100%; border-collapse: collapse; font-family: 'Outfit', sans-serif; }
    .compare-table th {
        background: rgba(0,176,155,0.18); color: #81e6d9;
        font-size: 0.88rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: 1px;
        padding: 0.75rem 1.2rem; text-align: left;
        border-bottom: 2px solid rgba(0,176,155,0.3);
    }
    .compare-table td {
        padding: 0.8rem 1.2rem;
        border-bottom: 1px solid rgba(255,255,255,0.07);
        color: #e2e8f0; font-size: 0.97rem; vertical-align: middle;
    }
    .compare-table tr:last-child td { border-bottom: none; }
    .compare-table tr:hover td { background: rgba(255,255,255,0.03); }
    .compare-table .dim-cell {
        font-weight: 600; color: #a0aec0;
        font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.8px;
    }

    .badge { display: inline-block; padding: 0.28rem 0.9rem; border-radius: 30px; font-size: 0.82rem; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase; }
    .badge-low    { background: rgba(0,230,118,0.15);  color: #00e676; border: 1px solid rgba(0,230,118,0.35); }
    .badge-medium { background: rgba(255,145,0,0.15);  color: #ff9100; border: 1px solid rgba(255,145,0,0.35); }
    .badge-high   { background: rgba(255,23,68,0.15);  color: #ff1744; border: 1px solid rgba(255,23,68,0.35); }

    .compare-section-header {
        font-size: 1.25rem; font-weight: 700; color: #81e6d9;
        border-left: 4px solid #00b09b; padding-left: 0.85rem;
        margin: 2rem 0 1rem 0;
    }

    /* ── History viewer ────────────────────────────────────────── */
    .history-header {
        background: linear-gradient(135deg, rgba(0,176,155,0.10) 0%, rgba(150,201,61,0.08) 100%);
        border: 1px solid rgba(0,176,155,0.28);
        border-radius: 18px;
        padding: 1.4rem 2rem;
        margin-bottom: 1.5rem;
    }
    .history-header h2 { margin: 0; color: #81e6d9; font-size: 1.4rem; }
    .history-meta { color: #a0aec0; font-size: 0.9rem; margin-top: 0.3rem; }

    .trend-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 18px;
        padding: 1.5rem 1.8rem;
        margin-bottom: 1.8rem;
        box-shadow: 0 6px 24px rgba(0,0,0,0.14);
    }
    .trend-card-title { font-size: 1.1rem; font-weight: 700; color: #e2e8f0; margin-bottom: 1rem; }

    /* Sidebar history table tweaks */
    .sidebar-history-badge {
        display: inline-block; padding: 0.15rem 0.6rem; border-radius: 12px;
        font-size: 0.75rem; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase;
    }
    .history-empty { color: #718096; font-size: 0.9rem; text-align: center; padding: 0.8rem 0; }
</style>
""", unsafe_allow_html=True)


# ── Application Header ─────────────────────────────────────────────────────────
st.markdown("<h1 style='text-align:center;font-weight:700;margin-bottom:0.2rem;'>🌱 ESG Risk Intelligence Hub</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#a0aec0;font-size:1.15rem;margin-bottom:1.5rem;'>Multi-Agent Sustainability Disclosures &amp; Controversy Analysis System</p>", unsafe_allow_html=True)


# ── Pipeline runner ─────────────────────────────────────────────────────────────
def run_pipeline(company_name, groq_key):
    from src.agents.graph import run_esg_pipeline
    return run_esg_pipeline(company_name, groq_key)


# ── Risk helpers ────────────────────────────────────────────────────────────────
SCORE_MAP = {"Low": 1, "Medium": 2, "High": 3}
SCORE_LABEL = {1: "LOW", 2: "MEDIUM", 3: "HIGH"}


def compute_risk_scores(results):
    """Return (agg_e, agg_s, agg_g) as 'Low' | 'Medium' | 'High' strings."""
    risk_classifications = results.get("risk_classifications", [])
    e_counts = {"Low": 0, "Medium": 0, "High": 0}
    s_counts = {"Low": 0, "Medium": 0, "High": 0}
    g_counts = {"Low": 0, "Medium": 0, "High": 0}
    for rc in risk_classifications:
        e_counts[rc.get("E_risk", "Low")] += 1
        s_counts[rc.get("S_risk", "Low")] += 1
        g_counts[rc.get("G_risk", "Low")] += 1

    def _agg(counts):
        total = sum(counts.values())
        if total == 0:
            return "Low"
        weighted = counts["Low"] * 1 + counts["Medium"] * 2 + counts["High"] * 3
        avg = weighted / total
        if avg >= 2.33:
            return "High"
        elif avg >= 1.5:
            return "Medium"
        return "Low"

    return _agg(e_counts), _agg(s_counts), _agg(g_counts)


def get_risk_class(val):
    return f"risk-{val.lower()}"


def badge_html(val):
    return f'<span class="badge badge-{val.lower()}">{val.upper()}</span>'


# ── Render a single company's risk cards + full report ──────────────────────────
def render_company_report(company_name, results):
    """Renders risk cards, company context bar, and full report markdown.
    Returns (agg_e, agg_s, agg_g) for downstream use."""
    agg_e, agg_s, agg_g = compute_risk_scores(results)

    # Company context bar (Wikipedia)
    try:
        from src.utils.company_info import get_company_context
        rag_ctx = results.get("rag_context", "")
        inferred_ind = ""
        if "Benchmark" in rag_ctx:
            inferred_ind = rag_ctx.split("Benchmark")[0].split("\n")[-1].strip()
        ctx_info = get_company_context(company_name, inferred_ind)
        st.markdown(f"""
        <div class="company-context-bar">
            <div class="context-header">
                <span class="context-title">🏢 {ctx_info['display_name']}</span>
                <span class="context-badge">Sector: {ctx_info['industry']}</span>
            </div>
            <p class="context-desc">{ctx_info['description']}</p>
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        pass

    # Risk metric cards
    card_col1, card_col2, card_col3 = st.columns(3)
    with card_col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Environmental (E)</div>
            <div class="metric-value {get_risk_class(agg_e)}">{agg_e.upper()}</div>
        </div>
        """, unsafe_allow_html=True)
    with card_col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Social (S)</div>
            <div class="metric-value {get_risk_class(agg_s)}">{agg_s.upper()}</div>
        </div>
        """, unsafe_allow_html=True)
    with card_col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Governance (G)</div>
            <div class="metric-value {get_risk_class(agg_g)}">{agg_g.upper()}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Full markdown report
    st.markdown('<div class="report-container">', unsafe_allow_html=True)
    report_text = results.get("final_report", "# No report generated")
    st.markdown(report_text)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # PDF download
    try:
        from src.utils.pdf_generator import create_esg_pdf
        pdf_bytes = create_esg_pdf(company_name, agg_e, agg_s, agg_g, report_text)
        dl_col1, dl_col2, dl_col3 = st.columns([2, 3, 2])
        with dl_col2:
            st.download_button(
                label="📄 Download Executive Report as PDF",
                data=pdf_bytes,
                file_name=f"{company_name.strip().replace(' ', '_')}_ESG_Risk_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
                key=f"pdf_{company_name}"
            )
    except Exception as pdf_err:
        st.warning(f"Could not generate PDF download: {pdf_err}")

    return agg_e, agg_s, agg_g


# ── Trend chart builder ──────────────────────────────────────────────────────────
def render_trend_chart(company_name: str):
    """Fetch company history and render a Plotly E/S/G line chart.
    Only renders if the company has been analysed more than once."""
    history = get_company_history(company_name)
    if len(history) < 2:
        return  # Not enough data

    rows = []
    for r in history:
        rows.append({
            "Date": r["date_generated"],
            "Environmental": SCORE_MAP.get(r["e_score"], 1),
            "Social":        SCORE_MAP.get(r["s_score"], 1),
            "Governance":    SCORE_MAP.get(r["g_score"], 1),
        })
    df = pd.DataFrame(rows)

    fig = go.Figure()

    color_map = {
        "Environmental": "#00e676",
        "Social":        "#ff9100",
        "Governance":    "#00b4d8",
    }
    for dim, color in color_map.items():
        fig.add_trace(go.Scatter(
            x=df["Date"],
            y=df[dim],
            name=dim,
            mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=9, color=color,
                        line=dict(width=2, color="rgba(255,255,255,0.4)")),
            hovertemplate=f"<b>{dim}</b><br>%{{x}}<br>Score: %{{customdata}}<extra></extra>",
            customdata=[SCORE_LABEL.get(v, v) for v in df[dim]],
        ))

    fig.update_layout(
        title=dict(
            text=f"📈 E/S/G Score Trend — {company_name}",
            font=dict(size=15, color="#e2e8f0"),
            x=0.02,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.03)",
        font=dict(family="Outfit, sans-serif", color="#a0aec0"),
        yaxis=dict(
            tickvals=[1, 2, 3],
            ticktext=["LOW", "MEDIUM", "HIGH"],
            range=[0.5, 3.5],
            gridcolor="rgba(255,255,255,0.07)",
            zeroline=False,
        ),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.07)",
            tickangle=-30,
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=10, r=10, t=50, b=40),
        height=320,
    )

    st.markdown('<div class="trend-card"><div class="trend-card-title">📊 Historical E/S/G Score Trend</div>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("<h2 style='font-weight:600;margin-top:0;'>⚙️ System Settings</h2>", unsafe_allow_html=True)
    st.write("Configure API access and database settings.")

    groq_api_key = st.text_input(
        "Groq API Key",
        value=os.environ.get("GROQ_API_KEY", ""),
        type="password",
        help="Input your Groq API Key to enable dynamic report synthesis with Llama 3.1."
    )

    st.markdown("---")
    st.markdown("<h4 style='font-weight:600;'>🛠️ Developer Controls</h4>", unsafe_allow_html=True)
    if st.button("Train ESG Model & Seed DB"):
        with st.spinner("Seeding database & training model..."):
            try:
                from src.utils.model_trainer import train_and_save_model
                from src.utils.db_initializer import initialize_db
                train_and_save_model()
                initialize_db()
                st.success("Successfully trained model and initialized database!")
            except Exception as e:
                st.error(f"Seeding failed: {e}")

    st.markdown("---")
    st.write("💡 **Architecture Highlights:**")
    st.info(
        "1. **Scraper Agent**: Fetches ESG news (DuckDuckGo).\n"
        "2. **Classifier Agent**: Categorizes E/S/G risk levels (Scikit-Learn ML).\n"
        "3. **RAG Agent**: Finds benchmark context (ChromaDB).\n"
        "4. **Synthesis Agent**: Generates structured report (Llama 3.1)."
    )

    # ── Report History ─────────────────────────────────────────────────────────
    st.markdown("---")
    with st.expander("📚 Report History", expanded=False):
        all_history = get_all_history()

        if not all_history:
            st.markdown('<p class="history-empty">No reports generated yet.<br>Run an analysis to start building history.</p>', unsafe_allow_html=True)
        else:
            st.caption(f"**{len(all_history)}** report(s) saved to local database")

            # Sort controls
            sort_opt = st.selectbox(
                "Sort by",
                ["Date ↓ (newest)", "Date ↑ (oldest)", "Company A→Z", "Company Z→A"],
                key="history_sort"
            )
            sort_key_map = {
                "Date ↓ (newest)": ("date_generated", True),
                "Date ↑ (oldest)": ("date_generated", False),
                "Company A→Z":     ("company_name",   False),
                "Company Z→A":     ("company_name",   True),
            }
            sk, sr = sort_key_map[sort_opt]
            sorted_history = sorted(all_history, key=lambda r: r[sk], reverse=sr)

            # Build display DataFrame
            RISK_EMOJI = {"Low": "🟢", "Medium": "🟠", "High": "🔴"}
            display_rows = []
            for r in sorted_history:
                display_rows.append({
                    "ID":          r["id"],
                    "Company":     r["company_name"],
                    "Date":        r["date_generated"][:16],   # trim seconds
                    "E":           RISK_EMOJI.get(r["e_score"], "") + " " + r["e_score"],
                    "S":           RISK_EMOJI.get(r["s_score"], "") + " " + r["s_score"],
                    "G":           RISK_EMOJI.get(r["g_score"], "") + " " + r["g_score"],
                })
            df_display = pd.DataFrame(display_rows)

            st.dataframe(
                df_display[["Company", "Date", "E", "S", "G"]],
                use_container_width=True,
                hide_index=True,
            )

            st.markdown("**View a saved report:**")
            report_options = [
                f"{r['company_name']}  —  {r['date_generated'][:16]}"
                for r in sorted_history
            ]
            selected_label = st.selectbox(
                "Select report",
                report_options,
                key="history_select",
                label_visibility="collapsed"
            )
            selected_idx  = report_options.index(selected_label)
            selected_id   = sorted_history[selected_idx]["id"]
            selected_co   = sorted_history[selected_idx]["company_name"]

            btn_col_a, btn_col_b = st.columns(2)
            with btn_col_a:
                if st.button("📖 View Report", use_container_width=True, key="btn_view_history"):
                    st.session_state["history_report_id"] = selected_id
                    st.session_state["history_company"]   = selected_co
                    st.session_state["viewing_history"]   = True
                    st.rerun()
            with btn_col_b:
                if st.button("🗑️ Delete", use_container_width=True, key="btn_delete_history"):
                    from src.utils.history_db import delete_report
                    delete_report(selected_id)
                    # If we're currently viewing this report, close the viewer
                    if st.session_state.get("history_report_id") == selected_id:
                        st.session_state.pop("viewing_history", None)
                        st.session_state.pop("history_report_id", None)
                        st.session_state.pop("history_company", None)
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# HISTORY VIEWER  (takes over main area when active)
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.get("viewing_history") and st.session_state.get("history_report_id"):
    record = get_report_by_id(st.session_state["history_report_id"])

    if record:
        company_name = record["company_name"]
        date_str     = record["date_generated"]

        # Header bar
        st.markdown(f"""
        <div class="history-header">
            <h2>📚 Viewing Saved Report</h2>
            <p class="history-meta">🏢 <strong>{company_name}</strong> &nbsp;·&nbsp; 🗓 {date_str}</p>
        </div>
        """, unsafe_allow_html=True)

        back_col, _ = st.columns([1, 5])
        with back_col:
            if st.button("← Back to Analysis", key="btn_history_back"):
                st.session_state.pop("viewing_history", None)
                st.session_state.pop("history_report_id", None)
                st.session_state.pop("history_company", None)
                st.rerun()

        # ── E/S/G summary cards (from stored scores) ────────────────────────
        agg_e = record["e_score"]
        agg_s = record["s_score"]
        agg_g = record["g_score"]

        c1, c2, c3 = st.columns(3)
        for col, label, val in [(c1, "Environmental (E)", agg_e),
                                 (c2, "Social (S)",        agg_s),
                                 (c3, "Governance (G)",    agg_g)]:
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value {get_risk_class(val)}">{val.upper()}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Trend chart (only if company has ≥ 2 records) ──────────────────
        render_trend_chart(company_name)

        # ── Full report text ───────────────────────────────────────────────
        st.markdown('<div class="report-container">', unsafe_allow_html=True)
        st.markdown(record.get("report_text", "*No report text stored.*"))
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # PDF download from stored data
        try:
            from src.utils.pdf_generator import create_esg_pdf
            pdf_bytes = create_esg_pdf(
                company_name, agg_e, agg_s, agg_g,
                record.get("report_text", "")
            )
            dl1, dl2, dl3 = st.columns([2, 3, 2])
            with dl2:
                st.download_button(
                    label="📄 Download this Report as PDF",
                    data=pdf_bytes,
                    file_name=f"{company_name.replace(' ','_')}_ESG_{date_str[:10]}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="history_pdf_dl"
                )
        except Exception as pdf_err:
            st.warning(f"Could not generate PDF: {pdf_err}")

    else:
        st.error("Report not found — it may have been deleted.")
        if st.button("← Back"):
            st.session_state.pop("viewing_history", None)
            st.session_state.pop("history_report_id", None)
            st.rerun()

    # Stop here — don't render the analysis UI below
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# COMPARE MODE TOGGLE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="compare-toggle-bar">', unsafe_allow_html=True)
toggle_col, label_col = st.columns([1, 8])
with toggle_col:
    compare_mode = st.toggle("", key="compare_mode", value=False)
with label_col:
    if compare_mode:
        st.markdown('<span class="compare-toggle-label">🔀 Compare Two Companies &nbsp;<span style="color:#00b09b;">● Active</span></span><span class="compare-toggle-hint">Run both pipelines in parallel and view a side-by-side ESG breakdown</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="compare-toggle-label">🔀 Compare Two Companies</span><span class="compare-toggle-hint">Toggle to analyse two companies side by side</span>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SINGLE COMPANY MODE
# ══════════════════════════════════════════════════════════════════════════════
if not compare_mode:
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        company_input = st.text_input(
            "Enter Company Name",
            placeholder="e.g., Tesla, Apple, ExxonMobil, Amazon...",
            key="company_search"
        )
        analyze_btn = st.button("Generate ESG Risk Analysis", use_container_width=True)

    if analyze_btn:
        if not company_input.strip():
            st.warning("Please enter a valid company name.")
        else:
            status_container = st.empty()
            with status_container.container():
                st.markdown("<h3 style='font-weight:600;'>🔄 Running Multi-Agent Workflow</h3>", unsafe_allow_html=True)
                p_collector  = st.status("🕵️ Agent 1: Gathering web search and news disclosures...", state="running")
                p_classifier = st.status("🧠 Agent 2: Loading ML model and classifying risks...", state="running")
                p_retriever  = st.status("📚 Agent 3: Querying ChromaDB for ESG benchmarks...", state="running")
                p_generator  = st.status("✍️ Agent 4: Synthesizing final intelligence report...", state="running")

            try:
                p_collector.update(label="🕵️ Agent 1: Scraping recent disclosures...", state="running")
                results = run_pipeline(company_input, groq_api_key)

                p_collector.update(label=f"🕵️ Agent 1: Scraped {len(results.get('scraped_content', []))} sources.", state="complete")
                p_classifier.update(label=f"🧠 Agent 2: Classified {len(results.get('risk_classifications', []))} dimensions.", state="complete")
                p_retriever.update(label="📚 Agent 3: Historical industry standards retrieved.", state="complete")
                p_generator.update(label="✍️ Agent 4: Synthesis complete.", state="complete")

                status_container.empty()

                st.markdown(f"<h2 style='text-align:center;margin-top:1.5rem;'>📈 ESG Intelligence Analysis: {company_input}</h2>", unsafe_allow_html=True)
                agg_e, agg_s, agg_g = render_company_report(company_input, results)

                # ── Persist to history DB ────────────────────────────────────
                report_text = results.get("final_report", "")
                save_report(company_input.strip(), agg_e, agg_s, agg_g, report_text)

            except Exception as e:
                p_collector.update(state="error")
                p_classifier.update(state="error")
                p_retriever.update(state="error")
                p_generator.update(state="error")
                st.error(f"An error occurred during workflow execution: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# COMPARE TWO COMPANIES MODE
# ══════════════════════════════════════════════════════════════════════════════
else:
    inp_col1, gap_col, inp_col2 = st.columns([5, 1, 5])
    with inp_col1:
        st.markdown("<p style='font-weight:600;font-size:1rem;margin-bottom:0.3rem;'>🏢 Company A</p>", unsafe_allow_html=True)
        company_a = st.text_input("Company A", placeholder="e.g., Tesla, Apple…", key="compare_company_a", label_visibility="collapsed")
    with gap_col:
        st.markdown("<p style='text-align:center;font-size:1.8rem;padding-top:0.5rem;color:#a0aec0;'>vs</p>", unsafe_allow_html=True)
    with inp_col2:
        st.markdown("<p style='font-weight:600;font-size:1rem;margin-bottom:0.3rem;'>🏢 Company B</p>", unsafe_allow_html=True)
        company_b = st.text_input("Company B", placeholder="e.g., ExxonMobil, Amazon…", key="compare_company_b", label_visibility="collapsed")

    btn_col1, btn_col2, btn_col3 = st.columns([2, 3, 2])
    with btn_col2:
        compare_btn = st.button("⚡ Run Parallel Comparison", use_container_width=True, key="compare_run_btn")

    if compare_btn:
        if not company_a.strip() or not company_b.strip():
            st.warning("Please enter names for **both** companies before running the comparison.")
        else:
            status_container = st.empty()
            with status_container.container():
                st.markdown("<h3 style='font-weight:600;'>⚡ Running Parallel Multi-Agent Workflow</h3>", unsafe_allow_html=True)
                prog_a = st.status(f"🔄 Pipeline for **{company_a}** — running all 4 agents...", state="running")
                prog_b = st.status(f"🔄 Pipeline for **{company_b}** — running all 4 agents...", state="running")

            results_a = results_b = error_a = error_b = None

            with ThreadPoolExecutor(max_workers=2) as executor:
                future_a = executor.submit(run_pipeline, company_a.strip(), groq_api_key)
                future_b = executor.submit(run_pipeline, company_b.strip(), groq_api_key)
                for future in as_completed([future_a, future_b]):
                    if future is future_a:
                        try:
                            results_a = future.result()
                            prog_a.update(label=f"✅ Pipeline for **{company_a}** — complete.", state="complete")
                        except Exception as e:
                            error_a = e
                            prog_a.update(label=f"❌ Pipeline for **{company_a}** failed: {e}", state="error")
                    else:
                        try:
                            results_b = future.result()
                            prog_b.update(label=f"✅ Pipeline for **{company_b}** — complete.", state="complete")
                        except Exception as e:
                            error_b = e
                            prog_b.update(label=f"❌ Pipeline for **{company_b}** failed: {e}", state="error")

            status_container.empty()

            if error_a:
                st.error(f"**{company_a}** pipeline error: {error_a}")
            if error_b:
                st.error(f"**{company_b}** pipeline error: {error_b}")

            if results_a and results_b:
                e_a, s_a, g_a = compute_risk_scores(results_a)
                e_b, s_b, g_b = compute_risk_scores(results_b)

                # ── Comparison table ─────────────────────────────────────────
                st.markdown("<div class='compare-section-header'>📊 Side-by-Side ESG Comparison</div>", unsafe_allow_html=True)
                st.markdown(f"""
                <div class="compare-table-wrap">
                    <div class="compare-table-title">ESG Risk Scorecard</div>
                    <table class="compare-table">
                        <thead>
                            <tr>
                                <th>Dimension</th>
                                <th>🏢 {company_a}</th>
                                <th>🏢 {company_b}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td class="dim-cell">🌿 Environmental</td>
                                <td>{badge_html(e_a)}</td>
                                <td>{badge_html(e_b)}</td>
                            </tr>
                            <tr>
                                <td class="dim-cell">🤝 Social</td>
                                <td>{badge_html(s_a)}</td>
                                <td>{badge_html(s_b)}</td>
                            </tr>
                            <tr>
                                <td class="dim-cell">🏛️ Governance</td>
                                <td>{badge_html(g_a)}</td>
                                <td>{badge_html(g_b)}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                """, unsafe_allow_html=True)

                # ── Save both to history ─────────────────────────────────────
                save_report(company_a.strip(), e_a, s_a, g_a, results_a.get("final_report", ""))
                save_report(company_b.strip(), e_b, s_b, g_b, results_b.get("final_report", ""))

                # ── Expandable full reports ──────────────────────────────────
                st.markdown("<div class='compare-section-header'>📄 Full Intelligence Reports</div>", unsafe_allow_html=True)
                with st.expander(f"📋 {company_a} — Full ESG Report", expanded=False):
                    st.markdown(f"<h2 style='margin-top:0.5rem;'>📈 ESG Intelligence Analysis: {company_a}</h2>", unsafe_allow_html=True)
                    render_company_report(company_a.strip(), results_a)

                with st.expander(f"📋 {company_b} — Full ESG Report", expanded=False):
                    st.markdown(f"<h2 style='margin-top:0.5rem;'>📈 ESG Intelligence Analysis: {company_b}</h2>", unsafe_allow_html=True)
                    render_company_report(company_b.strip(), results_b)

            elif results_a:
                agg_e, agg_s, agg_g = render_company_report(company_a.strip(), results_a)
                save_report(company_a.strip(), agg_e, agg_s, agg_g, results_a.get("final_report", ""))
            elif results_b:
                agg_e, agg_s, agg_g = render_company_report(company_b.strip(), results_b)
                save_report(company_b.strip(), agg_e, agg_s, agg_g, results_b.get("final_report", ""))
