import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Review Analysis - Top 200 Companies",
    page_icon="📊",
    layout="wide"
)

def main():


    # Main content
    st.title("Review Analysis Results")
    st.markdown("### Explore and analyze your AI-powered company evaluations")

    try:
        session = st.connection("snowflake").session()
        
        # Get summary statistics
        st.markdown("## 📈 Analysis Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Total analysis runs
            try:
                result = session.sql("SELECT COUNT(DISTINCT run_id) as count FROM cortex_output WHERE run_id IS NOT NULL").collect()
                run_count = result[0]['COUNT'] if result else 0
                st.metric("🔄 Total Runs", run_count)
            except:
                st.metric("🔄 Total Runs", "0")
        
        with col2:
            # Total analyses
            try:
                result = session.sql("SELECT COUNT(*) as count FROM cortex_output").collect()
                analysis_count = result[0]['COUNT'] if result else 0
                st.metric("📊 Total Analyses", analysis_count)
            except:
                st.metric("📊 Total Analyses", "0")
        
        with col3:
            # Unique companies analyzed
            try:
                result = session.sql("SELECT COUNT(DISTINCT data_source) as count FROM cortex_output").collect()
                company_count = result[0]['COUNT'] if result else 0
                st.metric("🏢 Companies", company_count)
            except:
                st.metric("🏢 Companies", "0")
        
        with col4:
            # Unique criteria used
            try:
                result = session.sql("SELECT COUNT(DISTINCT criteria_id) as count FROM cortex_output").collect()
                criteria_count = result[0]['COUNT'] if result else 0
                st.metric("📋 Criteria", criteria_count)
            except:
                st.metric("📋 Criteria", "0")
        
        st.markdown("---")
        
        # Recent analysis runs
        st.markdown("## 📅 Recent Analysis Runs")
        
        # Get recent runs
        recent_runs = session.sql("""
        SELECT 
            RUN_ID,
            COUNT(DISTINCT CRITERIA_ID) as criteria_count,
            COUNT(DISTINCT DATA_SOURCE) as companies_analyzed,
            COUNT(*) as total_analyses,
            MIN(OUTPUT:timestamp::string) as run_timestamp
        FROM cortex_output 
        WHERE RUN_ID IS NOT NULL
        GROUP BY RUN_ID
        ORDER BY MIN(OUTPUT:timestamp::timestamp_ntz) DESC
        LIMIT 10
        """).collect()
        
        if recent_runs:
            # Display recent runs table
            runs_data = []
            for run in recent_runs:
                runs_data.append({
                    'Run ID': run['RUN_ID'],
                    'Criteria': run['CRITERIA_COUNT'],
                    'Companies': run['COMPANIES_ANALYZED'],
                    'Total Analyses': run['TOTAL_ANALYSES'],
                    'Timestamp': run['RUN_TIMESTAMP']
                })
            
            runs_df = pd.DataFrame(runs_data)
            st.dataframe(runs_df, use_container_width=True)
            
            st.markdown("---")
            
            # Detailed analysis viewer
            st.markdown("## 🔍 Detailed Analysis Viewer")
            
            # Select a run to view details
            selected_run = st.selectbox(
                "Select a run to view detailed results:",
                options=[''] + [run['RUN_ID'] for run in recent_runs],
                format_func=lambda x: f"{x} - {next((str(r['CRITERIA_COUNT']) + ' criteria × ' + str(r['COMPANIES_ANALYZED']) + ' companies (' + r['RUN_TIMESTAMP'][:10] + ')' for r in recent_runs if r['RUN_ID'] == x), '')}" if x else "Select a run..."
            )
            
            if selected_run:
                # Display detailed results for selected run
                detailed_results = session.sql(f"""
                SELECT 
                    CRITERIA_ID,
                    CRITERIA_VERSION,
                    DATA_SOURCE as company,
                    QUESTION,
                    RESULT,
                    JUSTIFICATION,
                    EVIDENCE,
                    OUTPUT:timestamp::string as timestamp
                FROM cortex_output 
                WHERE RUN_ID = '{selected_run}'
                ORDER BY CRITERIA_ID, DATA_SOURCE
                """).collect()
                
                if detailed_results:
                    st.markdown(f"### 📋 Results for Run: `{selected_run}`")
                    
                    # Analysis summary for this run
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        unique_criteria = len(set(r['CRITERIA_ID'] for r in detailed_results))
                        st.metric("📋 Criteria in Run", unique_criteria)
                    with col2:
                        unique_companies = len(set(r['COMPANY'] for r in detailed_results))
                        st.metric("🏢 Companies in Run", unique_companies)
                    with col3:
                        total_results = len(detailed_results)
                        st.metric("📊 Total Results", total_results)
                    
                    # Results display options
                    display_mode = st.radio(
                        "Choose display format:",
                        ["📋 By Criteria", "🏢 By Company", "📊 Data Table"],
                        horizontal=True
                    )
                    
                    if display_mode == "📋 By Criteria":
                        # Group by criteria for better display
                        criteria_groups = {}
                        for result in detailed_results:
                            criteria_key = f"{result['CRITERIA_ID']} ({result['CRITERIA_VERSION']})"
                            if criteria_key not in criteria_groups:
                                criteria_groups[criteria_key] = []
                            criteria_groups[criteria_key].append(result)
                        
                        for criteria_name, criteria_results in criteria_groups.items():
                            st.markdown(f"#### 📋 {criteria_name}")
                            
                            # Show the question
                            if criteria_results:
                                st.markdown(f"**Question:** {criteria_results[0]['QUESTION']}")
                            
                            for result in criteria_results:
                                with st.expander(f"🏢 {result['COMPANY']}", expanded=False):
                                    st.markdown(f"**Timestamp:** {result['TIMESTAMP']}")
                                    st.markdown("**Analysis Result:**")
                                    st.markdown(result['RESULT'])
                                    if result['EVIDENCE']:
                                        st.markdown(f"**Evidence:** {result['EVIDENCE']}")
                                    if result['JUSTIFICATION']:
                                        st.markdown(f"**Justification:** {result['JUSTIFICATION']}")
                            st.markdown("---")
                    
                    elif display_mode == "🏢 By Company":
                        # Group by company
                        company_groups = {}
                        for result in detailed_results:
                            company = result['COMPANY']
                            if company not in company_groups:
                                company_groups[company] = []
                            company_groups[company].append(result)
                        
                        for company, company_results in company_groups.items():
                            st.markdown(f"#### 🏢 {company}")
                            
                            for result in company_results:
                                criteria_name = f"{result['CRITERIA_ID']} ({result['CRITERIA_VERSION']})"
                                with st.expander(f"📋 {criteria_name}", expanded=False):
                                    st.markdown(f"**Question:** {result['QUESTION']}")
                                    st.markdown(f"**Timestamp:** {result['TIMESTAMP']}")
                                    st.markdown("**Analysis Result:**")
                                    st.markdown(result['RESULT'])
                                    if result['EVIDENCE']:
                                        st.markdown(f"**Evidence:** {result['EVIDENCE']}")
                                    if result['JUSTIFICATION']:
                                        st.markdown(f"**Justification:** {result['JUSTIFICATION']}")
                            st.markdown("---")
                    
                    else:  # Data Table
                        # Show as a comprehensive data table
                        table_data = []
                        for result in detailed_results:
                            table_data.append({
                                'Criteria': f"{result['CRITERIA_ID']} ({result['CRITERIA_VERSION']})",
                                'Company': result['COMPANY'],
                                'Question': result['QUESTION'],
                                'Result Preview': result['RESULT'][:150] + "..." if len(result['RESULT']) > 150 else result['RESULT'],
                                'Timestamp': result['TIMESTAMP']
                            })
                        
                        table_df = pd.DataFrame(table_data)
                        st.dataframe(table_df, use_container_width=True)
                        
                        # Download option
                        if st.button("📥 Download Full Results as CSV"):
                            full_data = []
                            for result in detailed_results:
                                full_data.append({
                                    'Run_ID': selected_run,
                                    'Criteria_ID': result['CRITERIA_ID'],
                                    'Criteria_Version': result['CRITERIA_VERSION'],
                                    'Company': result['COMPANY'],
                                    'Question': result['QUESTION'],
                                    'Result': result['RESULT'],
                                    'Justification': result['JUSTIFICATION'],
                                    'Evidence': result['EVIDENCE'],
                                    'Timestamp': result['TIMESTAMP']
                                })
                            
                            full_df = pd.DataFrame(full_data)
                            csv_string = full_df.to_csv(index=False)
                            
                            st.download_button(
                                label="📄 Download CSV",
                                data=csv_string,
                                file_name=f"analysis_results_{selected_run}.csv",
                                mime="text/csv"
                            )
        
        else:
            st.info("📭 No analysis results found. Run your first analysis using the AI Analysis page!")
            if st.button("🚀 Go to AI Analysis"):
                st.switch_page("pages/ai_analysis.py")
                
    except Exception as e:
        st.error(f"❌ Error loading analysis results: {e}")
        st.info("Please check your Snowflake connection and ensure the cortex_output table exists.")

if __name__ == "__main__":
    main() 