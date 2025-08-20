import streamlit as st
import pandas as pd
from snowflake.snowpark import Session
import time
import os
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

def upload_file_to_stage(session: Session, uploaded_file, stage_name: str) -> bool:
    """Upload file to Snowflake stage."""
    try:
        # Save uploaded file temporarily
        temp_file_path = f"/tmp/{uploaded_file.name}"
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Upload to stage
        session.file.put(
            temp_file_path,
            f"@{stage_name}",
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
            SELECT relative_path, company_name, year, 
                   COUNT(*) as chunk_count
            FROM cortex_docs_chunks_table 
            GROUP BY relative_path, company_name, year
            ORDER BY relative_path
        """).collect()
        
        if result:
            df = pd.DataFrame([row.as_dict() for row in result])
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error getting processed files: {e}")
        return pd.DataFrame()

def process_all_documents(session: Session) -> None:
    """Process all PDF documents in the stage using the Python processing pipeline."""
    
    # Check if there are files to process
    stage_files = get_stage_files(session, STAGE_NAME)
    pdf_files = stage_files[stage_files['name'].str.upper().str.endswith('.PDF')] if not stage_files.empty else pd.DataFrame()
    
    if pdf_files.empty:
        st.warning("No PDF files found in stage to process")
        return
    
    st.info(f"📄 Found {len(pdf_files)} PDF files to process")
    
    # Process documents using the Python processor
    with st.spinner("Processing documents..."):
        results = process_docs(session)
        
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
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                success_count = 0
                total_files = len(uploaded_files)
                
                for i, file in enumerate(uploaded_files):
                    status_text.text(f"Uploading {file.name}...")
                    
                    if upload_file_to_stage(session, file, STAGE_NAME):
                        success_count += 1
                        st.success(f"✅ {file.name} uploaded successfully")
                    else:
                        st.error(f"❌ Failed to upload {file.name}")
                    
                    progress_bar.progress((i + 1) / total_files)
                
                status_text.text(f"Upload complete: {success_count}/{total_files} files successful")
                
                if success_count > 0:
                    st.balloons()
    
    with tab2:
        st.header("Files in Stage")
        
    
        if st.button("Refresh Stage", type="secondary"):
            st.rerun()
        
        st.markdown("---")
        
        if st.button("Process All Files", type="primary"):
            process_all_documents(session)
        
        stage_files = get_stage_files(session, STAGE_NAME)
        
        if not stage_files.empty:
            # Filter for PDF files only
            pdf_files = stage_files[stage_files['name'].str.upper().str.endswith('.PDF')]
            
            if not pdf_files.empty:
                st.dataframe(
                    pdf_files[['name', 'size', 'last_modified']].rename(columns={
                        'name': 'File Name',
                        'size': 'Size (bytes)',
                        'last_modified': 'Upload Date'
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
                    'CHUNK_COUNT': 'Text Chunks'
                }),
                use_container_width=True
            )
            
            st.success(f"📊 {len(processed_files)} documents processed and searchable")
        else:
            st.info("No processed documents found. Upload and process some files first!")

if __name__ == "__main__":
    main() 