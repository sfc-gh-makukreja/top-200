import streamlit as st
import pandas as pd
from snowflake.snowpark import Session
import time
import os
import datetime
from typing import List, Dict, Any
from utils import process_all_documents as process_docs, get_processing_summary

# Page configuration
st.set_page_config(
    page_title="Document Processing - Deloitte Top 200 Awards",
    page_icon="📄",
    layout="wide"
)

# Configuration
STAGE_NAME = "stage"

def get_snowflake_session() -> Session:
    """Initialize Snowflake session using Streamlit connection."""
    try:
        return st.connection("snowflake").session()
    except Exception as e:
        st.error(f"Failed to connect to Snowflake: {e}")
        st.stop()

def generate_batch_id() -> str:
    """Generate a unique batch ID based on current timestamp"""
    return f"batch_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

def upload_file_to_stage(session: Session, uploaded_file, stage_name: str, batch_id: str) -> bool:
    """Upload file to Snowflake stage with batch ID path."""
    try:
        # Save uploaded file temporarily
        temp_file_path = f"/tmp/{uploaded_file.name}"
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Upload to stage with batch path: @stage/batch_id/filename
        session.file.put(
            temp_file_path,
            f"@{stage_name}/{batch_id}",
            auto_compress=False,
            overwrite=True
        )
        
        # Clean up temp file
        os.remove(temp_file_path)
        return True
    except Exception as e:
        st.error(f"File upload error: {e}")
        return False

def get_stage_files(session: Session, stage_name: str) -> pd.DataFrame:
    """Get list of files in the stage."""
    try:
        result = session.sql(f"LIST @{stage_name}").collect()
        if result:
            df = pd.DataFrame([row.as_dict() for row in result])
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error listing stage files: {e}")
        return pd.DataFrame()

def get_processed_files(session: Session) -> pd.DataFrame:
    """Get list of already processed files."""
    try:
        result = session.sql("""
            SELECT relative_path, company_name, year, batch_id,
                   COUNT(*) as chunk_count,
                   file_uploaded_at,
                   file_uploaded_at_nz
            FROM cortex_docs_chunks_table 
            GROUP BY relative_path, company_name, year, batch_id, file_uploaded_at, file_uploaded_at_nz
            ORDER BY relative_path
        """).collect()
        
        if result:
            df = pd.DataFrame([row.as_dict() for row in result])
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error getting processed files: {e}")
        return pd.DataFrame()

def get_available_batches(session: Session) -> pd.DataFrame:
    """Get list of available batch directories from stage"""
    try:
        result = session.sql(f"LIST @{STAGE_NAME}").collect()
        if result:
            df = pd.DataFrame([row.as_dict() for row in result])
            # Filter for directories (batch folders)
            if 'name' in df.columns:
                batch_dirs = df[df['name'].str.contains('batch_') & df['name'].str.endswith('/')]
                batch_dirs['batch_id'] = batch_dirs['name'].str.replace('/', '')
                return batch_dirs
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error getting batches: {e}")
        return pd.DataFrame()

def process_documents_by_batch(session: Session, batch_id: str = None) -> None:
    """Process PDF documents for a specific batch or all documents."""
    
    # Check if there are files to process
    stage_files = get_stage_files(session, STAGE_NAME)
    
    if batch_id:
        # Filter files for specific batch
        pdf_files = stage_files[
            stage_files['name'].str.upper().str.endswith('.PDF') & 
            stage_files['name'].str.startswith(f"{batch_id}/")
        ] if not stage_files.empty else pd.DataFrame()
        process_label = f"batch {batch_id}"
    else:
        # Process all PDF files
        pdf_files = stage_files[stage_files['name'].str.upper().str.endswith('.PDF')] if not stage_files.empty else pd.DataFrame()
        process_label = "all files"
    
    if pdf_files.empty:
        st.warning(f"No PDF files found to process for {process_label}")
        return
    
    st.info(f"📄 Found {len(pdf_files)} PDF files to process for {process_label}")
    
    # Process documents using the Python processor
    with st.spinner(f"Processing {process_label}..."):
        results = process_docs(session, batch_id)
        
        if results['success']:
            st.success("✅ Processing completed successfully!")
            
            # Display progress messages
            for message in results['messages']:
                st.info(message)
            
            # Display summary metrics
            summary = get_processing_summary(session)
            if summary:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Files Processed", summary.get('TOTAL_FILES_PROCESSED', 0))
                with col2:
                    st.metric("Text Chunks Created", summary.get('TOTAL_CHUNKS_CREATED', 0))
                with col3:
                    st.metric("Avg Document Length", f"{summary.get('AVG_DOCUMENT_LENGTH', 0):,.0f} chars")
            
            st.balloons()
            
        else:
            st.error(f"❌ Processing failed: {results['error']}")
            st.info(f"Completed {results['steps_completed']}/{results['total_steps']} steps")
            
            # Show any partial progress
            for message in results['messages']:
                st.info(message)

def main():

    
    st.title("Document Upload & Processing")
    st.markdown("Upload annual reports and make them searchable with Snowflake Cortex AI")
    
    # Initialize session
    session = get_snowflake_session()
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Upload Files", "Stage Files", "Processed Files"])
    
    with tab1:
        st.header("Upload PDF Documents")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type=['pdf'],
            accept_multiple_files=True,
            help="Upload annual reports in PDF format"
        )
        
        if uploaded_files:
            st.subheader("Selected Files")
            for file in uploaded_files:
                st.write(f"📄 {file.name} ({file.size:,} bytes)")
            
            # Upload button
            if st.button("Upload to Snowflake Stage", type="primary"):
                # Generate batch ID for this upload session
                batch_id = generate_batch_id()
                st.info(f"🆔 **Batch ID:** `{batch_id}`")
                st.info(f"📁 **Upload Path:** `{STAGE_NAME}/{batch_id}/`")
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                success_count = 0
                total_files = len(uploaded_files)
                
                for i, file in enumerate(uploaded_files):
                    status_text.text(f"Uploading {file.name} to batch {batch_id}...")
                    
                    if upload_file_to_stage(session, file, STAGE_NAME, batch_id):
                        success_count += 1
                        st.success(f"✅ {file.name} uploaded successfully to batch {batch_id}")
                    else:
                        st.error(f"❌ Failed to upload {file.name}")
                    
                    progress_bar.progress((i + 1) / total_files)
                
                status_text.text(f"Upload complete: {success_count}/{total_files} files successful")
                
                if success_count > 0:
                    st.success(f"🎉 Upload completed! All files are in batch: **{batch_id}**")
                    st.balloons()
    
    with tab2:
        st.header("Files in Stage")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Refresh Stage", type="secondary"):
                st.rerun()
        
        st.markdown("---")
        
        # Batch selection for processing
        st.subheader("🎯 Processing Options")
        
        # Get available batches
        available_batches = get_available_batches(session)
        
        processing_mode = st.radio(
            "Choose processing mode:",
            ["📦 Process Specific Batch", "🌐 Process All Files"],
            horizontal=True
        )
        
        if processing_mode == "📦 Process Specific Batch":
            if not available_batches.empty:
                batch_options = available_batches['batch_id'].tolist()
                selected_batch = st.selectbox(
                    "Select batch to process:",
                    options=batch_options,
                    help="Choose a specific batch to process"
                )
                
                if st.button("Process Selected Batch", type="primary"):
                    process_documents_by_batch(session, selected_batch)
            else:
                st.warning("No batches found. Upload some files first!")
        else:
            if st.button("Process All Files", type="primary"):
                process_documents_by_batch(session)
        
        st.markdown("---")
        
        # Display stage files
        stage_files = get_stage_files(session, STAGE_NAME)
        
        if not stage_files.empty:
            # Filter for PDF files only
            pdf_files = stage_files[stage_files['name'].str.upper().str.endswith('.PDF')]
            
            if not pdf_files.empty:
                # Add batch information to the display
                pdf_files['batch_id'] = pdf_files['name'].apply(
                    lambda x: x.split('/')[0] if '/' in x else 'legacy_batch'
                )
                
                st.dataframe(
                    pdf_files[['name', 'batch_id', 'size', 'last_modified']].rename(columns={
                        'name': 'File Name',
                        'batch_id': 'Batch ID',
                        'size': 'Size (bytes)',
                        'last_modified': 'Upload Date'
                    }),
                    use_container_width=True
                )
                
                # Show batch summary
                if 'batch_id' in pdf_files.columns:
                    batch_summary = pdf_files.groupby('batch_id').size().reset_index(name='file_count')
                    st.subheader("📊 Batch Summary")
                    st.dataframe(
                        batch_summary.rename(columns={
                            'batch_id': 'Batch ID',
                            'file_count': 'File Count'
                        }),
                        use_container_width=True
                    )
            else:
                st.info("No PDF files found in stage")
        else:
            st.info("No files found in stage. Upload some files first!")
    
    with tab3:
        st.header("Processed Documents")
        
        if st.button("Refresh Processed", type="secondary"):
            st.rerun()
        
        processed_files = get_processed_files(session)
        
        if not processed_files.empty:
            st.dataframe(
                processed_files.rename(columns={
                    'RELATIVE_PATH': 'File Path',
                    'COMPANY_NAME': 'Company',
                    'YEAR': 'Year',
                    'CHUNK_COUNT': 'Text Chunks',
                    'BATCH_ID': 'Batch ID',
                    'FILE_UPLOADED_AT': 'Uploaded At (GMT)',
                    'FILE_UPLOADED_AT_NZ': 'Uploaded At (NZ)'
                }),
                use_container_width=True
            )
            
            st.success(f"📊 {len(processed_files)} documents processed and searchable")
        else:
            st.info("No processed documents found. Upload and process some files first!")

if __name__ == "__main__":
    main() 