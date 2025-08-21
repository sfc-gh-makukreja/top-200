import streamlit as st
import pandas as pd
import json
from snowflake.snowpark import Session
import uuid
from typing import List, Dict, Any, Optional
import time

# Page configuration
st.set_page_config(
    page_title="Criteria Management",
    page_icon="⚙️",
    layout="wide"
)

def get_snowflake_session() -> Session:
    """Initialize Snowflake session using Streamlit connection."""
    try:
        return st.connection("snowflake").session()
    except Exception as e:
        st.error(f"Failed to connect to Snowflake: {e}")
        st.stop()

def get_all_criteria(session: Session) -> pd.DataFrame:
    """Fetch all criteria from the database."""
    try:
        result = session.sql("""
            SELECT id, question, cluster, role, instructions, output, 
                   criteria_prompt, weight, version, active
            FROM input_criteria
            ORDER BY question, version DESC
        """).collect()
        
        if result:
            df = pd.DataFrame([row.as_dict() for row in result])
            # Convert cluster to string
            if 'CLUSTER' in df.columns:
                df['CLUSTER'] = df['CLUSTER'].astype(str)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching criteria: {e}")
        return pd.DataFrame()

def save_criteria(session: Session, criteria_data: Dict[str, Any], is_edit: bool = False) -> bool:
    """Save or update criteria in the database."""
    try:
        # Convert cluster string to array
        cluster_list = [item.strip() for item in criteria_data['cluster'].split(',') if item.strip()]
        
        if is_edit:
            # Update existing criteria - use ARRAY_CONSTRUCT for proper ARRAY type
            if cluster_list:
                placeholders = ', '.join(['?' for _ in cluster_list])
                cluster_sql = f"ARRAY_CONSTRUCT({placeholders})"
                params = [criteria_data['question']] + cluster_list
            else:
                cluster_sql = "ARRAY_CONSTRUCT()"
                params = [criteria_data['question']]
                
            query = f"""
                UPDATE input_criteria 
                SET question = ?, cluster = {cluster_sql}, role = ?, instructions = ?, 
                    output = ?, criteria_prompt = ?, weight = ?, version = ?, active = ?
                WHERE id = ?
            """
            params += [
                criteria_data['role'],
                criteria_data['instructions'],
                criteria_data['output'],
                criteria_data['criteria_prompt'],
                criteria_data['weight'],
                criteria_data['version'],
                criteria_data['active'],
                criteria_data['id']
            ]
            session.sql(query, params).collect()
        else:
            # Insert new criteria - use ARRAY_CONSTRUCT for proper ARRAY type
            if cluster_list:
                placeholders = ', '.join(['?' for _ in cluster_list])
                cluster_sql = f"ARRAY_CONSTRUCT({placeholders})"
                params = [criteria_data['id'], criteria_data['question']] + cluster_list
            else:
                cluster_sql = "ARRAY_CONSTRUCT()"
                params = [criteria_data['id'], criteria_data['question']]
                
            query = f"""
                INSERT INTO input_criteria 
                (id, question, cluster, role, instructions, output, criteria_prompt, weight, version, active)
                SELECT ? as id,
                       ? as question, 
                       {cluster_sql} as cluster,
                       ? as role, 
                       ? as instructions,
                       ? as output,
                       ? as criteria_prompt,
                       ? as weight,
                       ? as version,
                       ? as active
            """
            params += [
                criteria_data['role'],
                criteria_data['instructions'],
                criteria_data['output'],
                criteria_data['criteria_prompt'],
                criteria_data['weight'],
                criteria_data['version'],
                criteria_data['active']
            ]
            session.sql(query, params).collect()
        
        return True
    except Exception as e:
        st.error(f"Error saving criteria: {e}")
        return False

def delete_criteria(session: Session, criteria_id: str) -> bool:
    """Delete criteria from the database."""
    try:
        session.sql("DELETE FROM input_criteria WHERE id = ?", [criteria_id]).collect()
        return True
    except Exception as e:
        st.error(f"Error deleting criteria: {e}")
        return False

def toggle_criteria_status(session: Session, criteria_id: str, active: bool) -> bool:
    """Toggle the active status of criteria."""
    try:
        session.sql("UPDATE input_criteria SET active = ? WHERE id = ?", [active, criteria_id]).collect()
        return True
    except Exception as e:
        st.error(f"Error updating criteria status: {e}")
        return False

def generate_criteria_prompt(current_id: str, question: str, cluster: str, role: str, instructions: str, output: str, related_questions: List[Dict] = None) -> str:
    """Generate the criteria prompt using the specified XML structure."""
    if related_questions is None:
        related_questions = []
    
    # Parse cluster into array format
    cluster_list = [item.strip() for item in cluster.split(',') if item.strip()] if cluster else []
    cluster_str = ', '.join(cluster_list)
    
    # Build the questions section
    questions_section = []
    
    # Add current question
    if question.strip():
        questions_section.append(f"{current_id} <cluster>{cluster_str}</cluster><question>{question}</question>")
    
    # Add related questions (same ID prefix)
    for rel_q in related_questions:
        if rel_q.get('ID') != current_id:  # Don't duplicate current question
            rel_cluster = ', '.join(rel_q.get('CLUSTER', [])) if rel_q.get('CLUSTER') else ''
            questions_section.append(f"{rel_q.get('ID', '')} <cluster>{rel_cluster}</cluster><question>{rel_q.get('QUESTION', '')}</question>")
    
    # Build the complete prompt
    prompt_parts = []
    
    if role.strip():
        prompt_parts.append(f"<role>\n{role.strip()}\n</role>")
    
    if instructions.strip():
        prompt_parts.append(f"<instructions>\n{instructions.strip()}\n</instructions>")
    
    if questions_section:
        prompt_parts.append(f"<questions>\n{chr(10).join(questions_section)}\n</questions>")
    
    if output.strip():
        prompt_parts.append(f"<output>\n{output.strip()}\n</output>")
    
    if current_id.strip():
        prompt_parts.append(f"<task>\nAnswer question {current_id}\n</task>")
    
    return "\n\n".join(prompt_parts)

def get_related_questions(session: Session, current_id: str) -> List[Dict]:
    """Get related questions with the same ID prefix (e.g., A.x for A.1)."""
    try:
        # Extract the prefix (e.g., "A" from "A.1")
        id_prefix = current_id.split('.')[0] if '.' in current_id else current_id[0]
        
        result = session.sql("""
            SELECT id, question, cluster
            FROM input_criteria
            WHERE id LIKE ? AND active = true
            ORDER BY id
        """, [f"{id_prefix}.%"]).collect()
        
        if result:
            return [row.as_dict() for row in result]
        return []
    except Exception as e:
        st.error(f"Error fetching related questions: {e}")
        return []

def criteria_form(existing_data: Optional[Dict] = None, session: Session = None) -> Optional[Dict[str, Any]]:
    """Display a form for creating or editing criteria."""
    
    # Form defaults
    defaults = {
        'id': str(uuid.uuid4()),
        'question': '',
        'cluster': '',
        'role': '',
        'instructions': '',
        'output': '',
        'criteria_prompt': '',
        'weight': 1.0,
        'version': '1.0',
        'active': True
    }
    
    # Use existing data if editing
    if existing_data:
        # Map database column names to form field names
        field_mapping = {
            'ID': 'id',
            'QUESTION': 'question', 
            'CLUSTER': 'cluster',
            'ROLE': 'role',
            'INSTRUCTIONS': 'instructions',
            'OUTPUT': 'output',
            'CRITERIA_PROMPT': 'criteria_prompt',
            'WEIGHT': 'weight',
            'VERSION': 'version',
            'ACTIVE': 'active'
        }
        
        for db_field, form_field in field_mapping.items():
            if db_field in existing_data and existing_data[db_field] is not None:
                defaults[form_field] = existing_data[db_field]
        
        # Special handling for CLUSTER field
        if 'CLUSTER' in existing_data and existing_data['CLUSTER']:
            if isinstance(existing_data['CLUSTER'], list):
                defaults['cluster'] = ', '.join(existing_data['CLUSTER'])
            else:
                defaults['cluster'] = str(existing_data['CLUSTER'])
    
    # Create unique form key based on mode and criteria ID
    form_mode = 'edit' if existing_data else 'add'
    # Clean the ID to make it form-key safe
    clean_id = str(defaults['id']).replace('.', '_').replace(' ', '_').replace('-', '_')
    form_key = f"criteria_form_{form_mode}_{clean_id}"
    
    # Dynamic prompt checkbox - OUTSIDE the form so it can update immediately
    is_edit_mode = existing_data is not None
    # Use the same clean ID for consistency
    dynamic_prompt_key = f"dynamic_prompt_{clean_id}"
    
    # Initialize dynamic prompt state - default to True for both add and edit modes
    if dynamic_prompt_key not in st.session_state:
        st.session_state[dynamic_prompt_key] = True
    
    # We'll move the checkbox next to the criteria prompt text area
    
    # Fetch related questions for edit mode (only once)
    related_questions = []
    if existing_data and session:
        related_questions = get_related_questions(session, defaults['id'])
    
    # Initialize form field session states for real-time updates
    form_fields = {
        'id': f"form_id_{clean_id}",
        'question': f"form_question_{clean_id}",
        'cluster': f"form_cluster_{clean_id}",
        'role': f"form_role_{clean_id}",
        'instructions': f"form_instructions_{clean_id}",
        'output': f"form_output_{clean_id}",
        'criteria_prompt': f"form_criteria_prompt_{clean_id}"
    }
    
    # Initialize session state for form fields
    for field, key in form_fields.items():
        if key not in st.session_state:
            st.session_state[key] = defaults[field]
    
    def update_criteria_prompt():
        """Update the criteria prompt when any field changes and dynamic mode is on."""
        if st.session_state.get(dynamic_prompt_key, False):
            auto_generated_prompt = generate_criteria_prompt(
                current_id=st.session_state.get(form_fields['id'], ''),
                question=st.session_state.get(form_fields['question'], ''),
                cluster=st.session_state.get(form_fields['cluster'], ''),
                role=st.session_state.get(form_fields['role'], ''),
                instructions=st.session_state.get(form_fields['instructions'], ''),
                output=st.session_state.get(form_fields['output'], ''),
                related_questions=related_questions
            )
            st.session_state[form_fields['criteria_prompt']] = auto_generated_prompt
    
    # Real-time fields OUTSIDE form for immediate updates
    st.subheader("📝 Form Fields")
    
    # ID field at the top
    id_field = st.text_input(
        "Criteria ID *",
        value=st.session_state[form_fields['id']],
        key=form_fields['id'],
        help="Unique identifier for the criteria (e.g., A.1, B.2, CUSTOM_001)",
        placeholder="A.1",
        on_change=update_criteria_prompt
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        question = st.text_area(
            "Question *",
            value=st.session_state[form_fields['question']],
            key=form_fields['question'],
            help="The main question or evaluation criteria",
            height=100,
            on_change=update_criteria_prompt
        )
        
        cluster = st.text_input(
            "Cluster",
            value=st.session_state[form_fields['cluster']],
            key=form_fields['cluster'],
            help="Comma-separated list of clusters/categories (e.g., Financial, ESG, Strategy)",
            on_change=update_criteria_prompt
        )
        
        role = st.text_input(
            "Role",
            value=st.session_state[form_fields['role']],
            key=form_fields['role'],
            help="Role or perspective for evaluation (e.g., Financial Analyst, ESG Expert)",
            on_change=update_criteria_prompt
        )
        
        instructions = st.text_area(
            "Instructions",
            value=st.session_state[form_fields['instructions']],
            key=form_fields['instructions'],
            help="Detailed instructions for evaluation",
            height=150,
            on_change=update_criteria_prompt
        )
    
    with col2:
        output = st.text_input(
            "Expected Output",
            value=st.session_state[form_fields['output']],
            key=form_fields['output'],
            help="Format or type of expected output (e.g., Score 1-10, Yes/No, Percentage)",
            on_change=update_criteria_prompt
        )
        
        # Dynamic prompt checkbox - right above the text area
        dynamic_prompt = st.checkbox(
            "🤖 Dynamic (auto-generate)",
            value=st.session_state.get(dynamic_prompt_key, True),
            key=dynamic_prompt_key,
            help="When checked, the criteria prompt will be auto-generated from other fields"
        )
        
        # Update criteria prompt in session state if dynamic mode is on
        if dynamic_prompt:
            update_criteria_prompt()
        
        # Always show the text area, but disable it when dynamic mode is on
        criteria_prompt_label = "Criteria Prompt *" + (" (Auto-generated)" if dynamic_prompt else "")
        criteria_prompt = st.text_area(
            criteria_prompt_label,
            value=st.session_state[form_fields['criteria_prompt']],
            help="The actual prompt to be used with AI models" + (" - Currently in auto-generate mode" if dynamic_prompt else ""),
            height=200,
            disabled=dynamic_prompt,
            placeholder="Enter your criteria prompt here..." if not dynamic_prompt else "This will be auto-generated based on other fields"
        )
    
    # Additional fields in columns
    col3, col4 = st.columns(2)
    with col3:
        weight = st.number_input(
            "Weight",
            min_value=0.0,
            max_value=10.0,
            value=float(defaults['weight']),
            step=0.1,
            help="Weight for this criteria in overall scoring"
        )
        
        version = st.text_input(
            "Version",
            value=defaults['version'],
            help="Version identifier for this criteria"
        )
    
    with col4:
        active = st.checkbox(
            "Active",
            value=defaults['active'],
            help="Whether this criteria is currently active"
        )
    
    # Simple form with just buttons for submission
    with st.form(form_key):
        
        # Form buttons
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
        
        with col_btn1:
            submitted = st.form_submit_button("💾 Save", type="primary")
        
        with col_btn2:
            cancelled = st.form_submit_button("❌ Cancel")
        
        if cancelled:
            # Clean up dynamic prompt session state  
            if dynamic_prompt_key in st.session_state:
                del st.session_state[dynamic_prompt_key]
            
            if st.session_state.edit_mode:
                st.session_state.edit_mode = False
            else:
                st.session_state.show_add_form = False
            st.session_state.selected_criteria = None
            st.rerun()
            return None
            
        if submitted:
            # Get values from session state
            current_id = st.session_state.get(form_fields['id'], '').strip()
            current_question = st.session_state.get(form_fields['question'], '').strip()
            current_cluster = st.session_state.get(form_fields['cluster'], '').strip()
            current_role = st.session_state.get(form_fields['role'], '').strip()
            current_instructions = st.session_state.get(form_fields['instructions'], '').strip()
            current_output = st.session_state.get(form_fields['output'], '').strip()
            current_criteria_prompt = st.session_state.get(form_fields['criteria_prompt'], '').strip()
            
            # Validation
            if not current_id:
                st.error("Criteria ID is required")
                return None
            if not current_question:
                st.error("Question is required")
                return None
            if not dynamic_prompt and not current_criteria_prompt:
                st.error("Criteria Prompt is required when not in dynamic mode")
                return None
            
            return {
                'id': current_id,
                'question': current_question,
                'cluster': current_cluster,
                'role': current_role,
                'instructions': current_instructions,
                'output': current_output,
                'criteria_prompt': current_criteria_prompt,
                'weight': weight,
                'version': version.strip(),
                'active': active,
                'dynamic_prompt': dynamic_prompt
            }
    
    return None

def main():
    st.title("Criteria Management")
    st.markdown("Manage evaluation criteria for document analysis")
    
    # Initialize session
    session = get_snowflake_session()
    
    # Initialize session states
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False
    if 'selected_criteria' not in st.session_state:
        st.session_state.selected_criteria = None
    if 'show_add_form' not in st.session_state:
        st.session_state.show_add_form = False
    if 'show_upload' not in st.session_state:
        st.session_state.show_upload = False
    
    # Action buttons
    col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
    
    with col1:
        if st.button("➕ Add New", type="primary"):
            st.session_state.show_add_form = True
            st.session_state.edit_mode = False
            st.session_state.selected_criteria = None
            # Clear any existing dynamic prompt session state
            for key in list(st.session_state.keys()):
                if key.startswith("dynamic_prompt_"):
                    del st.session_state[key]
    
    with col2:
        if st.button("🔄 Refresh"):
            st.session_state.edit_mode = False
            st.session_state.selected_criteria = None
            st.session_state.show_add_form = False
            # Clear any existing dynamic prompt session state
            for key in list(st.session_state.keys()):
                if key.startswith("dynamic_prompt_"):
                    del st.session_state[key]
            st.rerun()
    
    with col3:
        if st.button("📤 Bulk Upload"):
            st.session_state.show_upload = not st.session_state.get('show_upload', False)
            st.session_state.show_add_form = False
            st.session_state.edit_mode = False
    
    # Show CSV upload section if requested
    if st.session_state.get('show_upload', False):
        st.markdown("---")
        st.subheader("📤 Bulk Upload Criteria from CSV")
        
        with st.expander("📋 CSV Format Requirements", expanded=False):
            st.markdown("""
            **Required columns (case-sensitive):**
            - `ID` - Unique identifier (e.g., A.1, B.2)
            - `QUESTION` - The evaluation question
            - `CLUSTER` - JSON array format: `["Strategy", "Planning cycle"]`
            - `ROLE` - Role definition (can include XML tags)
            - `INSTRUCTIONS` - Instructions (can include XML tags)
            - `OUTPUT` - Output format (can include XML tags)
            - `CRITERIA_PROMPT` - Full prompt with XML structure
            - `WEIGHT` - Numeric weight (e.g., 0.05)
            - `VERSION` - Version string (e.g., 20250723)
            - `ACTIVE` - Boolean (True/False)
            
            **Example:** Use `input_criteria_transformed.csv` as a template.
            """)
        
        uploaded_file = st.file_uploader(
            "Choose CSV file",
            type=['csv'],
            help="Upload a CSV file with criteria data matching the format above"
        )
        
        if uploaded_file is not None:
            try:
                # Read CSV
                import pandas as pd
                df = pd.read_csv(uploaded_file)
                
                st.subheader(f"📊 Preview: {len(df)} criteria found")
                st.dataframe(df.head(), use_container_width=True)
                
                col_upload1, col_upload2 = st.columns([1, 3])
                
                with col_upload1:
                    if st.button("✅ Import All", type="primary"):
                        success_count = 0
                        error_count = 0
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for idx, row in df.iterrows():
                            try:
                                # Parse cluster from JSON string to list
                                import json
                                cluster_list = []
                                if row['CLUSTER'] and str(row['CLUSTER']).strip() and str(row['CLUSTER']).strip() != 'nan':
                                    try:
                                        cluster_list = json.loads(str(row['CLUSTER']))
                                    except (json.JSONDecodeError, ValueError):
                                        # Fallback: treat as comma-separated string
                                        cluster_list = [item.strip() for item in str(row['CLUSTER']).split(',') if item.strip()]
                                
                                criteria_data = {
                                    'id': str(row['ID']),
                                    'question': str(row['QUESTION']),
                                    'cluster': ', '.join(cluster_list) if cluster_list else '',
                                    'role': str(row['ROLE']) if row['ROLE'] and str(row['ROLE']) != 'nan' else '',
                                    'instructions': str(row['INSTRUCTIONS']) if row['INSTRUCTIONS'] and str(row['INSTRUCTIONS']) != 'nan' else '',
                                    'output': str(row['OUTPUT']) if row['OUTPUT'] and str(row['OUTPUT']) != 'nan' else '',
                                    'criteria_prompt': str(row['CRITERIA_PROMPT']) if row['CRITERIA_PROMPT'] and str(row['CRITERIA_PROMPT']) != 'nan' else '',
                                    'weight': float(row['WEIGHT']) if row['WEIGHT'] and str(row['WEIGHT']) != 'nan' else 1.0,
                                    'version': str(row['VERSION']) if row['VERSION'] and str(row['VERSION']) != 'nan' else '1.0',
                                    'active': bool(row['ACTIVE']) if row['ACTIVE'] and str(row['ACTIVE']) != 'nan' else True
                                }
                                
                                if save_criteria(session, criteria_data):
                                    success_count += 1
                                else:
                                    error_count += 1
                                    
                                # Update progress
                                progress = (idx + 1) / len(df)
                                progress_bar.progress(progress)
                                status_text.text(f"Processing {idx + 1}/{len(df)}: {row['ID']}")
                                
                            except Exception as e:
                                error_count += 1
                                st.error(f"Error processing row {idx + 1} ({row.get('ID', 'unknown')}): {e}")
                        
                        # Final status
                        st.success(f"✅ Import complete! {success_count} criteria imported, {error_count} errors.")
                        if error_count == 0:
                            st.session_state.show_upload = False
                            st.rerun()
                
                with col_upload2:
                    if st.button("❌ Cancel Upload"):
                        st.session_state.show_upload = False
                        st.rerun()
                        
            except Exception as e:
                st.error(f"Error reading CSV file: {e}")
                st.info("Please check that your CSV file matches the required format.")

    # Show add form if requested
    if st.session_state.show_add_form and not st.session_state.edit_mode:
        st.subheader("Add New Criteria")
        
        form_data = criteria_form(session=session)
        
        if form_data is not None:
            if save_criteria(session, form_data, is_edit=False):
                # Clean up dynamic prompt session state
                clean_form_id = str(form_data['id']).replace('.', '_').replace(' ', '_').replace('-', '_')
                dynamic_prompt_key = f"dynamic_prompt_{clean_form_id}"
                if dynamic_prompt_key in st.session_state:
                    del st.session_state[dynamic_prompt_key]
                    
                st.success("✅ Criteria added successfully!")
                st.session_state.show_add_form = False
                time.sleep(1)
                st.rerun()
        elif form_data is None and 'cancelled' in locals():
            st.session_state.show_add_form = False
            st.rerun()
    
    # Show edit form if in edit mode
    elif st.session_state.edit_mode and st.session_state.selected_criteria:
        st.subheader(f"✏️ Edit Criteria: {st.session_state.selected_criteria.get('ID', 'Unknown')}")
        
        # Add cancel button
        # col_edit1, col_edit2 = st.columns([1, 4])
        # with col_edit1:
            # if st.button("❌ Cancel Edit"):
            #     st.session_state.edit_mode = False
            #     st.session_state.selected_criteria = None
            #     st.rerun()
        
        form_data = criteria_form(st.session_state.selected_criteria, session)
        
        if form_data is not None:
            if save_criteria(session, form_data, is_edit=True):
                # Clean up dynamic prompt session state
                clean_form_id = str(form_data['id']).replace('.', '_').replace(' ', '_').replace('-', '_')
                dynamic_prompt_key = f"dynamic_prompt_{clean_form_id}"
                if dynamic_prompt_key in st.session_state:
                    del st.session_state[dynamic_prompt_key]
                    
                st.success("✅ Criteria updated successfully!")
                st.session_state.edit_mode = False
                st.session_state.selected_criteria = None
                time.sleep(1)
                st.rerun()
        elif form_data is None and not st.session_state.edit_mode:
            # Form was cancelled
            st.session_state.edit_mode = False
            st.session_state.selected_criteria = None
            st.rerun()
    
    # Display existing criteria
    st.subheader("Existing Criteria")
    
    criteria_df = get_all_criteria(session)
    
    if not criteria_df.empty:
        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Criteria", len(criteria_df))
        with col2:
            active_count = len(criteria_df[criteria_df['ACTIVE'] == True])
            st.metric("Active", active_count)
        with col3:
            inactive_count = len(criteria_df[criteria_df['ACTIVE'] == False])
            st.metric("Inactive", inactive_count)
        with col4:
            versions = criteria_df['VERSION'].nunique()
            st.metric("Versions", versions)
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("Filter by Status", ["All", "Active", "Inactive"])
        with col2:
            version_filter = st.selectbox("Filter by Version", ["All"] + sorted(criteria_df['VERSION'].unique().tolist()))
        with col3:
            role_filter = st.selectbox("Filter by Role", ["All"] + sorted([r for r in criteria_df['ROLE'].unique() if r]))
        
        # Apply filters
        filtered_df = criteria_df.copy()
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['ACTIVE'] == (status_filter == "Active")]
        if version_filter != "All":
            filtered_df = filtered_df[filtered_df['VERSION'] == version_filter]
        if role_filter != "All":
            filtered_df = filtered_df[filtered_df['ROLE'] == role_filter]
        
        # Sort by ID
        filtered_df = filtered_df.sort_values('ID')
        
        # Display criteria table
        for idx, row in filtered_df.iterrows():
            with st.expander(f"📋 **`{row['ID']}`** - {row['QUESTION'][:100]}{'...' if len(row['QUESTION']) > 100 else ''}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**ID:** `{row['ID']}`")
                    st.markdown(f"**Question:** {row['QUESTION']}")
                    st.markdown(f"**Role:** {row['ROLE'] or 'Not specified'}")
                    st.markdown(f"**Cluster:** {row.get('CLUSTER', 'Not specified')}")
                    st.markdown(f"**Instructions:** {row['INSTRUCTIONS'] or 'Not specified'}")
                    st.markdown(f"**Expected Output:** {row['OUTPUT'] or 'Not specified'}")
                    st.markdown(f"**Weight:** {row['WEIGHT']}")
                    st.markdown(f"**Version:** {row['VERSION']}")
                    
                    # Show/hide criteria prompt with button
                    if st.button(f"👁️ View Prompt", key=f"view_prompt_{row['ID']}"):
                        st.session_state[f"show_prompt_{row['ID']}"] = not st.session_state.get(f"show_prompt_{row['ID']}", False)
                    
                    if st.session_state.get(f"show_prompt_{row['ID']}", False):
                        st.code(row['CRITERIA_PROMPT'], language="text")
                
                with col2:
                    # Status indicator
                    status_color = "🟢" if row['ACTIVE'] else "🔴"
                    st.markdown(f"**Status:** {status_color} {'Active' if row['ACTIVE'] else 'Inactive'}")
                    
                    st.markdown("**Actions:**")
                    
                    # Edit button
                    if st.button(f"✏️ Edit", key=f"edit_{row['ID']}"):
                        st.session_state.edit_mode = True
                        # Convert pandas Series to dict and ensure proper data types
                        selected_data = row.to_dict()
                        # Ensure CLUSTER is properly formatted
                        if 'CLUSTER' in selected_data and selected_data['CLUSTER']:
                            if isinstance(selected_data['CLUSTER'], list):
                                selected_data['CLUSTER'] = ', '.join(selected_data['CLUSTER'])
                        st.session_state.selected_criteria = selected_data
                        st.session_state.show_add_form = False
                        st.session_state.show_upload = False
                        st.rerun()
                    
                    # Toggle status button
                    toggle_text = "Deactivate" if row['ACTIVE'] else "Activate"
                    if st.button(f"🔄 {toggle_text}", key=f"toggle_{row['ID']}"):
                        if toggle_criteria_status(session, row['ID'], not row['ACTIVE']):
                            st.success(f"✅ Criteria {toggle_text.lower()}d!")
                            time.sleep(1)
                            st.rerun()
                    
                    # Delete button with confirmation
                    delete_key = f"delete_pending_{row['ID']}"
                    if not st.session_state.get(delete_key, False):
                        if st.button(f"🗑️ Delete", key=f"delete_{row['ID']}", type="secondary"):
                            st.session_state[delete_key] = True
                            st.rerun()
                    else:
                        st.warning("⚠️ Confirm deletion:")
                        col_del1, col_del2 = st.columns(2)
                        with col_del1:
                            if st.button(f"✅ Yes", key=f"confirm_delete_{row['ID']}", type="primary"):
                                if delete_criteria(session, row['ID']):
                                    st.success("✅ Criteria deleted!")
                                    st.session_state[delete_key] = False
                                    time.sleep(1)
                                    st.rerun()
                        with col_del2:
                            if st.button(f"❌ No", key=f"cancel_delete_{row['ID']}", type="secondary"):
                                st.session_state[delete_key] = False
                                st.rerun()
    
    else:
        st.info("No criteria found. Add your first criteria using the 'Add New' button above.")

if __name__ == "__main__":
    main() 