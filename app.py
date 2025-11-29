"""
Oncology Clinical Decision Support System
Final production version with proper contrast
"""

import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

from agents.supervisor import OncologySupervisor

# Page configuration
st.set_page_config(
    page_title="Oncology CDSS",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS with fixed contrast
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #1e40af;
        text-align: center;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-box {
        background: #eff6ff;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 6px solid #3b82f6;
        margin: 1rem 0;
        color: #1e293b;
    }
    .result-box h4 {
        color: #1e40af;
        margin-bottom: 0.8rem;
    }
    .result-box p {
        color: #334155;
        margin: 0.3rem 0;
    }
    .result-box strong {
        color: #0f172a;
    }
    .approve-box {
        background: #ecfdf5;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 6px solid #10b981;
        margin: 1rem 0;
        color: #1e293b;
    }
    .approve-box h4 {
        color: #047857;
        margin-bottom: 0.8rem;
    }
    .approve-box p {
        color: #334155;
        margin: 0.3rem 0;
    }
    .approve-box strong {
        color: #0f172a;
    }
    .approve-box em {
        color: #475569;
    }
    .stButton>button {
        width: 100%;
        background-color: #1e40af;
        color: white;
        border: none;
        padding: 0.6rem 1rem;
        font-weight: 600;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar - Query Builder
with st.sidebar:
    st.markdown("## 🔬 Query Builder")
    
    cancer_type = st.selectbox(
        "Cancer Type",
        ["melanoma", "lung cancer", "breast cancer", "colorectal cancer", 
         "prostate cancer", "pancreatic cancer", "renal cell carcinoma"]
    )
    
    treatment = st.text_input(
        "Treatment",
        value="pembrolizumab",
        help="Drug name or treatment type"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        start_year = st.selectbox("From", list(range(2018, 2026)), index=6)
    with col2:
        end_year = st.selectbox("To", list(range(2019, 2027)), index=6)
    
    query = f"{treatment} AND {cancer_type} AND ({start_year}/01/01:{end_year}/12/31[PDAT])"
    
    st.markdown("**Generated Query:**")
    st.code(query, language="text")
    
    st.markdown("---")
    st.info("**Model:** Gemini 2.5 Flash")
    
    if st.button("🗑️ Clear Results"):
        if "result" in st.session_state:
            del st.session_state.result
            st.rerun()

# Main Dashboard
st.markdown('<h1 class="main-header">Oncology Clinical Decision Support</h1>', 
            unsafe_allow_html=True)
st.markdown('<p class="subtitle">Evidence-based recommendations with physician oversight</p>', 
            unsafe_allow_html=True)

if st.button("▶ Run Clinical Analysis", type="primary"):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or "your_api" in api_key.lower():
        st.error("❌ GOOGLE_API_KEY not configured. Check .env file.")
        st.stop()
    
    with st.spinner("🔍 Searching literature • 📊 Analyzing survival • 👨‍⚕️ Physician review..."):
        try:
            supervisor = OncologySupervisor(model_name="gemini-2.5-flash")
            result = supervisor.process_query(query)
            
            st.session_state.result = result
            st.session_state.query = query
            
            st.success("✅ Analysis completed successfully!")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.stop()

if "result" in st.session_state:
    res = st.session_state.result
    
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Papers", res["literature"].get("total_found", 0))
    with col2:
        st.metric("P-value", f"{res['analysis'].get('p_value', 0):.4f}")
    with col3:
        st.metric("Confidence", f"{res['recommendation']['confidence_score']:.0%}")
    with col4:
        st.metric("GRADE", res['recommendation']['grade'])
    
    st.markdown("---")
    
    left, right = st.columns([1, 1])
    
    with left:
        st.markdown("### 📊 Survival Analysis")
        
        fig_path = "outputs/figures/km_survival_analysis.png"
        if os.path.exists(fig_path):
            st.image(fig_path, caption="Kaplan-Meier Survival Curve", width=600)
        else:
            st.warning("⚠️ Figure not found")
        
        with st.expander("📈 Statistical Details"):
            st.write(f"**Test:** Log-rank")
            st.write(f"**P-value:** {res['analysis'].get('p_value', 'N/A')}")
            st.write(f"**Median OS (Treatment):** {res['analysis'].get('median_pembrolizumab', 'N/A')} months")
            st.write(f"**Median OS (Control):** {res['analysis'].get('median_nivolumab', 'N/A')} months")
    
    with right:
        st.markdown("### 📋 Clinical Recommendation")
        
        rec = res["recommendation"]
        doc = res["doctor_review"]
        
        st.markdown(f"""
        <div class="result-box">
        <h4>Treatment Recommendation</h4>
        <p><strong>{doc['final_recommendation']}</strong></p>
        <p>Strength: <strong>{rec['strength_of_recommendation']} (GRADE {rec['grade']})</strong></p>
        <p>Confidence: <strong>{rec['confidence_score']:.1%}</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="approve-box">
        <h4>Physician Review</h4>
        <p>Decision: <strong>{doc['doctor_decision'].upper()}</strong></p>
        <p>Reviewer: {doc['doctor_name']}</p>
        <p><em>"{doc['comment']}"</em></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### ⚠️ Adverse Event Risk")
        risk = res["risk_profile"]
        st.error(f"**Grade 3-4 irAE:** {risk['grade_3_4_irae']}")
        st.info(f"**Monitoring:** {risk['recommendation']}")
    
    st.markdown("---")
    st.markdown("### 📚 Supporting Literature")
    
    lit = res["literature"]
    papers = lit.get("papers", [])[:15]
    
    with st.expander(f"View {len(papers)} publications"):
        for i, paper in enumerate(papers, 1):
            title = paper.get("title", "No title")
            journal = paper.get("journal", "Unknown")
            year = paper.get("year", "N/A")
            pmid = str(paper.get("pmid", "")).strip()
            
            st.markdown(f"**{i}. {title}**")
            
            info_parts = [f"*{journal}*", f"({year})"]
            if pmid and pmid.isdigit():
                info_parts.append(f"[PMID: {pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)")
            
            st.caption(" • ".join(info_parts))
            st.divider()

st.markdown("---")
st.caption("Oncology Clinical Decision Support System • Powered by Gemini 2.5 Flash")