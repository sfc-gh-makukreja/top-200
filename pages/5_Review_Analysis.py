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
        
        # Create tabs for different views
        tab1, tab2 = st.tabs(["🔄 View by Runs", "🏢 View by Company"])
        
        with tab1:
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
                    format_func=lambda x: f"{x} - {next((str(r['CRITERIA_COUNT']) + ' criteria × ' + str(r['COMPANIES_ANALYZED']) + ' companies (' + r['RUN_TIMESTAMP'] + ')' for r in recent_runs if r['RUN_ID'] == x), '')}" if x else "Select a run..."
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
                                    'Result': result['RESULT'],
                                    'Justification': result['JUSTIFICATION'],
                                    'Evidence': result['EVIDENCE'],
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
                    st.switch_page("pages/4_AI_Analysis.py")
        
        with tab2:
            st.markdown("## 🏢 Company Analysis View")
            
            # Get all unique companies
            try:
                companies_result = session.sql("""
                SELECT DISTINCT data_source as company_name
                FROM cortex_output 
                WHERE data_source IS NOT NULL 
                AND TRIM(data_source) != ''
                ORDER BY data_source
                """).collect()
                
                if companies_result:
                    company_names = [row['COMPANY_NAME'] for row in companies_result]
                    
                    # Company selection
                    selected_company = st.selectbox(
                        "Select a company to analyze:",
                        options=[''] + company_names,
                        format_func=lambda x: "Choose a company..." if x == '' else x
                    )
                    
                    if selected_company:
                        st.markdown(f"### 📊 Analysis Results for: **{selected_company}**")
                        
                        # Data scope selection
                        data_scope = st.radio(
                            "Select data scope:",
                            ["📈 All Runs", "🎯 Latest Run per Criteria"],
                            horizontal=True,
                            help="All Runs: Shows complete history including multiple analyses of same criteria. Latest Run per Criteria: Shows only the most recent analysis for each criteria."
                        )
                        
                        # Build appropriate query based on data scope
                        if data_scope == "📈 All Runs":
                            query = f"""
                            SELECT 
                                co.criteria_id as id,
                                co.question,
                                co.criteria_prompt,
                                ic.weight,
                                co.result,
                                co.justification,
                                co.evidence,
                                co.run_id,
                                CASE 
                                    WHEN UPPER(TRIM(co.result)) = 'YES' THEN ic.weight 
                                    ELSE 0 
                                END as score
                            FROM cortex_output co
                            LEFT JOIN input_criteria ic ON co.criteria_id = ic.id 
                                AND co.criteria_version = ic.version
                            WHERE co.data_source = '{selected_company}'
                            ORDER BY co.criteria_id, co.run_id DESC
                            """
                        else:  # Latest Run per Criteria
                            query = f"""
                            WITH latest_runs AS (
                                SELECT 
                                    criteria_id,
                                    MAX(output:timestamp::timestamp_ntz) as latest_timestamp
                                FROM cortex_output 
                                WHERE data_source = '{selected_company}'
                                GROUP BY criteria_id
                            )
                            SELECT 
                                co.criteria_id as id,
                                co.question,
                                co.criteria_prompt,
                                ic.weight,
                                co.result,
                                co.justification,
                                co.evidence,
                                co.run_id,
                                CASE 
                                    WHEN UPPER(TRIM(co.result)) = 'YES' THEN ic.weight 
                                    ELSE 0 
                                END as score
                            FROM cortex_output co
                            LEFT JOIN input_criteria ic ON co.criteria_id = ic.id 
                                AND co.criteria_version = ic.version
                            INNER JOIN latest_runs lr ON co.criteria_id = lr.criteria_id 
                                AND co.output:timestamp::timestamp_ntz = lr.latest_timestamp
                            WHERE co.data_source = '{selected_company}'
                            ORDER BY co.criteria_id
                            """
                        
                        # Execute query and display results
                        try:
                            results = session.sql(query).collect()
                            
                            if results:
                                # Convert to DataFrame for display
                                data = []
                                for row in results:
                                    data.append({
                                        'ID': row['ID'],
                                        'Question': row['QUESTION'],
                                        'Criteria Prompt': row['CRITERIA_PROMPT'],
                                        'Weight': row['WEIGHT'],
                                        'Result': row['RESULT'],
                                        'Justification': row['JUSTIFICATION'],
                                        'Evidence': row['EVIDENCE'],
                                        'Run ID': row['RUN_ID'],
                                        'Score': row['SCORE']
                                    })
                                
                                df = pd.DataFrame(data)
                                
                                # Get overall progress percentage
                                try:
                                    progress_result = session.sql("""
                                    SELECT 
                                        COUNT(DISTINCT co.criteria_id) as answered_criteria,
                                        (SELECT COUNT(*) FROM input_criteria WHERE active = TRUE) as total_active_criteria
                                    FROM cortex_output co
                                    WHERE co.data_source = ?
                                    """, params=[selected_company]).collect()
                                    
                                    if progress_result:
                                        answered_criteria = progress_result[0]['ANSWERED_CRITERIA']
                                        total_active_criteria = progress_result[0]['TOTAL_ACTIVE_CRITERIA']
                                        progress_percentage = (answered_criteria / total_active_criteria * 100) if total_active_criteria > 0 else 0
                                    else:
                                        answered_criteria = 0
                                        total_active_criteria = 0
                                        progress_percentage = 0
                                except:
                                    answered_criteria = 0
                                    total_active_criteria = 0
                                    progress_percentage = 0
                                
                                # Display metrics
                                col1, col2, col3, col4, col5 = st.columns(5)
                                with col1:
                                    st.metric("📊 Overall Progress", f"{progress_percentage:.1f}%", 
                                             help=f"{answered_criteria} of {total_active_criteria} active criteria answered")
                                with col2:
                                    st.metric("📋 Total Criteria", len(df))
                                with col3:
                                    yes_count = len(df[df['Result'].str.upper().str.strip() == 'YES'])
                                    st.metric("✅ Yes Results", yes_count)
                                with col4:
                                    total_score = df['Score'].sum()
                                    st.metric("🎯 Total Score", f"{total_score:.1f}")
                                with col5:
                                    max_possible = df['Weight'].sum()
                                    percentage = (total_score / max_possible * 100) if max_possible > 0 else 0
                                    st.metric("📊 Score %", f"{percentage:.1f}%")
                                
                                st.markdown("---")
                                
                                # Display the data table
                                st.markdown("### 📋 Detailed Results")
                                st.dataframe(
                                    df, 
                                    use_container_width=True,
                                    height=400
                                )
                                
                                # CSV Export functionality
                                st.markdown("### 📥 Export Data")
                                
                                # Prepare CSV data
                                csv_data = df.copy()
                                csv_data['Company'] = selected_company
                                csv_data['Data_Scope'] = data_scope.replace("📈 ", "").replace("🎯 ", "")
                                csv_data['Export_Timestamp'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                                
                                # Reorder columns for CSV
                                csv_columns = ['Company', 'ID', 'Question', 'Criteria Prompt', 'Weight', 
                                             'Result', 'Justification', 'Evidence', 'Run ID', 'Score', 
                                             'Data_Scope', 'Export_Timestamp']
                                csv_data = csv_data[csv_columns]
                                
                                csv_string = csv_data.to_csv(index=False)
                                
                                # Generate filename
                                scope_suffix = "all_runs" if data_scope == "📈 All Runs" else "latest_per_criteria"
                                filename = f"company_analysis_{selected_company.replace(' ', '_')}_{scope_suffix}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
                                
                                st.download_button(
                                    label="📄 Download Complete Analysis as CSV",
                                    data=csv_string,
                                    file_name=filename,
                                    mime="text/csv",
                                    help=f"Downloads all {len(df)} analysis results for {selected_company}"
                                )
                                
                            else:
                                st.info(f"📭 No analysis results found for {selected_company}")
                                
                        except Exception as e:
                            st.error(f"❌ Error retrieving company data: {e}")
                    
                else:
                    st.info("📭 No companies found in analysis results. Run your first analysis using the AI Analysis page!")
                    if st.button("🚀 Go to AI Analysis"):
                        st.switch_page("pages/4_AI_Analysis.py")
            except Exception as e:
                st.error(f"❌ Error loading companies: {e}")
                
    except Exception as e:
        st.error(f"❌ Error loading analysis results: {e}")
        st.info("Please check your Snowflake connection and ensure the cortex_output table exists.")

if __name__ == "__main__":
    main()