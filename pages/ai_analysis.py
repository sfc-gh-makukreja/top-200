import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="AI Analysis - Top 200 Companies",
    page_icon="🔍",
    layout="wide"
)

def rag(query, company_name):
    from snowflake.core import Root
    from snowflake.cortex import complete
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
    
    # add <media_scan>
    media_scan_query=f"""select TOPIC_OF_DISQUALIFICATION from media_scan 
    where ai_filter(PROMPT('company name {{0}} matches exactly with {{1}}', company_name,'{company_name}'))"""

    result = session.sql(media_scan_query).to_pandas().to_xml(index=False, xml_declaration=False)
    query += f"""{query}
    <media_scan>
    {result}
    </media_scan>
    """
    
    root = Root(session)
    cortex_search_service = (
            root.databases['top_200_db']
            .schemas['top_200_schema']
            .cortex_search_services['cortex_search_service']
        )
    columns = ['chunk',
            'relative_path',
            'company_name',
            'year',
            'file_url',
            'language'] 
    filter={"@and": [{"@eq": {"company_name": company_name}}]}
    context_documents = cortex_search_service.search(
        query, columns=columns, filter=filter, limit=5
    )
    results = context_documents.results
    context_str = ""
    for i, r in enumerate(results):
        context_str += f"Context document {i+1}: {r['chunk']} \n" + "\n"
    prompt_context, results = context_str, results
    prompt = f"""{query}
    <context>
    {prompt_context}
    </context>
    """
    
    output = complete('claude-3-5-sonnet', prompt)

    return output

def get_available_companies():
    """Get list of available companies from the database"""
    try:
        session = st.connection("snowflake").session()
        result = session.sql("""
            SELECT DISTINCT company_name 
            FROM cortex_docs_chunks_table 
            ORDER BY company_name
        """).collect()
        return [row['COMPANY_NAME'] for row in result]
    except Exception as e:
        st.error(f"Error fetching companies: {e}")
        return []

def main():
    # Sidebar navigation
    with st.sidebar:
        st.title("🔍 AI Analysis")
        st.markdown("### 📑 Navigation")
        if st.button("🏠 Back to Home"):
            st.switch_page("streamlit_app.py")
        if st.button("📄 Document Processing"):
            st.switch_page("pages/document_processing.py")
        if st.button("📋 Criteria Management"):
            st.switch_page("pages/criteria_management.py")
        if st.button("📚 Help & Documentation"):
            st.switch_page("pages/help.py")

    # Main content
    st.title("🔍 AI Analysis Platform")
    st.markdown("### Perform AI-powered analysis on company documents using Snowflake Cortex")

    # Analysis configuration section
    st.markdown("## ⚙️ Analysis Configuration")
    
    # Query input
    query = st.text_area(
        "📝 Analysis Query",
        placeholder="Enter your analysis question (e.g., 'What are the key sustainability initiatives mentioned in the annual report?')",
        height=100,
        help="This query will be used to search and analyze company documents"
    )

    if not query.strip():
        st.warning("⚠️ Please enter an analysis query to proceed.")
        return

    # Company selection options
    st.markdown("## 🏢 Company Selection")
    
    # Get available companies
    with st.spinner("Loading available companies..."):
        available_companies = get_available_companies()
    
    if not available_companies:
        st.error("❌ No companies found. Please upload and process documents first.")
        return

    # Selection mode
    selection_mode = st.radio(
        "Choose analysis mode:",
        ["🎯 Select Specific Companies", "🌐 Run All Companies"],
        horizontal=True
    )

    selected_companies = []
    
    if selection_mode == "🎯 Select Specific Companies":
        # Multi-select for specific companies
        selected_companies = st.multiselect(
            "Select companies to analyze:",
            options=available_companies,
            help="You can select multiple companies for analysis"
        )
        
        if not selected_companies:
            st.warning("⚠️ Please select at least one company for analysis.")
            return
            
    else:  # Run all companies
        selected_companies = available_companies
        st.info(f"📊 Analysis will run for all {len(available_companies)} available companies")

    # Analysis execution
    st.markdown("## 🚀 Run Analysis")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            f"🔍 Start Analysis ({len(selected_companies)} companies)",
            type="primary",
            use_container_width=True
        ):
            run_analysis(query, selected_companies)

def run_analysis(query, companies):
    """Run the RAG analysis for selected companies"""
    
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    results = []
    
    for i, company in enumerate(companies):
        # Update progress
        progress = (i + 1) / len(companies)
        progress_bar.progress(progress)
        status_text.text(f"Analyzing {company}... ({i + 1}/{len(companies)})")
        
        try:
            # Run RAG analysis
            with st.spinner(f"Processing {company}..."):
                result = rag(query, company)
                results.append({
                    'company': company,
                    'result': result,
                    'status': 'success'
                })
                
        except Exception as e:
            st.error(f"❌ Error analyzing {company}: {str(e)}")
            results.append({
                'company': company,
                'result': f"Error: {str(e)}",
                'status': 'error'
            })
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    # Display results
    st.success(f"✅ Analysis completed for {len(companies)} companies")
    
    # Results display options
    display_mode = st.radio(
        "Display results as:",
        ["📋 Individual Results", "📊 Summary Table"],
        horizontal=True
    )
    
    if display_mode == "📋 Individual Results":
        # Display detailed results for each company
        for result in results:
            with st.expander(f"🏢 {result['company']}", expanded=False):
                if result['status'] == 'success':
                    st.markdown(result['result'])
                else:
                    st.error(result['result'])
    
    else:  # Summary table
        # Create summary dataframe
        summary_data = []
        for result in results:
            summary_data.append({
                'Company': result['company'],
                'Status': '✅ Success' if result['status'] == 'success' else '❌ Error',
                'Result Preview': result['result'][:200] + "..." if len(result['result']) > 200 else result['result']
            })
        
        df = pd.DataFrame(summary_data)
        st.dataframe(df, use_container_width=True)
        
        # Download results
        if st.button("📥 Download Results as CSV"):
            csv_data = []
            for result in results:
                csv_data.append({
                    'Company': result['company'],
                    'Query': query,
                    'Result': result['result'],
                    'Status': result['status']
                })
            
            csv_df = pd.DataFrame(csv_data)
            csv_string = csv_df.to_csv(index=False)
            
            st.download_button(
                label="📄 Download CSV",
                data=csv_string,
                file_name=f"ai_analysis_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main() 