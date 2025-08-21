import streamlit as st
import pandas as pd
import datetime

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
    where ai_filter(PROMPT('company name {{0}} matches exactly with {{1}}', COMPANY_NAME,'{company_name}'))"""

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
            .cortex_search_services['cortex_search_service_ocr']
        )
    columns = ['final_chunk_ocr',
            'relative_path',
            'COMPANY_NAME',
            'year',
            'file_url',
            'language'] 
    filter={"@and": [{"@eq": {"COMPANY_NAME": company_name}}]}
    context_documents = cortex_search_service.search(
        query, columns=columns, filter=filter, limit=5
    )
    results = context_documents.results
    context_str = ""
    for i, r in enumerate(results):
        context_str += f"Context document {i+1}: {r['final_chunk_ocr']} \n" + "\n"
    prompt_context, results = context_str, results
    prompt = f"""{query}
    <context>
    {prompt_context}
    </context>
    """
    
    output = complete('claude-3-5-sonnet', prompt)

    return output

def get_available_companies(start_date=None, end_date=None):
    """Get list of available companies from the database, optionally filtered by upload timestamp"""
    try:
        session = st.connection("snowflake").session()
        
        # Base query
        base_query = """
            SELECT DISTINCT COMPANY_NAME 
            FROM cortex_docs_chunks_table 
        """
        
        # Add timestamp filter if dates are provided
        if start_date and end_date:
            query = base_query + """
                WHERE file_uploaded_at_nz BETWEEN ? AND ?
                ORDER BY COMPANY_NAME
            """
            result = session.sql(query, [start_date, end_date]).collect()
        else:
            query = base_query + "ORDER BY COMPANY_NAME"
            result = session.sql(query).collect()
        
        return [row['COMPANY_NAME'] for row in result]
    except Exception as e:
        st.error(f"Error fetching companies: {e}")
        return []

def get_active_criteria():
    """Get list of active criteria from input_criteria table"""
    try:
        session = st.connection("snowflake").session()
        result = session.sql("""
            SELECT 
                ID,
                VERSION,
                CRITERIA_PROMPT,
                QUESTION,
                WEIGHT
            FROM input_criteria 
            WHERE ACTIVE = TRUE
            ORDER BY ID, VERSION
        """).collect()
        
        criteria_list = []
        for row in result:
            criteria_list.append({
                'id': row['ID'],
                'version': row['VERSION'],
                'prompt': row['CRITERIA_PROMPT'],
                'question': row['QUESTION'],
                'weight': row['WEIGHT'] if row['WEIGHT'] is not None else 1.0,
                'display_name': f"{row['ID']} ({row['VERSION']})"
            })
        return criteria_list
    except Exception as e:
        st.error(f"Error fetching criteria: {e}")
        return []

def main():

    # Main content
    st.title("AI Analysis Platform")
    st.markdown("### Perform AI-powered analysis on company documents using Snowflake Cortex")

    # Quick link to review results
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("📊 **View Results:** Explore completed analyses and detailed results on the Review Analysis page.")
    with col2:
        if st.button("📊 Review Results", type="secondary"):
            st.switch_page("pages/5_Review_Analysis.py")
    
    st.markdown("---")

    # Analysis configuration section
    st.markdown("## ⚙️ New Analysis Configuration")
    
    # Criteria selection
    st.markdown("### 📝 Select Analysis Criteria")
    
    # Get available criteria
    with st.spinner("Loading active criteria..."):
        available_criteria = get_active_criteria()
    
    if not available_criteria:
        st.error("❌ No active criteria found. Please add criteria in Criteria Management first.")
        return

    # Criteria selection mode
    criteria_selection_mode = st.radio(
        "Choose criteria mode:",
        ["🎯 Select Specific Criteria", "📋 Run All Criteria"],
        horizontal=True
    )

    selected_criteria = []
    
    if criteria_selection_mode == "🎯 Select Specific Criteria":
        # Multi-select for specific criteria
        selected_criteria_names = st.multiselect(
            "Select criteria to analyze:",
            options=[c['display_name'] for c in available_criteria],
            help="You can select multiple criteria for analysis"
        )
        
        if not selected_criteria_names:
            st.warning("⚠️ Please select at least one criteria for analysis.")
            return
        
        # Get selected criteria details
        selected_criteria = [c for c in available_criteria if c['display_name'] in selected_criteria_names]
            
    else:  # Run all criteria
        selected_criteria = available_criteria
        st.info(f"📋 Analysis will run for all {len(available_criteria)} available criteria")
    
    # Show selected criteria details
    with st.expander("📋 Selected Criteria Details", expanded=False):
        for criteria in selected_criteria:
            st.markdown(f"**{criteria['display_name']}**")
            st.markdown(f"- **Question:** {criteria['question']}")
            st.markdown("---")

    # Company selection options
    st.markdown("### 🏢 Select Companies")
    
    # Get available companies
    with st.spinner("Loading available companies..."):
        available_companies = get_available_companies()
    
    if not available_companies:
        st.error("❌ No companies found. Please upload and process documents first.")
        return

    # Selection mode
    selection_mode = st.radio(
        "Choose analysis mode:",
        ["🎯 Select Specific Companies", "🌐 Run All Companies", "📅 Upload Timestamp Filter"],
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
    
    elif selection_mode == "📅 Upload Timestamp Filter":
        # Date range picker for timestamp filtering
        st.markdown("#### 📅 Select Upload Date Range")
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date (NZ time):",
                help="Select the start date for upload timestamp filter"
            )
        
        with col2:
            end_date = st.date_input(
                "End Date (NZ time):",
                help="Select the end date for upload timestamp filter"
            )
        
        if start_date and end_date:
            if start_date > end_date:
                st.error("❌ Start date must be before or equal to end date.")
                return
            
            # Convert dates to datetime strings for SQL query
            start_datetime = f"{start_date} 00:00:00"
            end_datetime = f"{end_date} 23:59:59"
            
            # Get companies filtered by timestamp
            with st.spinner("Filtering companies by upload timestamp..."):
                filtered_companies = get_available_companies(start_datetime, end_datetime)
            
            if not filtered_companies:
                st.warning(f"⚠️ No companies found with documents uploaded between {start_date} and {end_date}.")
                return
            
            selected_companies = filtered_companies
            st.info(f"📊 Found {len(filtered_companies)} companies with documents uploaded between {start_date} and {end_date}")
            
            # Show the filtered companies
            with st.expander("📋 Companies in Date Range", expanded=False):
                for company in filtered_companies:
                    st.markdown(f"• {company}")
        else:
            st.warning("⚠️ Please select both start and end dates.")
            return
            
    else:  # Run all companies
        selected_companies = available_companies
        st.info(f"📊 Analysis will run for all {len(available_companies)} available companies")

    # Analysis execution
    st.markdown("### 🚀 Run Analysis")
    
    # Show analysis matrix
    total_analyses = len(selected_criteria) * len(selected_companies)
    st.info(f"📊 **Analysis Matrix:** {len(selected_criteria)} criteria × {len(selected_companies)} companies = {total_analyses} total analyses")
    
    # Show what will be analyzed
    with st.expander("🔍 Preview Analysis Matrix", expanded=False):
        matrix_data = []
        for criteria in selected_criteria:
            for company in selected_companies:
                matrix_data.append({
                    'Criteria': criteria['display_name'],
                    'Company': company,
                    'Question': criteria['question']
                })
        
        if matrix_data:
            matrix_df = pd.DataFrame(matrix_data)
            st.dataframe(matrix_df, use_container_width=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            f"🔍 Start Analysis ({total_analyses} analyses)",
            type="primary",
            use_container_width=True
        ):
            run_analysis(selected_criteria, selected_companies)

def run_analysis(selected_criteria, companies):
    """Run the RAG analysis for selected criteria and companies (matrix analysis)"""
    
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    
    # Generate unique run_id for this analysis session
    import uuid
    import datetime
    import json
    run_id = f"analysis_{uuid.uuid4().hex[:8]}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Calculate total analyses
    total_analyses = len(selected_criteria) * len(companies)
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    results = []
    session = st.connection("snowflake").session()
    analysis_count = 0
    
    # Run analysis for each criteria-company combination
    for criteria in selected_criteria:
        for company in companies:
            analysis_count += 1
            
            # Update progress
            progress = analysis_count / total_analyses
            progress_bar.progress(progress)
            status_text.text(f"Analyzing {criteria['display_name']} for {company}... ({analysis_count}/{total_analyses})")
            
            try:
                # Run RAG analysis
                with st.spinner(f"Processing {criteria['display_name']} for {company}..."):
                    rag_output = rag(criteria['prompt'], company)
                    rag_output = json.loads(rag_output)
                    # Save to cortex_output table
                    try:
                        # Use actual criteria data
                        criteria_id = criteria['id']
                        criteria_version = criteria['version']
                        criteria_prompt = criteria['prompt']
                        question = criteria['question']
                        result = rag_output['result']
                        justification = rag_output['explanation']
                        evidence = json.dumps(rag_output['supporting_evidence'])
                        data_source = company
                        
                        # Create output JSON
                        output_json = {
                            "company": company,
                            "criteria_id": criteria_id,
                            "criteria_version": criteria_version,
                            "question": question,
                            "prompt": criteria_prompt,
                            "result": result,
                            "timestamp": datetime.datetime.now().isoformat(),
                            "run_id": run_id,
                            "analysis_type": "criteria_based_rag"
                        }
                        
                        # Insert into cortex_output table
                        insert_sql = """
                        INSERT INTO cortex_output (
                            criteria_id, criteria_version, criteria_prompt, question,
                            run_id, result, justification, evidence, data_source, output
                        ) SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?, PARSE_JSON(?)
                        """
                        
                        session.sql(insert_sql, [
                            criteria_id, criteria_version, criteria_prompt, question,
                            run_id, result, justification, evidence, data_source,
                            json.dumps(output_json)
                        ]).collect()
                        
                        results.append({
                            'criteria': criteria['display_name'],
                            'company': company,
                            'result': result,
                            'status': 'success',
                            'run_id': run_id,
                            'criteria_id': criteria_id,
                            'question': question,
                            'weight': criteria.get('weight', 1.0),
                            'justification': justification,
                            'supporting_evidence': evidence
                        })
                        
                    except Exception as db_error:
                        st.warning(f"⚠️ Analysis completed for {criteria['display_name']} - {company} but failed to save to database: {db_error}")
                        results.append({
                            'criteria': criteria['display_name'],
                            'company': company,
                            'result': rag_output['result'],
                            'status': 'success_no_save',
                            'run_id': run_id,
                            'criteria_id': criteria['id'],
                            'question': question,
                            'weight': criteria.get('weight', 1.0),
                            'justification': justification,
                            'supporting_evidence': evidence
                        })
                    
            except Exception as e:
                st.error(f"❌ Error analyzing {criteria['display_name']} for {company}: {str(e)}")
                
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    # Display results
    successful_analyses = len([r for r in results if r['status'] == 'success'])
    total_analyses = len(results)
    st.success(f"✅ Analysis completed: {successful_analyses}/{total_analyses} successful")
    
    # Show run ID and database info
    st.info(f"🔗 **Run ID:** `{run_id}` | 💾 **Database:** Results saved to `cortex_output` table")
    
    # Results display options
    display_mode = st.radio(
        "Display results as:",
        ["📋 Individual Results", "📊 Summary Table", "🎯 Matrix View"],
        horizontal=True
    )
    
    if display_mode == "📋 Individual Results":
        # Group by criteria for better organization
        criteria_groups = {}
        for rag_output in results:
            criteria_name = rag_output['criteria']
            if criteria_name not in criteria_groups:
                criteria_groups[criteria_name] = []
            criteria_groups[criteria_name].append(rag_output)
        
        # Display results grouped by criteria
        for criteria_name, criteria_results in criteria_groups.items():
            st.markdown(f"### 📋 {criteria_name}")
            
            for rag_output in criteria_results:
                status_icon = "✅" if rag_output['status'] == 'success' else "❌"
                with st.expander(f"{status_icon} {rag_output['company']}", expanded=False):
                    st.markdown(f"**Question:** {rag_output['question']}")
                    st.markdown("**Analysis Result:**")
                    if rag_output['status'] == 'success':
                        st.markdown(rag_output['result'])
                    else:
                        st.error(rag_output['result'])
            st.markdown("---")
    
    elif display_mode == "📊 Summary Table":
        # Create summary dataframe with expected format
        summary_data = []
        for rag_output in results:
            summary_data.append({
                'Company': rag_output['company'],
                'Result': rag_output['result'],
                'Justification': rag_output.get('justification', 'AI-generated analysis'),
                'Supporting Evidence': rag_output.get('supporting_evidence', f"Documents from {rag_output['company']}"),
                'Weighting': rag_output.get('weight', 1.0),
                'Status': '✅ Success' if rag_output['status'] == 'success' else '❌ Error'
            })
        
        df = pd.DataFrame(summary_data)
        st.dataframe(df, use_container_width=True)
    
    else:  # Matrix View
        # Create matrix view showing which combinations succeeded/failed
        st.markdown("### 🎯 Analysis Matrix Results")
        
        # Get unique criteria and companies
        unique_criteria = list(set(r['criteria'] for r in results))
        unique_companies = list(set(r['company'] for r in results))
        
        # Create matrix data
        matrix_data = []
        for criteria in unique_criteria:
            row = {'Criteria': criteria}
            for company in unique_companies:
                # Find result for this combination
                rag_output = next((r for r in results if r['criteria'] == criteria and r['company'] == company), None)
                if rag_output:
                    if rag_output['status'] == 'success':
                        row[company] = "✅"
                    else:
                        row[company] = "❌"
                else:
                    row[company] = "⚪"
            matrix_data.append(row)
        
        matrix_df = pd.DataFrame(matrix_data)
        st.dataframe(matrix_df, use_container_width=True)
        
        st.markdown("**Legend:** ✅ Success | ❌ Error | ⚪ Not Analyzed")
        
        # Download and database query options
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Download Results as CSV"):
                csv_data = []
                for rag_output in results:
                    csv_data.append({
                        'Company': rag_output['company'],
                        'Result': rag_output['result'] if rag_output['status'] == 'success' else 'Error',
                        'Justification': rag_output.get('justification', 'AI-generated analysis using RAG system with Cortex Search'),
                        'Supporting_Evidence': rag_output.get('supporting_evidence', rag_output.get('evidence', f"Documents from {rag_output['company']}")),
                        'Weighting': rag_output.get('weight', 1.0)
                    })
                
                csv_df = pd.DataFrame(csv_data)
                csv_string = csv_df.to_csv(index=False)
                
                st.download_button(
                    label="📄 Download CSV",
                    data=csv_string,
                    file_name=f"ai_analysis_results_{run_id}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("🔍 Query Database Results"):
                try:
                    db_results = session.sql(f"""
                    SELECT 
                        CRITERIA_ID,
                        CRITERIA_VERSION,
                        DATA_SOURCE as company,
                        QUESTION,
                        RESULT,
                        JUSTIFICATION,
                        OUTPUT:timestamp::string as timestamp
                    FROM cortex_output 
                    WHERE RUN_ID = '{run_id}'
                    ORDER BY CRITERIA_ID, DATA_SOURCE
                    """).collect()
                    
                    if db_results:
                        st.markdown("#### 📊 Database Results for Current Run")
                        db_df = pd.DataFrame([dict(row.asDict()) for row in db_results])
                        st.dataframe(db_df, use_container_width=True)
                        
                        # Show summary stats
                        total_db_results = len(db_results)
                        unique_criteria = len(set(row['CRITERIA_ID'] for row in db_results))
                        unique_companies = len(set(row['COMPANY'] for row in db_results))
                        
                        st.info(f"📈 **Summary:** {total_db_results} total analyses | {unique_criteria} criteria | {unique_companies} companies")
                    else:
                        st.warning("No results found in database for this run ID")
                        
                except Exception as e:
                    st.error(f"Error querying database: {e}")

if __name__ == "__main__":
    main() 