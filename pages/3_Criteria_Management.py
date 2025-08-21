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

def criteria_form(existing_data: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
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
    
    with st.form("criteria_form"):
        # ID field at the top
        id_field = st.text_input(
            "Criteria ID *",
            value=defaults['id'],
            help="Unique identifier for the criteria (e.g., A.1, B.2, CUSTOM_001)",
            placeholder="A.1"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            question = st.text_area(
                "Question *",
                value=defaults['question'],
                help="The main question or evaluation criteria",
                height=100
            )
            
            cluster = st.text_input(
                "Cluster",
                value=defaults['cluster'],
                help="Comma-separated list of clusters/categories (e.g., Financial, ESG, Strategy)"
            )
            
            role = st.text_input(
                "Role",
                value=defaults['role'],
                help="Role or perspective for evaluation (e.g., Financial Analyst, ESG Expert)"
            )
            
            instructions = st.text_area(
                "Instructions",
                value=defaults['instructions'],
                help="Detailed instructions for evaluation",
                height=150
            )
        
        with col2:
            output = st.text_input(
                "Expected Output",
                value=defaults['output'],
                help="Format or type of expected output (e.g., Score 1-10, Yes/No, Percentage)"
            )
            
            criteria_prompt = st.text_area(
                "Criteria Prompt *",
                value=defaults['criteria_prompt'],
                help="The actual prompt to be used with AI models",
                height=200
            )
            
            weight = st.number_input(
                "Weight",
                min_value=0.0,
                max_value=10.0,
                value=float(defaults['weight']),
                step=0.1,
                help="Weight for this criteria in overall scoring"
            )
            
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                version = st.text_input(
                    "Version",
                    value=defaults['version'],
                    help="Version identifier for this criteria"
                )
            
            with col2_2:
                active = st.checkbox(
                    "Active",
                    value=defaults['active'],
                    help="Whether this criteria is currently active"
                )
        
        # Form buttons
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
        
        with col_btn1:
            submitted = st.form_submit_button("💾 Save", type="primary")
        
        with col_btn2:
            cancelled = st.form_submit_button("❌ Cancel")
        
        if cancelled:
            return None
            
        if submitted:
            # Validation
            if not id_field.strip():
                st.error("Criteria ID is required")
                return None
            if not question.strip():
                st.error("Question is required")
                return None
            if not criteria_prompt.strip():
                st.error("Criteria Prompt is required")
                return None
            
            return {
                'id': id_field.strip(),
                'question': question.strip(),
                'cluster': cluster.strip(),
                'role': role.strip(),
                'instructions': instructions.strip(),
                'output': output.strip(),
                'criteria_prompt': criteria_prompt.strip(),
                'weight': weight,
                'version': version.strip(),
                'active': active
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
    
    with col2:
        if st.button("🔄 Refresh"):
            st.session_state.edit_mode = False
            st.session_state.selected_criteria = None
            st.session_state.show_add_form = False
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
        
        form_data = criteria_form()
        
        if form_data is not None:
            if save_criteria(session, form_data, is_edit=False):
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
        col_edit1, col_edit2 = st.columns([1, 4])
        with col_edit1:
            if st.button("❌ Cancel Edit"):
                st.session_state.edit_mode = False
                st.session_state.selected_criteria = None
                st.rerun()
        
        form_data = criteria_form(st.session_state.selected_criteria)
        
        if form_data is not None:
            if save_criteria(session, form_data, is_edit=True):
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