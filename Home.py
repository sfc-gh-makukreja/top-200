import streamlit as st
import base64


def render_image(filepath: str):
    """
    Convert image to base64 data URL for embedding in HTML
    filepath: path to the image. Must have a valid file extension.
    """
    try:
        mime_type = filepath.split('.')[-1:][0].lower()
        with open(filepath, "rb") as f:
            content_bytes = f.read()
        content_b64encoded = base64.b64encode(content_bytes).decode()
        return f'data:image/{mime_type};base64,{content_b64encoded}'
    except Exception as e:
        st.error(f"Error loading image {filepath}: {e}")
        return ""


# Page configuration
st.set_page_config(
    page_title="Deloitte Top 200 Awards - AI Analysis Platform",
    page_icon="🏢",
    layout="wide"
)

def main():
    st.markdown("# AI-powered ESG performance analysis platform")
    
    # Render logos with base64 embedding
    deloitte_img = render_image("assets/deloitte.png")
    snowflake_img = render_image("assets/snowflake.png")
    
    st.markdown(f"""
    <div style="margin: 20px 0;">
        Supporting the <img src="{deloitte_img}" alt="Deloitte" style="height: 30px; vertical-align: middle;"> 
        <a href="https://top200.co.nz/" target="_blank">Top 200 Awards</a> - Powered by 
        <img src="{snowflake_img}" alt="Snowflake" style="height: 30px; vertical-align: middle;">
    </div>
    """, unsafe_allow_html=True)
    
    # Feature overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📄 Document Processing
        - Upload PDF annual reports
        - AI-powered text extraction and chunking
        - Snowflake Cortex search integration
        - Automated document analysis
        """)
        if st.button("Start Processing", key="doc_process"):
            st.switch_page("pages/1_Document_Processing.py")
        
        st.markdown("""
        ### 📰 Media Scan Management
        - Track company disqualification topics
        - Manage negative media coverage
        - Bulk upload from CSV
        - Export and audit records
        """)
        if st.button("Manage Media Scan", key="media_scan_mgmt"):
            st.switch_page("pages/2_Media_Scan_Management.py")
    
    with col2:
        st.markdown("""
        ### 📋 Criteria Management
        - Define custom evaluation criteria
        - Manage ESG assessment questions
        - Bulk upload from CSV
        - Role-based AI prompts
        """)
        if st.button("Manage Criteria", key="criteria_mgmt"):
            st.switch_page("pages/3_Criteria_Management.py")
    
    with col3:
        st.markdown("""
        ### 🔍 AI Analysis
        - Automated ESG scoring
        - Evidence-based evaluations
        - Comprehensive reporting
        - Deloitte methodology
        """)
        if st.button("Start Analysis", key="ai_analysis"):
            st.switch_page("pages/4_AI_Analysis.py")
        
        st.markdown("""
        ### 📊 Review Analysis
        - Explore completed analysis runs
        - View detailed results by criteria/company
        - Download comprehensive reports
        - Track analysis history
        """)
        if st.button("Review Results", key="review_analysis"):
            st.switch_page("pages/5_Review_Analysis.py")
    
    # Getting started section
    st.markdown("---")
    st.markdown("## 🚀 Getting Started")
    
    with st.expander("📖 Quick Start Guide", expanded=False):
        st.markdown("""
        ### Step 1: Upload Documents 📄
        Navigate to **Document Processing** and upload PDF annual reports for analysis.
        
        ### Step 2: Manage Media Coverage 📰
        Use **Media Scan Management** to track company disqualification topics.
        
        ### Step 3: Define Criteria 📋
        Go to **Criteria Management** to set up evaluation questions and AI prompts.
        
        ### Step 4: Run Analysis 🔍
        Navigate to **AI Analysis** to perform automated evaluations using the RAG system.
        
        ### Step 5: Review Results 📊
        Navigate to **Review Analysis** to explore completed analysis runs, view detailed results, and download comprehensive reports.
        """)
    
    # System status
    st.markdown("---")
    st.markdown("## 📊 System Status")
    
    try:
        # Initialize connection to show system health
        session = st.connection("snowflake").session()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            # Check for processed documents
            try:
                result = session.sql("SELECT COUNT(*) as count FROM cortex_parsed_docs").collect()
                doc_count = result[0]['COUNT'] if result else 0
                st.metric("📄 Processed Docs", doc_count, delta="Ready")
            except:
                st.metric("📄 Processed Docs", "0", delta="Ready")        
        
        with col2:
            # Check for processed documents chunks
            try:
                result = session.sql("SELECT COUNT(*) as count FROM cortex_docs_chunks_table").collect()
                doc_chunk_count = result[0]['COUNT'] if result else 0
                st.metric("📄 Doc Chunks", doc_chunk_count, delta="Ready")
            except:
                st.metric("📄 Doc Chunks", "0", delta="Ready")
        
        with col3:
            # Check for criteria
            try:
                result = session.sql("SELECT COUNT(*) as count FROM input_criteria WHERE active = TRUE").collect()
                criteria_count = result[0]['COUNT'] if result else 0
                st.metric("📋 Active Criteria", criteria_count, delta="Ready")
            except:
                st.metric("📋 Active Criteria", "0", delta="Setup needed")
        
        with col4:
            # Check for media scan records
            try:
                result = session.sql("SELECT COUNT(*) as count FROM deloitte_200_db.deloitte_200_schema.media_scan").collect()
                media_scan_count = result[0]['COUNT'] if result else 0
                st.metric("📰 Media Scans", media_scan_count, delta="Ready")
            except:
                st.metric("📰 Media Scans", "0", delta="Setup needed")
        
        with col5:
            st.metric("🤖 AI Services", "Cortex", delta="Ready")
            
    except Exception as e:
        st.error("❌ System Status: Connection failed")
        st.info("Please check your Snowflake connection configuration.")

if __name__ == "__main__":
    main() 