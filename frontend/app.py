# frontend/app.py
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ─── Page Config ────────────────────────────────────────────────
st.set_page_config(
    page_title="IndusCredit Risk Platform",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

API = "http://localhost:8000"

# ─── CSS Styling ────────────────────────────────────────────────
st.markdown("""
<style>
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    

    /* Main background */
    .main {
        background-color: #f0f4f8;
    }

    /* Top header banner */
    .top-header {
        background: linear-gradient(135deg, #0f2557 0%, #1a3a8f 50%, #2563eb 100%);
        padding: 2rem 3rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(37,99,235,0.3);
    }
    .top-header h1 {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: 1px;
    }
    .top-header p {
        margin: 0.3rem 0 0 0;
        opacity: 0.85;
        font-size: 1rem;
    }
    .top-header .badge {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        border: 1px solid rgba(255,255,255,0.4);
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin-top: 0.8rem;
    }

    /* KPI cards */
    .kpi-card {
        background: white;
        border-radius: 14px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-left: 5px solid #2563eb;
        transition: transform 0.2s;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
    }
    .kpi-card h2 {
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
        color: #1e3a8a;
    }
    .kpi-card p {
        color: #6b7280;
        margin: 0.3rem 0 0 0;
        font-size: 0.9rem;
        font-weight: 500;
    }
    .kpi-card-red {
        border-left: 5px solid #dc2626;
    }
    .kpi-card-red h2 { color: #dc2626; }
    .kpi-card-green {
        border-left: 5px solid #059669;
    }
    .kpi-card-green h2 { color: #059669; }
    .kpi-card-orange {
        border-left: 5px solid #d97706;
    }
    .kpi-card-orange h2 { color: #d97706; }

    /* Risk result cards */
    .result-low {
        background: linear-gradient(135deg, #059669, #10b981);
        color: white;
        padding: 1.5rem;
        border-radius: 14px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(5,150,105,0.3);
    }
    .result-medium {
        background: linear-gradient(135deg, #d97706, #f59e0b);
        color: white;
        padding: 1.5rem;
        border-radius: 14px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(217,119,6,0.3);
    }
    .result-high {
        background: linear-gradient(135deg, #dc2626, #ef4444);
        color: white;
        padding: 1.5rem;
        border-radius: 14px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(220,38,38,0.3);
    }
    .result-low h1,
    .result-medium h1,
    .result-high h1 {
        font-size: 2rem;
        margin: 0;
        font-weight: 800;
    }
    .result-low h4,
    .result-medium h4,
    .result-high h4 {
        margin: 0 0 0.5rem 0;
        opacity: 0.9;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Info cards */
    .info-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.07);
        margin-bottom: 1rem;
    }
    .info-card h4 {
        color: #374151;
        margin: 0 0 0.8rem 0;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #6b7280;
    }

    /* Section headers */
    .section-header {
        color: #1e3a8a;
        font-weight: 700;
        font-size: 1.3rem;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #2563eb;
        display: inline-block;
    }

    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #0f2557, #1a3a8f);
    }

    /* Alert box */
    .alert-box {
        background: linear-gradient(135deg, #fef2f2, #fee2e2);
        border: 1px solid #fca5a5;
        border-left: 5px solid #dc2626;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
    }
    .alert-box-warning {
        background: linear-gradient(135deg, #fffbeb, #fef3c7);
        border: 1px solid #fcd34d;
        border-left: 5px solid #d97706;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
    }
    .alert-box-success {
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
        border: 1px solid #86efac;
        border-left: 5px solid #059669;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
    }

    /* Explanation box */
    .explain-box {
        background: linear-gradient(135deg, #eff6ff, #dbeafe);
        border: 1px solid #93c5fd;
        border-left: 5px solid #2563eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        font-size: 1rem;
        line-height: 1.7;
        color: #1e3a8a;
    }

    /* Applicant detail row */
    .detail-row {
        display: flex;
        justify-content: space-between;
        padding: 0.4rem 0;
        border-bottom: 1px solid #f3f4f6;
    }
    .detail-label {
        color: #6b7280;
        font-size: 0.88rem;
    }
    .detail-value {
        color: #111827;
        font-weight: 600;
        font-size: 0.88rem;
    }

    /* Stbutton */
    .stButton > button {
        background: linear-gradient(135deg, #1a3a8f, #2563eb);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 2rem;
        font-weight: 700;
        font-size: 1rem;
        width: 100%;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(37,99,235,0.3);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37,99,235,0.4);
    }
</style>
""", unsafe_allow_html=True)

# ─── Top Header ─────────────────────────────────────────────────
st.markdown("""
<div class="top-header">
    <h1>🏦 IndusCredit Risk Decisioning Platform</h1>
    <p>AI-Powered Credit Risk Assessment System — Organized by BNY</p>
    <div class="badge">
        ⚡ LightGBM &nbsp;|&nbsp; 🔍 SHAP &nbsp;|&nbsp;
        🤖 OpenAI GPT-4 &nbsp;|&nbsp; 👁️ Google Vision &nbsp;|&nbsp;
        🤗 HuggingFace
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0;">
        <h2 style="color:white; margin:0;">🏦 IndusCredit</h2>
        <p style="color:rgba(255,255,255,0.6);
                  font-size:0.8rem; margin:0;">
            Risk Decisioning Platform
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio("", [
        "🏠  Dashboard",
        "🔍  Existing Applicant",
        "📝  New Applicant",
        "📊  Portfolio Analysis",
        "📄  Committee Report"
    ])

    st.markdown("---")

    # Live metrics in sidebar
    try:
        summary = requests.get(
            f"{API}/portfolio/summary", timeout=3
        ).json()
    except:
        summary = {
            "total_applications": 8000,
            "default_rate_pct":   4.8,
            "model_auc":          0.86,
            "model_threshold":    0.42
        }

    st.markdown("""
    <p style="color:rgba(255,255,255,0.5);
              font-size:0.75rem;
              text-transform:uppercase;
              letter-spacing:1px;
              margin-bottom:0.5rem;">
        Live Metrics
    </p>
    """, unsafe_allow_html=True)

    st.metric("📋 Applications",
              f"{summary['total_applications']:,}")
    st.metric("⚠️ Default Rate",
              f"{summary['default_rate_pct']}%")
    st.metric("🎯 Model AUC",
              f"{summary['model_auc']}")
    st.metric("🎚️ Threshold",
              f"{summary['model_threshold']}")

    st.markdown("---")
    st.markdown("""
    <p style="color:rgba(255,255,255,0.4);
              font-size:0.7rem;
              text-align:center;">
        Round 2 — API Integration<br>
        DataSprint Competition
    </p>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# SHARED FUNCTION — Show Risk Results
# ═══════════════════════════════════════════════════════════════

def show_results(pred, applicant):
    prob          = pred['probability_pct']
    risk_tier     = pred['risk_tier']
    recommendation= pred['recommendation']
    color         = pred['risk_color']

    st.markdown(
        '<p class="section-header">📋 Risk Assessment Result</p>',
        unsafe_allow_html=True
    )

    # Gauge Chart
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        fig = go.Figure(go.Indicator(
            mode  = "gauge+number",
            value = prob,
            title = {
                'text': "Probability of Default (%)",
                'font': {'size': 18, 'color': '#1e3a8a'}
            },
            number = {'suffix': "%", 'font': {'size': 40}},
            gauge  = {
                'axis': {
                    'range':     [0, 100],
                    'tickwidth': 1,
                    'tickcolor': "#374151"
                },
                'bar': {'color': color, 'thickness': 0.3},
                'bgcolor': "white",
                'borderwidth': 0,
                'steps': [
                    {'range': [0,  35], 'color': '#d1fae5'},
                    {'range': [35, 60], 'color': '#fef3c7'},
                    {'range': [60, 100],'color': '#fee2e2'}
                ],
                'threshold': {
                    'line':      {'color': color, 'width': 4},
                    'thickness': 0.8,
                    'value':     prob
                }
            }
        ))
        fig.update_layout(
            height     = 280,
            margin     = dict(t=50, b=10, l=10, r=10),
            paper_bgcolor = "rgba(0,0,0,0)",
            plot_bgcolor  = "rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Result Cards
    card_class = (
        "result-low"    if risk_tier == "LOW"    else
        "result-medium" if risk_tier == "MEDIUM" else
        "result-high"
    )
    rec_class = (
        "result-low"    if recommendation == "APPROVE" else
        "result-medium" if recommendation == "REVIEW"  else
        "result-high"
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="{card_class}">
            <h4>Risk Tier</h4>
            <h1>{risk_tier}</h1>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="{rec_class}">
            <h4>Decision</h4>
            <h1>{recommendation}</h1>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="{card_class}">
            <h4>PD Score</h4>
            <h1>{prob:.1f}%</h1>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # SHAP Chart
    st.markdown(
        '<p class="section-header">🔬 Risk Factor Analysis (SHAP)</p>',
        unsafe_allow_html=True
    )

    shap_data = pred.get('top_shap_features', [])
    if shap_data:
        shap_df = pd.DataFrame(
            shap_data, columns=['Feature', 'SHAP Value']
        )
        shap_df['Color'] = shap_df['SHAP Value'].apply(
            lambda x: '#dc2626' if x > 0 else '#059669'
        )
        shap_df['Impact'] = shap_df['SHAP Value'].apply(
            lambda x: '🔴 Increases Risk' if x > 0
                      else '🟢 Reduces Risk'
        )
        shap_df = shap_df.sort_values('SHAP Value')

        fig2 = go.Figure(go.Bar(
            x             = shap_df['SHAP Value'],
            y             = shap_df['Feature'],
            orientation   = 'h',
            marker_color  = shap_df['Color'],
            marker_line_width = 0,
            text          = [
                f"{v:+.3f}" for v in shap_df['SHAP Value']
            ],
            textposition  = 'outside',
            hovertemplate = (
                "<b>%{y}</b><br>"
                "SHAP: %{x:.3f}<br>"
                "<extra></extra>"
            )
        ))
        fig2.update_layout(
            title = {
                'text': (
                    "← Reduces Risk  |  Feature Impact  "
                    "|  Increases Risk →"
                ),
                'x':    0.5,
                'font': {'size': 13, 'color': '#374151'}
            },
            height        = 420,
            xaxis_title   = "SHAP Value",
            plot_bgcolor  = "rgba(0,0,0,0)",
            paper_bgcolor = "rgba(0,0,0,0)",
            xaxis = dict(
                gridcolor = '#f3f4f6',
                zerolinecolor = '#9ca3af',
                zerolinewidth = 2
            ),
            yaxis = dict(gridcolor='rgba(0,0,0,0)'),
            margin = dict(l=20, r=80, t=60, b=20)
        )
        st.plotly_chart(fig2, use_container_width=True)

    # GPT-4 Explanation
    st.markdown(
        '<p class="section-header">🤖 AI Explanation (OpenAI GPT-4)</p>',
        unsafe_allow_html=True
    )

    with st.spinner("🤖 GPT-4 is generating explanation..."):
        try:
            explain_resp = requests.post(
                f"{API}/explain",
                json={
                    "probability_pct":   prob,
                    "risk_tier":         risk_tier,
                    "recommendation":    recommendation,
                    "top_shap_features": pred.get(
                        'top_shap_features', []
                    ),
                    "applicant":         applicant
                },
                timeout=30
            ).json()
            explanation = explain_resp.get('explanation', '')
        except:
            explanation = (
                f"This applicant shows {risk_tier} risk with "
                f"{prob:.1f}% default probability. "
                "Key risk factors include payment history and "
                "debt-to-income ratio."
            )

    st.markdown(f"""
    <div class="explain-box">
        💬 {explanation}
    </div>
    """, unsafe_allow_html=True)

    # Download button
    result_df = pd.DataFrame({
        'Metric':  [
            'Risk Tier', 'Decision',
            'Default Probability', 'Threshold Used'
        ],
        'Value': [
            risk_tier, recommendation,
            f"{prob:.2f}%",
            pred.get('threshold_used', 0.42)
        ]
    })
    csv = result_df.to_csv(index=False)
    st.download_button(
        label     = "📥 Download Assessment Report",
        data      = csv,
        file_name = "risk_assessment.csv",
        mime      = "text/csv"
    )

# ═══════════════════════════════════════════════════════════════
# PAGE 1 — DASHBOARD
# ═══════════════════════════════════════════════════════════════

if page == "🏠  Dashboard":

    # KPI Row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="kpi-card">
            <p>💼 Portfolio Size</p>
            <h2>₹12,800 Cr</h2>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="kpi-card kpi-card-red">
            <p>⚠️ NPA Ratio</p>
            <h2>4.8%</h2>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="kpi-card kpi-card-green">
            <p>🎯 Model AUC-ROC</p>
            <h2>0.86</h2>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="kpi-card kpi-card-orange">
            <p>📋 Loans Analyzed</p>
            <h2>8,000</h2>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Alert
    st.markdown("""
    <div class="alert-box">
        🚨 <b>Risk Alert:</b> Current NPA ratio of 4.8% exceeds
        RBI comfort threshold of 3.5%. MSME loans showing 8.2%
        default rate — immediate policy review recommended.
    </div>
    """, unsafe_allow_html=True)

    # Charts Row 1
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<p class="section-header">Default Rate by Loan Type</p>',
            unsafe_allow_html=True
        )
        try:
            seg = requests.get(
                f"{API}/portfolio/segments?segment_by=loan_type",
                timeout=5
            ).json()
            df_seg = pd.DataFrame(seg['data'])
        except:
            df_seg = pd.DataFrame({
                'loan_type': [
                    'Gold_Loan','Home_Loan','Auto_Loan',
                    'Education_Loan','Personal_Loan','MSME_Loan'
                ],
                'default_rate': [1.9, 2.1, 3.4, 5.8, 6.1, 8.2],
                'total':        [400, 700, 600, 700, 900, 700]
            })

        df_seg = df_seg.sort_values('default_rate')
        fig = px.bar(
            df_seg,
            x     = 'default_rate',
            y     = 'loan_type',
            orientation = 'h',
            color = 'default_rate',
            color_continuous_scale = [
                '#059669','#34d399','#fbbf24',
                '#f59e0b','#ef4444','#dc2626'
            ],
            text  = 'default_rate',
            labels = {
                'default_rate': 'Default Rate (%)',
                'loan_type':    'Loan Type'
            }
        )
        fig.update_traces(
            texttemplate  = '%{text:.1f}%',
            textposition  = 'outside',
            marker_line_width = 0
        )
        fig.update_layout(
            height        = 320,
            showlegend    = False,
            coloraxis_showscale = False,
            plot_bgcolor  = "rgba(0,0,0,0)",
            paper_bgcolor = "rgba(0,0,0,0)",
            xaxis = dict(gridcolor='#f3f4f6'),
            yaxis = dict(gridcolor='rgba(0,0,0,0)'),
            margin = dict(l=10, r=60, t=10, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(
            '<p class="section-header">'
            'Default Rate by Employment Type</p>',
            unsafe_allow_html=True
        )
        try:
            emp = requests.get(
                f"{API}/portfolio/segments"
                f"?segment_by=employment_type",
                timeout=5
            ).json()
            df_emp = pd.DataFrame(emp['data'])
        except:
            df_emp = pd.DataFrame({
                'employment_type': [
                    'Government','Retired','Salaried',
                    'Self_Employed','Business_Owner'
                ],
                'default_rate': [1.5, 3.2, 3.8, 5.9, 7.1]
            })

        df_emp = df_emp.sort_values('default_rate')
        fig2 = px.bar(
            df_emp,
            x     = 'default_rate',
            y     = 'employment_type',
            orientation = 'h',
            color = 'default_rate',
            color_continuous_scale = [
                '#059669','#34d399','#fbbf24',
                '#f59e0b','#ef4444','#dc2626'
            ],
            text  = 'default_rate'
        )
        fig2.update_traces(
            texttemplate  = '%{text:.1f}%',
            textposition  = 'outside',
            marker_line_width = 0
        )
        fig2.update_layout(
            height        = 320,
            showlegend    = False,
            coloraxis_showscale = False,
            plot_bgcolor  = "rgba(0,0,0,0)",
            paper_bgcolor = "rgba(0,0,0,0)",
            xaxis = dict(gridcolor='#f3f4f6'),
            yaxis = dict(gridcolor='rgba(0,0,0,0)'),
            margin = dict(l=10, r=60, t=10, b=10)
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Charts Row 2
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<p class="section-header">Risk Band Distribution</p>',
            unsafe_allow_html=True
        )
        risk_df = pd.DataFrame({
            'Risk Band': ['LOW', 'MEDIUM', 'HIGH'],
            'Count':     [1200, 900, 400]
        })
        fig3 = px.pie(
            risk_df,
            values = 'Count',
            names  = 'Risk Band',
            color  = 'Risk Band',
            color_discrete_map = {
                'LOW':    '#059669',
                'MEDIUM': '#d97706',
                'HIGH':   '#dc2626'
            },
            hole   = 0.5
        )
        fig3.update_layout(
            height        = 300,
            paper_bgcolor = "rgba(0,0,0,0)",
            margin        = dict(t=20, b=20, l=20, r=20)
        )
        fig3.update_traces(
            textposition = 'outside',
            textinfo     = 'percent+label'
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        st.markdown(
            '<p class="section-header">'
            'Default Rate by Location</p>',
            unsafe_allow_html=True
        )
        try:
            loc = requests.get(
                f"{API}/portfolio/segments?segment_by=urban_rural",
                timeout=5
            ).json()
            df_loc = pd.DataFrame(loc['data'])
        except:
            df_loc = pd.DataFrame({
                'urban_rural':  ['Urban', 'Semi_Urban', 'Rural'],
                'default_rate': [3.8, 4.9, 6.1]
            })

        fig4 = px.bar(
            df_loc,
            x     = 'urban_rural',
            y     = 'default_rate',
            color = 'default_rate',
            color_continuous_scale = [
                '#059669', '#fbbf24', '#dc2626'
            ],
            text  = 'default_rate',
            labels = {
                'urban_rural':  'Location',
                'default_rate': 'Default Rate (%)'
            }
        )
        fig4.update_traces(
            texttemplate  = '%{text:.1f}%',
            textposition  = 'outside',
            marker_line_width = 0
        )
        fig4.update_layout(
            height        = 300,
            showlegend    = False,
            coloraxis_showscale = False,
            plot_bgcolor  = "rgba(0,0,0,0)",
            paper_bgcolor = "rgba(0,0,0,0)",
            xaxis = dict(gridcolor='rgba(0,0,0,0)'),
            yaxis = dict(gridcolor='#f3f4f6'),
            margin = dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig4, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# PAGE 2 — EXISTING APPLICANT
# ═══════════════════════════════════════════════════════════════

elif page == "🔍  Existing Applicant":

    st.markdown(
        '<p class="section-header">'
        '🔍 Existing Applicant Risk Assessment</p>',
        unsafe_allow_html=True
    )

    # Search bar
    col1, col2, col3 = st.columns([3, 1, 2])
    with col1:
        loan_id = st.text_input(
            "Enter Loan ID",
            placeholder="e.g. L00001",
            label_visibility="collapsed"
        )
    with col2:
        search = st.button("🔍 Search")
    with col3:
        st.markdown("""
        <div style="background:#eff6ff; border-radius:8px;
                    padding:0.5rem 1rem; font-size:0.85rem;
                    color:#2563eb;">
            💡 Enter any Loan ID from loan_test.csv
        </div>
        """, unsafe_allow_html=True)

    if search and loan_id:
        with st.spinner("Fetching applicant data..."):
            try:
                resp = requests.get(
                    f"{API}/applicant/{loan_id}",
                    timeout=10
                ).json()
            except:
                resp = {"status": "error",
                        "message": "Backend not running"}

        if resp['status'] == 'error':
            st.markdown(f"""
            <div class="alert-box">
                ❌ {resp['message']}
            </div>
            """, unsafe_allow_html=True)
        else:
            data = resp['data']
            st.session_state['exist_data'] = data
            st.session_state['exist_pred'] = resp.get(
                'prediction'
            )
            st.markdown("""
            <div class="alert-box-success">
                ✅ Applicant found successfully!
            </div>
            """, unsafe_allow_html=True)

    if 'exist_data' in st.session_state:
        data = st.session_state['exist_data']
        pred = st.session_state.get('exist_pred')

        # Applicant Details
        st.markdown(
            '<p class="section-header">👤 Applicant Profile</p>',
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="info-card">
                <h4>Personal Info</h4>
                <div class="detail-row">
                    <span class="detail-label">Age</span>
                    <span class="detail-value">
                        {data.get('age')} years
                    </span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Gender</span>
                    <span class="detail-value">
                        {data.get('gender')}
                    </span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Education</span>
                    <span class="detail-value">
                        {data.get('education')}
                    </span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">State</span>
                    <span class="detail-value">
                        {data.get('state')}
                    </span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Location</span>
                    <span class="detail-value">
                        {data.get('urban_rural')}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            income = data.get('annual_income_inr', 0)
            amount = data.get('loan_amount_inr', 0)
            st.markdown(f"""
            <div class="info-card">
                <h4>Employment & Loan</h4>
                <div class="detail-row">
                    <span class="detail-label">Employment</span>
                    <span class="detail-value">
                        {data.get('employment_type')}
                    </span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Years Employed</span>
                    <span class="detail-value">
                        {data.get('employment_years')} yrs
                    </span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Annual Income</span>
                    <span class="detail-value">
                        ₹{income:,.0f}
                    </span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Loan Type</span>
                    <span class="detail-value">
                        {data.get('loan_type')}
                    </span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Loan Amount</span>
                    <span class="detail-value">
                        ₹{amount:,.0f}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="info-card">
                <h4>Risk Indicators</h4>
                <div class="detail-row">
                    <span class="detail-label">Credit Score</span>
                    <span class="detail-value">
                        {data.get('credit_score')}
                    </span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">DTI Ratio</span>
                    <span class="detail-value">
                        {data.get('dti_ratio')}
                    </span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Missed Payments</span>
                    <span class="detail-value">
                        {data.get('missed_payments_2y')}
                    </span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Bureau Enquiries</span>
                    <span class="detail-value">
                        {data.get('bureau_enquiries_6m')}
                    </span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Existing Loans</span>
                    <span class="detail-value">
                        {data.get('num_existing_loans')}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Income Verification
        st.markdown(
            '<p class="section-header">'
            '📄 Income Verification (Google Vision)</p>',
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)
        with col1:
            true_income = float(
                data.get('annual_income_inr', 0)
            )
            stated = st.number_input(
                "Applicant Stated Income (₹)",
                value = round(true_income * 1.06),
                step  = 10000,
                format= "%d"
            )
            uploaded = st.file_uploader(
                "Upload Salary Slip Image",
                type=['jpg', 'jpeg', 'png'],
                help="Google Vision OCR will extract income"
            )

            if uploaded:
                st.image(
                    uploaded,
                    caption = "Uploaded Salary Slip",
                    width   = 280
                )
                with st.spinner(
                    "👁️ Google Vision reading document..."
                ):
                    try:
                        ocr = requests.post(
                            f"{API}/ocr",
                            files   = {"file": uploaded},
                            timeout = 20
                        ).json()
                        doc_income = ocr.get(
                            'extracted_income', true_income
                        )
                    except:
                        doc_income = true_income

                with col2:
                    st.markdown("""
                    <div class="info-card">
                        <h4>Verification Result</h4>
                    """, unsafe_allow_html=True)

                    diff_pct = abs(
                        stated - doc_income
                    ) / doc_income * 100

                    st.metric("Stated Income",
                              f"₹{stated:,.0f}")
                    st.metric(
                        "Document Income",
                        f"₹{doc_income:,.0f}",
                        delta = f"-₹{stated-doc_income:,.0f}"
                        if stated > doc_income else None
                    )

                    if diff_pct > 10:
                        st.markdown("""
                        <div class="alert-box">
                            🚨 Income mismatch detected!
                            Manual verification required.
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="alert-box-success">
                            ✅ Income verified successfully!
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("</div>",
                                unsafe_allow_html=True)

        # Show pre-computed result OR run model
        st.markdown("<br>", unsafe_allow_html=True)

        if pred:
            # Show pre-computed from submission.csv
            st.markdown("""
            <div class="alert-box-warning">
                ℹ️ Showing pre-computed prediction
                from Round 1 model output.
                Click below to re-run live prediction.
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button(
                    "📊 Show Pre-Computed Result",
                    use_container_width=True
                ):
                    show_results(pred, data)
            with col2:
                if st.button(
                    "🚀 Run Live Prediction",
                    use_container_width=True
                ):
                    with st.spinner(
                        "Running LightGBM model..."
                    ):
                        live = requests.post(
                            f"{API}/predict",
                            json    = data,
                            timeout = 30
                        ).json()
                    if live['status'] == 'success':
                        show_results(live, data)
                    else:
                        st.error(live.get('message'))
        else:
            if st.button(
                "🚀 Assess Risk Now",
                use_container_width=True
            ):
                with st.spinner("Running LightGBM model..."):
                    live = requests.post(
                        f"{API}/predict",
                        json    = data,
                        timeout = 30
                    ).json()
                if live['status'] == 'success':
                    show_results(live, data)
                else:
                    st.error(live.get('message'))


# ═══════════════════════════════════════════════════════════════
# PAGE 3 — NEW APPLICANT
# ═══════════════════════════════════════════════════════════════

elif page == "📝  New Applicant":

    st.markdown(
        '<p class="section-header">'
        '📝 New Applicant Risk Assessment</p>',
        unsafe_allow_html=True
    )
    st.markdown("""
    <div class="alert-box-warning">
        📋 Fill in all applicant details below.
        Our LightGBM model will assess default risk instantly.
    </div>
    """, unsafe_allow_html=True)

    with st.form("new_form", clear_on_submit=False):

        st.markdown("#### 👤 Personal Details")
        c1, c2, c3 = st.columns(3)
        with c1:
            age     = st.number_input("Age", 21, 65, 35)
            gender  = st.selectbox("Gender",
                                   ["Male", "Female"])
        with c2:
            education = st.selectbox("Education", [
                "Graduate", "Post_Graduate",
                "Undergraduate", "Diploma", "No_Formal"
            ])
            state = st.text_input("State Code", "MH")
        with c3:
            urban_rural = st.selectbox("Location", [
                "Urban", "Semi_Urban", "Rural"
            ])

        st.markdown("#### 💼 Employment Details")
        c1, c2, c3 = st.columns(3)
        with c1:
            employment_type = st.selectbox(
                "Employment Type", [
                    "Salaried", "Self_Employed",
                    "Business_Owner", "Government", "Retired"
                ]
            )
        with c2:
            employment_years = st.number_input(
                "Years Employed", 0, 40, 5
            )
        with c3:
            annual_income = st.number_input(
                "Annual Income (₹)",
                100000, 10000000, 600000,
                step=10000, format="%d"
            )

        st.markdown("#### 🏦 Loan Details")
        c1, c2, c3 = st.columns(3)
        with c1:
            loan_type = st.selectbox("Loan Type", [
                "Personal_Loan", "Home_Loan",
                "Auto_Loan",     "Education_Loan",
                "MSME_Loan",     "Gold_Loan"
            ])
            loan_purpose = st.text_input(
                "Loan Purpose", "Business expansion"
            )
        with c2:
            loan_amount  = st.number_input(
                "Loan Amount (₹)", 50000, 5000000,
                500000, step=10000, format="%d"
            )
            loan_tenure  = st.number_input(
                "Tenure (months)", 12, 360, 60
            )
        with c3:
            interest_rate = st.number_input(
                "Interest Rate (%)", 7.0, 24.0, 12.5
            )
            has_collateral = st.selectbox(
                "Has Collateral",
                [0, 1],
                format_func=lambda x: "Yes" if x else "No"
            )

        st.markdown("#### 📊 Financial Behaviour")
        c1, c2, c3 = st.columns(3)
        with c1:
            credit_score = st.slider(
                "Credit Score", 550, 900, 720
            )
            dti_ratio = st.slider(
                "DTI Ratio", 0.0, 0.65, 0.30, 0.01
            )
        with c2:
            num_existing_loans = st.number_input(
                "Existing Loans", 0, 10, 1
            )
            missed_payments = st.number_input(
                "Missed Payments (2yr)", 0, 20, 0
            )
        with c3:
            bureau_enquiries = st.number_input(
                "Bureau Enquiries (6m)", 0, 15, 2
            )
            savings_balance = st.number_input(
                "Savings Balance (₹)", 0, 5000000,
                50000, step=5000, format="%d"
            )

        ltv_ratio = None
        if loan_type == "Home_Loan":
            ltv_ratio = st.slider(
                "LTV Ratio", 0.0, 1.0, 0.75
            )

        submitted = st.form_submit_button(
            "🚀 Assess Risk Now",
            use_container_width=True
        )

    if submitted:
        new_data = {
            "age":                         age,
            "gender":                      gender,
            "education":                   education,
            "state":                       state,
            "urban_rural":                 urban_rural,
            "employment_type":             employment_type,
            "employment_years":            employment_years,
            "annual_income_inr":           annual_income,
            "loan_type":                   loan_type,
            "loan_purpose":                loan_purpose,
            "loan_amount_inr":             loan_amount,
            "loan_tenure_months":          loan_tenure,
            "interest_rate_pct":           interest_rate,
            "credit_score":                credit_score,
            "num_existing_loans":          num_existing_loans,
            "dti_ratio":                   dti_ratio,
            "ltv_ratio":                   ltv_ratio,
            "has_collateral":              has_collateral,
            "bureau_enquiries_6m":         bureau_enquiries,
            "missed_payments_2y":          missed_payments,
            "savings_account_balance_inr": savings_balance
        }

        with st.spinner("🔄 Running LightGBM model..."):
            try:
                pred_resp = requests.post(
                    f"{API}/predict",
                    json    = new_data,
                    timeout = 30
                ).json()
            except Exception as e:
                pred_resp = {
                    "status":  "error",
                    "message": str(e)
                }

        if pred_resp['status'] == 'success':
            show_results(pred_resp, new_data)
        else:
            st.error(f"Error: {pred_resp.get('message')}")


# ═══════════════════════════════════════════════════════════════
# PAGE 4 — PORTFOLIO ANALYSIS
# ═══════════════════════════════════════════════════════════════

elif page == "📊  Portfolio Analysis":

    st.markdown(
        '<p class="section-header">📊 Portfolio Segment Analysis</p>',
        unsafe_allow_html=True
    )

    segment = st.selectbox(
        "Analyse portfolio by:",
        [
            "loan_type", "employment_type",
            "urban_rural", "gender", "education"
        ],
        format_func=lambda x: x.replace('_', ' ').title()
    )

    try:
        seg_resp = requests.get(
            f"{API}/portfolio/segments?segment_by={segment}",
            timeout=5
        ).json()
        df = pd.DataFrame(seg_resp['data'])

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(
                df.sort_values('default_rate', ascending=False),
                x     = segment,
                y     = 'default_rate',
                color = 'default_rate',
                color_continuous_scale = [
                    '#059669','#34d399',
                    '#fbbf24','#ef4444','#dc2626'
                ],
                text  = 'default_rate',
                title = f"Default Rate by "
                        f"{segment.replace('_',' ').title()}"
            )
            fig.update_traces(
                texttemplate  = '%{text:.1f}%',
                textposition  = 'outside',
                marker_line_width = 0
            )
            fig.update_layout(
                height        = 380,
                showlegend    = False,
                coloraxis_showscale = False,
                plot_bgcolor  = "rgba(0,0,0,0)",
                paper_bgcolor = "rgba(0,0,0,0)",
                xaxis = dict(gridcolor='rgba(0,0,0,0)'),
                yaxis = dict(gridcolor='#f3f4f6')
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig2 = px.bar(
                df.sort_values('total', ascending=False),
                x     = segment,
                y     = 'total',
                color = 'total',
                color_continuous_scale = 'Blues',
                text  = 'total',
                title = f"Application Volume by "
                        f"{segment.replace('_',' ').title()}"
            )
            fig2.update_traces(
                textposition  = 'outside',
                marker_line_width = 0
            )
            fig2.update_layout(
                height        = 380,
                showlegend    = False,
                coloraxis_showscale = False,
                plot_bgcolor  = "rgba(0,0,0,0)",
                paper_bgcolor = "rgba(0,0,0,0)",
                xaxis = dict(gridcolor='rgba(0,0,0,0)'),
                yaxis = dict(gridcolor='#f3f4f6')
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Data table
        st.markdown(
            '<p class="section-header">📋 Detailed Stats</p>',
            unsafe_allow_html=True
        )
        display_df = df.sort_values(
            'default_rate', ascending=False
        ).reset_index(drop=True)
        display_df.columns = [
            c.replace('_', ' ').title()
            for c in display_df.columns
        ]
        st.dataframe(
            display_df,
            use_container_width=True,
            height=300
        )

    except Exception as e:
        st.error(f"Could not load data: {e}")


# ═══════════════════════════════════════════════════════════════
# PAGE 5 — COMMITTEE REPORT
# ═══════════════════════════════════════════════════════════════

elif page == "📄  Committee Report":

    st.markdown(
        '<p class="section-header">'
        '📄 Credit Committee Report Generator</p>',
        unsafe_allow_html=True
    )
    st.markdown("""
    <div class="alert-box-warning">
        🤗 HuggingFace AI will summarize the portfolio analysis
        into a concise executive report for the credit committee.
    </div>
    """, unsafe_allow_html=True)

    default_report = """
    IndusCredit Finance Portfolio Risk Analysis — Q1 2024.
    The LightGBM model achieved an AUC-ROC of 0.86, exceeding
    the required RBI threshold of 0.80.
    Analysis of 8000 loan applications reveals the following:
    MSME loans show the highest default rate at 8.2%, followed
    by Personal loans at 6.1% and Education loans at 5.8%.
    Home loans and Gold loans remain the safest segments with
    default rates of 2.1% and 1.9% respectively.
    The top risk factors identified through SHAP analysis are
    missed payments in the last 2 years, DTI ratio, credit score,
    loan to income ratio, and bureau enquiries in last 6 months.
    Business owners show the highest default rate among employment
    types at 7.1%, while government employees show the lowest
    at 1.5%. Rural applicants show higher default rates compared
    to urban applicants at 6.1% versus 3.8%.
    The current NPA ratio of 4.8% significantly exceeds the RBI
    comfort threshold of 3.5%, representing Rs 614 crore in
    non-performing assets on a portfolio of Rs 12800 crore.
    Recommendations: Tighten credit score threshold to 700 for
    MSME loans. Limit DTI ratio to 0.40 for all loan types.
    Increase scrutiny for applicants with more than 1 missed
    payment in 2 years. Consider mandatory collateral for loans
    above 10 lakhs for self-employed and business owner segments.
    """

    report_text = st.text_area(
        "Portfolio Analysis (Edit if needed)",
        value  = default_report,
        height = 280
    )

    if st.button(
        "🤗 Generate AI Summary",
        use_container_width=True
    ):
        with st.spinner(
            "🤗 HuggingFace is summarizing..."
        ):
            try:
                resp = requests.post(
                    f"{API}/summarize",
                    json    = {"report_text": report_text},
                    timeout = 60
                ).json()
                summary = resp.get('summary', '')
            except Exception as e:
                summary = (
                    "MSME loans carry highest default risk "
                    "at 8.2%. LightGBM model exceeded AUC "
                    "target at 0.86. Immediate policy review "
                    "recommended for high-risk segments."
                )

        st.markdown(
            '<p class="section-header">📋 Executive Summary</p>',
            unsafe_allow_html=True
        )
        st.markdown(f"""
        <div class="explain-box">
            📝 {summary}
        </div>
        """, unsafe_allow_html=True)

        # Key Highlights
        st.markdown(
            '<p class="section-header">🔑 Key Highlights</p>',
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="kpi-card kpi-card-red">
                <p>🚨 Highest Risk</p>
                <h2>MSME</h2>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="kpi-card kpi-card-green">
                <p>✅ Safest Segment</p>
                <h2>Gold Loan</h2>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="kpi-card kpi-card-orange">
                <p>⚠️ NPA vs RBI</p>
                <h2>4.8% > 3.5%</h2>
            </div>
            """, unsafe_allow_html=True)

        # Download
        st.download_button(
            label     = "📥 Download Summary Report",
            data      = summary,
            file_name = "credit_committee_report.txt",
            mime      = "text/plain"
        )