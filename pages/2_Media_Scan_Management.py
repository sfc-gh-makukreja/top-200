import streamlit as st
import pandas as pd
import uuid
from snowflake.snowpark import Session
from typing import List, Dict, Any, Optional
import time

# Page configuration
st.set_page_config(
    page_title="Media Scan Management - Deloitte Top 200 Awards",
    page_icon="📰",
    layout="wide"
)

def get_snowflake_session() -> Session:
    """Initialize Snowflake session using Streamlit connection."""
    try:
        return st.connection("snowflake").session()
    except Exception as e:
        st.error(f"Failed to connect to Snowflake: {e}")
        st.stop()

def get_all_media_scans(session: Session) -> pd.DataFrame:
    """Fetch all media scan records from the database."""
    try:
        result = session.sql("""
            SELECT COMPANY_NAME, TOPIC_OF_DISQUALIFICATION
            FROM media_scan
            ORDER BY COMPANY_NAME
        """).collect()
        
        if result:
            df = pd.DataFrame([row.as_dict() for row in result])
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching media scan data: {e}")
        return pd.DataFrame()

def save_media_scan(session: Session, media_scan_data: Dict[str, Any], is_edit: bool = False, original_company_name: str = None) -> bool:
    """Save or update media scan record in the database."""
    try:
        if is_edit and original_company_name:
            # Update existing record
            query = """
                UPDATE media_scan 
                SET COMPANY_NAME = ?, TOPIC_OF_DISQUALIFICATION = ?
                WHERE COMPANY_NAME = ?
            """
            params = [
                media_scan_data['company_name'],
                media_scan_data['topic_of_disqualification'],
                original_company_name
            ]
            session.sql(query, params).collect()
        else:
            # Insert new record (or replace if exists)
            query = """
                MERGE INTO media_scan AS target
                USING (SELECT ? as COMPANY_NAME, ? as TOPIC_OF_DISQUALIFICATION) AS source
                ON target.COMPANY_NAME = source.COMPANY_NAME
                WHEN MATCHED THEN
                    UPDATE SET TOPIC_OF_DISQUALIFICATION = source.TOPIC_OF_DISQUALIFICATION
                WHEN NOT MATCHED THEN
                    INSERT (COMPANY_NAME, TOPIC_OF_DISQUALIFICATION) 
                    VALUES (source.COMPANY_NAME, source.TOPIC_OF_DISQUALIFICATION)
            """
            params = [
                media_scan_data['company_name'],
                media_scan_data['topic_of_disqualification']
            ]
            session.sql(query, params).collect()
        
        return True
    except Exception as e:
        st.error(f"Error saving media scan data: {e}")
        return False

def delete_media_scan(session: Session, company_name: str) -> bool:
    """Delete media scan record from the database."""
    try:
        session.sql(
            "DELETE FROM media_scan WHERE COMPANY_NAME = ?", 
            [company_name]
        ).collect()
        return True
    except Exception as e:
        st.error(f"Error deleting media scan record: {e}")
        return False

def media_scan_form(existing_data: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
    """Display a form for creating or editing media scan records."""
    
    # Form defaults
    defaults = {
        'company_name': '',
        'topic_of_disqualification': ''
    }
    
    # Use existing data if editing
    if existing_data:
        defaults['company_name'] = existing_data.get('COMPANY_NAME', '')
        defaults['topic_of_disqualification'] = existing_data.get('TOPIC_OF_DISQUALIFICATION', '')
    
    with st.form("media_scan_form"):
        st.markdown("### Company Media Scan Information")
        
        company_name = st.text_input(
            "Company Name *",
            value=defaults['company_name'],
            help="Enter the full company name (e.g., 'Fonterra (NZX:FCG)', 'Auckland Airport (NZX:AIA)')",
            placeholder="Company Name (Exchange:Ticker)"
        )
        
        topic_of_disqualification = st.text_area(
            "Topic of Disqualification *",
            value=defaults['topic_of_disqualification'],
            help="Describe the issues or negative topics found in media coverage",
            height=150,
            placeholder="Enter details about negative media coverage, disqualification reasons, or compliance issues..."
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
            if not company_name.strip():
                st.error("Company Name is required")
                return None
            if not topic_of_disqualification.strip():
                st.error("Topic of Disqualification is required")
                return None
            
            return {
                'company_name': company_name.strip(),
                'topic_of_disqualification': topic_of_disqualification.strip()
            }
    
    return None

def main():
    st.title("Media Scan Management")
    st.markdown("Manage company media scan records and disqualification topics")
    
    # Initialize session
    session = get_snowflake_session()
    
    # Initialize session states
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False
    if 'selected_media_scan' not in st.session_state:
        st.session_state.selected_media_scan = None
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
            st.session_state.selected_media_scan = None
    
    with col2:
        if st.button("🔄 Refresh"):
            st.session_state.edit_mode = False
            st.session_state.selected_media_scan = None
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
        st.subheader("📤 Bulk Upload Media Scan Data from CSV")
        
        with st.expander("📋 CSV Format Requirements", expanded=False):
            st.markdown("""
            **Required columns (case-sensitive):**
            - `COMPANY_NAME` - Full company name with exchange/ticker if applicable
            - `TOPIC_OF_DISQUALIFICATION` - Description of negative media coverage or issues
            
            **Example CSV format:**
            ```
            COMPANY_NAME,TOPIC_OF_DISQUALIFICATION
            "Fonterra (NZX:FCG)","Many stories of concern including: farming drained peat, job losses, greenwashing claims, methane emissions"
            "Auckland Airport (NZX:AIA)","Some competition issues around cost of airport upgrade being passed on to airlines"
            ```
            
            **Notes:**
            - Use quotes around values that contain commas
            - Each row represents one company's media scan record
            - Duplicate company names will be updated with new information
            """)
        
        uploaded_file = st.file_uploader(
            "Choose CSV file",
            type=['csv'],
            help="Upload a CSV file with media scan data matching the format above"
        )
        
        if uploaded_file is not None:
            try:
                # Read CSV
                df = pd.read_csv(uploaded_file)
                
                # Validate required columns
                required_cols = ['COMPANY_NAME', 'TOPIC_OF_DISQUALIFICATION']
                missing_cols = [col for col in required_cols if col not in df.columns]
                
                if missing_cols:
                    st.error(f"Missing required columns: {', '.join(missing_cols)}")
                    st.info("Please ensure your CSV has the exact column names as specified in the format requirements.")
                else:
                    st.subheader(f"📊 Preview: {len(df)} records found")
                    st.dataframe(df.head(10), use_container_width=True)
                    
                    col_upload1, col_upload2 = st.columns([1, 3])
                    
                    with col_upload1:
                        if st.button("✅ Import All", type="primary"):
                            success_count = 0
                            error_count = 0
                            
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            for idx, row in df.iterrows():
                                try:
                                    media_scan_data = {
                                        'company_name': str(row['COMPANY_NAME']).strip() if pd.notna(row['COMPANY_NAME']) else '',
                                        'topic_of_disqualification': str(row['TOPIC_OF_DISQUALIFICATION']).strip() if pd.notna(row['TOPIC_OF_DISQUALIFICATION']) else ''
                                    }
                                    
                                    # Skip empty rows
                                    if not media_scan_data['company_name'] or not media_scan_data['topic_of_disqualification']:
                                        error_count += 1
                                        st.warning(f"Skipped row {idx + 1}: Missing company name or topic")
                                        continue
                                    
                                    if save_media_scan(session, media_scan_data):
                                        success_count += 1
                                    else:
                                        error_count += 1
                                        
                                    # Update progress
                                    progress = (idx + 1) / len(df)
                                    progress_bar.progress(progress)
                                    status_text.text(f"Processing {idx + 1}/{len(df)}: {media_scan_data['company_name']}")
                                    
                                except Exception as e:
                                    error_count += 1
                                    st.error(f"Error processing row {idx + 1}: {e}")
                            
                            # Final status
                            st.success(f"✅ Import complete! {success_count} records imported, {error_count} errors.")
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
        st.subheader("Add New Media Scan Record")
        
        form_data = media_scan_form()
        
        if form_data is not None:
            if save_media_scan(session, form_data, is_edit=False):
                st.success("✅ Media scan record added successfully!")
                st.session_state.show_add_form = False
                time.sleep(1)
                st.rerun()
        elif form_data is None:
            st.session_state.show_add_form = False
            st.rerun()
    
    # Show edit form if in edit mode
    elif st.session_state.edit_mode and st.session_state.selected_media_scan:
        st.subheader(f"✏️ Edit Media Scan Record: {st.session_state.selected_media_scan.get('COMPANY_NAME', 'Unknown')}")
        
        # Add cancel button
        col_edit1, col_edit2 = st.columns([1, 4])
        with col_edit1:
            if st.button("❌ Cancel Edit"):
                st.session_state.edit_mode = False
                st.session_state.selected_media_scan = None
                st.rerun()
        
        form_data = media_scan_form(st.session_state.selected_media_scan)
        
        if form_data is not None:
            original_company_name = st.session_state.selected_media_scan.get('COMPANY_NAME', '')
            if save_media_scan(session, form_data, is_edit=True, original_company_name=original_company_name):
                st.success("✅ Media scan record updated successfully!")
                st.session_state.edit_mode = False
                st.session_state.selected_media_scan = None
                time.sleep(1)
                st.rerun()
        elif form_data is None:
            st.session_state.edit_mode = False
            st.session_state.selected_media_scan = None
            st.rerun()
    
    # Display existing media scan records
    st.subheader("Existing Media Scan Records")
    
    media_scans_df = get_all_media_scans(session)
    
    if not media_scans_df.empty:
        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Companies", len(media_scans_df))
        with col2:
            # Count companies with negative findings
            negative_keywords = ['job losses', 'redundancies', 'court', 'negative', 'poor', 'concern', 'issues']
            negative_count = sum(1 for topic in media_scans_df['TOPIC_OF_DISQUALIFICATION'] 
                               if any(keyword in str(topic).lower() for keyword in negative_keywords))
            st.metric("With Issues", negative_count)
        with col3:
            clean_count = len(media_scans_df[media_scans_df['TOPIC_OF_DISQUALIFICATION'].str.contains('Nothing negative', na=False)])
            st.metric("Clean Records", clean_count)
        with col4:
            no_media_count = len(media_scans_df[media_scans_df['TOPIC_OF_DISQUALIFICATION'].str.contains('No relevant media', na=False)])
            st.metric("No Media Found", no_media_count)
        
        # Search and filter
        col1, col2 = st.columns([2, 1])
        with col1:
            search_term = st.text_input("🔍 Search companies or topics", placeholder="Enter company name or keyword...")
        with col2:
            sort_option = st.selectbox("Sort by", ["Company Name", "Topic Length", "Negative First"])
        
        # Apply search filter
        filtered_df = media_scans_df.copy()
        if search_term:
            mask = (
                filtered_df['COMPANY_NAME'].str.contains(search_term, case=False, na=False) |
                filtered_df['TOPIC_OF_DISQUALIFICATION'].str.contains(search_term, case=False, na=False)
            )
            filtered_df = filtered_df[mask]
        
        # Apply sorting
        if sort_option == "Company Name":
            filtered_df = filtered_df.sort_values('COMPANY_NAME')
        elif sort_option == "Topic Length":
            filtered_df['topic_length'] = filtered_df['TOPIC_OF_DISQUALIFICATION'].str.len()
            filtered_df = filtered_df.sort_values('topic_length', ascending=False)
            filtered_df = filtered_df.drop('topic_length', axis=1)
        elif sort_option == "Negative First":
            # Put negative findings first
            filtered_df['has_issues'] = ~filtered_df['TOPIC_OF_DISQUALIFICATION'].str.contains('Nothing negative|No relevant media', na=False)
            filtered_df = filtered_df.sort_values(['has_issues', 'COMPANY_NAME'], ascending=[False, True])
            filtered_df = filtered_df.drop('has_issues', axis=1)
        
        st.info(f"Showing {len(filtered_df)} of {len(media_scans_df)} records")
        
        # Display media scan records
        for idx, row in filtered_df.iterrows():
            # Determine status color based on content
            topic = str(row['TOPIC_OF_DISQUALIFICATION']).lower()
            if 'nothing negative' in topic:
                status_emoji = "🟢"
                status_text = "Clean"
            elif 'no relevant media' in topic:
                status_emoji = "⚪"
                status_text = "No Media"
            else:
                status_emoji = "🔴"
                status_text = "Issues Found"
            
            company_display = f"{status_emoji} {row['COMPANY_NAME']} - {status_text}"
            
            with st.expander(company_display, expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Company:** `{row['COMPANY_NAME']}`")
                    st.markdown("**Media Scan Topic:**")
                    st.write(row['TOPIC_OF_DISQUALIFICATION'])
                
                with col2:
                    st.markdown("**Actions:**")
                    
                    # Edit button
                    if st.button(f"✏️ Edit", key=f"edit_{idx}"):
                        st.session_state.edit_mode = True
                        st.session_state.selected_media_scan = row.to_dict()
                        st.session_state.show_add_form = False
                        st.session_state.show_upload = False
                        st.rerun()
                    
                    # Delete button with confirmation
                    delete_key = f"delete_pending_{idx}"
                    if not st.session_state.get(delete_key, False):
                        if st.button(f"🗑️ Delete", key=f"delete_{idx}", type="secondary"):
                            st.session_state[delete_key] = True
                            st.rerun()
                    else:
                        st.warning("⚠️ Confirm deletion:")
                        col_del1, col_del2 = st.columns(2)
                        with col_del1:
                            if st.button(f"✅ Yes", key=f"confirm_delete_{idx}", type="primary"):
                                if delete_media_scan(session, row['COMPANY_NAME']):
                                    st.success("✅ Record deleted!")
                                    st.session_state[delete_key] = False
                                    time.sleep(1)
                                    st.rerun()
                        with col_del2:
                            if st.button(f"❌ No", key=f"cancel_delete_{idx}", type="secondary"):
                                st.session_state[delete_key] = False
                                st.rerun()
    
    else:
        st.info("No media scan records found. Add your first record using the 'Add New' button above.")

if __name__ == "__main__":
    main() 