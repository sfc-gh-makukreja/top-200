import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Top 200 Companies - AI Analysis Platform",
    page_icon="🏢",
    layout="wide"
)

def main():
    # Sidebar navigation
    with st.sidebar:
        st.title("🏢 Top 200 App")
        st.markdown("### 📑 Navigation")
        st.markdown("Use the **pages** menu in the upper left to navigate:")
        st.markdown("- **🏠 Home** (Current)")
        st.markdown("- **📄 Document Processing**")
        st.markdown("- **📋 Criteria Management**")
        st.markdown("- **🔍 AI Analysis**")
        st.markdown("- **📚 Help & Documentation**")
        st.markdown("---")
        st.markdown("### 🔗 Quick Links")
        if st.button("📄 Upload Documents", type="primary"):
            st.switch_page("pages/document_processing.py")
        if st.button("📋 Manage Criteria", type="secondary"):
            st.switch_page("pages/criteria_management.py")
        if st.button("🔍 AI Analysis", type="secondary"):
            st.switch_page("pages/ai_analysis.py")
        if st.button("📚 View Help", type="secondary"):
            st.switch_page("pages/help.py")

    # Main content
    st.title("🏢 Top 200 Companies - AI Analysis Platform")
    st.markdown("### Welcome to the comprehensive AI-powered analysis platform for evaluating company sustainability and ESG performance.")
    
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
            st.switch_page("pages/document_processing.py")
    
    with col2:
        st.markdown("""
        ### 📋 Criteria Management
        - Define custom evaluation criteria
        - Manage ESG assessment questions
        - Bulk upload from CSV
        - Role-based AI prompts
        """)
        if st.button("Manage Criteria", key="criteria_mgmt"):
            st.switch_page("pages/criteria_management.py")
    
    with col3:
        st.markdown("""
        ### 🔍 AI Analysis
        - Automated ESG scoring
        - Evidence-based evaluations
        - Comprehensive reporting
        - Deloitte methodology
        """)
        if st.button("Start Analysis", key="ai_analysis"):
            st.switch_page("pages/ai_analysis.py")
    
    # Getting started section
    st.markdown("---")
    st.markdown("## 🚀 Getting Started")
    
    with st.expander("📖 Quick Start Guide", expanded=False):
        st.markdown("""
        ### Step 1: Upload Documents 📄
        Navigate to **Document Processing** and upload PDF annual reports for analysis.
        
        ### Step 2: Define Criteria 📋
        Go to **Criteria Management** to set up evaluation questions and AI prompts.
        
        ### Step 3: Run Analysis 🔍
        Navigate to **AI Analysis** to perform automated evaluations using the RAG system.
        
        ### Step 4: Review Results 📊
        Examine AI-generated analysis, evidence, and comprehensive evaluation reports.
        """)
    
    # System status
    st.markdown("---")
    st.markdown("## 📊 System Status")
    
    try:
        # Initialize connection to show system health
        session = st.connection("snowflake").session()
        
        col1, col2, col3, col4 = st.columns(4)
        
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
                st.metric("📄 Processed Docs Chunks", doc_chunk_count, delta="Ready")
            except:
                st.metric("📄 Processed Docs Chunks", "0", delta="Ready")
        
        with col3:
            # Check for criteria
            try:
                result = session.sql("SELECT COUNT(*) as count FROM input_criteria WHERE active = TRUE").collect()
                criteria_count = result[0]['COUNT'] if result else 0
                st.metric("📋 Active Criteria", criteria_count, delta="Ready")
            except:
                st.metric("📋 Active Criteria", "0", delta="Setup needed")
        
        with col4:
            st.metric("🤖 AI Services", "Cortex", delta="Ready")
            
    except Exception as e:
        st.error("❌ System Status: Connection failed")
        st.info("Please check your Snowflake connection configuration.")

if __name__ == "__main__":
    main() 