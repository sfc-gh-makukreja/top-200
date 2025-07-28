import streamlit as st
import pandas as pd
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
            # Convert cluster array to comma-separated string for display
            if 'CLUSTER' in df.columns:
                df['CLUSTER_DISPLAY'] = df['CLUSTER'].apply(
                    lambda x: ', '.join(x) if x and isinstance(x, list) else ''
                )
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
            # Update existing criteria
            query = """
                UPDATE input_criteria 
                SET question = ?, cluster = ?, role = ?, instructions = ?, 
                    output = ?, criteria_prompt = ?, weight = ?, version = ?, active = ?
                WHERE id = ?
            """
            session.sql(query, [
                criteria_data['question'],
                cluster_list,
                criteria_data['role'],
                criteria_data['instructions'],
                criteria_data['output'],
                criteria_data['criteria_prompt'],
                criteria_data['weight'],
                criteria_data['version'],
                criteria_data['active'],
                criteria_data['id']
            ]).collect()
        else:
            # Insert new criteria
            query = """
                INSERT INTO input_criteria 
                (id, question, cluster, role, instructions, output, criteria_prompt, weight, version, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            session.sql(query, [
                criteria_data['id'],
                criteria_data['question'],
                cluster_list,
                criteria_data['role'],
                criteria_data['instructions'],
                criteria_data['output'],
                criteria_data['criteria_prompt'],
                criteria_data['weight'],
                criteria_data['version'],
                criteria_data['active']
            ]).collect()
        
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
        defaults.update(existing_data)
        if 'CLUSTER' in existing_data and existing_data['CLUSTER']:
            defaults['cluster'] = ', '.join(existing_data['CLUSTER']) if isinstance(existing_data['CLUSTER'], list) else str(existing_data['CLUSTER'])
    
    with st.form("criteria_form"):
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
            if not question.strip():
                st.error("Question is required")
                return None
            if not criteria_prompt.strip():
                st.error("Criteria Prompt is required")
                return None
            
            return {
                'id': defaults['id'],
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
    st.title("⚙️ Criteria Management")
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
        st.subheader("Edit Criteria")
        
        form_data = criteria_form(st.session_state.selected_criteria)
        
        if form_data is not None:
            if save_criteria(session, form_data, is_edit=True):
                st.success("✅ Criteria updated successfully!")
                st.session_state.edit_mode = False
                st.session_state.selected_criteria = None
                time.sleep(1)
                st.rerun()
        elif form_data is None:
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
        
        # Display criteria table
        for idx, row in filtered_df.iterrows():
            with st.expander(f"📋 {row['QUESTION'][:100]}{'...' if len(row['QUESTION']) > 100 else ''}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**ID:** `{row['ID']}`")
                    st.markdown(f"**Question:** {row['QUESTION']}")
                    st.markdown(f"**Role:** {row['ROLE'] or 'Not specified'}")
                    st.markdown(f"**Cluster:** {row.get('CLUSTER_DISPLAY', 'Not specified')}")
                    st.markdown(f"**Instructions:** {row['INSTRUCTIONS'] or 'Not specified'}")
                    st.markdown(f"**Expected Output:** {row['OUTPUT'] or 'Not specified'}")
                    st.markdown(f"**Weight:** {row['WEIGHT']}")
                    st.markdown(f"**Version:** {row['VERSION']}")
                    
                    with st.expander("View Criteria Prompt"):
                        st.code(row['CRITERIA_PROMPT'], language="text")
                
                with col2:
                    # Status indicator
                    status_color = "🟢" if row['ACTIVE'] else "🔴"
                    st.markdown(f"**Status:** {status_color} {'Active' if row['ACTIVE'] else 'Inactive'}")
                    
                    st.markdown("**Actions:**")
                    
                    # Edit button
                    if st.button(f"✏️ Edit", key=f"edit_{row['ID']}"):
                        st.session_state.edit_mode = True
                        st.session_state.selected_criteria = row.to_dict()
                        st.session_state.show_add_form = False
                        st.rerun()
                    
                    # Toggle status button
                    toggle_text = "Deactivate" if row['ACTIVE'] else "Activate"
                    if st.button(f"🔄 {toggle_text}", key=f"toggle_{row['ID']}"):
                        if toggle_criteria_status(session, row['ID'], not row['ACTIVE']):
                            st.success(f"✅ Criteria {toggle_text.lower()}d!")
                            time.sleep(1)
                            st.rerun()
                    
                    # Delete button
                    if st.button(f"🗑️ Delete", key=f"delete_{row['ID']}", type="secondary"):
                        if st.button(f"⚠️ Confirm Delete", key=f"confirm_delete_{row['ID']}", type="secondary"):
                            if delete_criteria(session, row['ID']):
                                st.success("✅ Criteria deleted!")
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.warning("Click 'Confirm Delete' to permanently delete this criteria")
    
    else:
        st.info("No criteria found. Add your first criteria using the 'Add New' button above.")

if __name__ == "__main__":
    main() 