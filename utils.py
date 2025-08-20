"""
Document Processing Pipeline for Top 200 Companies
Handles PDF parsing, chunking, and search indexing using Snowflake Cortex AI
"""

import streamlit as st
from snowflake.snowpark import Session
from typing import Dict, Any, Tuple
import time


def process_all_documents(session: Session) -> Dict[str, Any]:
    """
    Complete document processing pipeline using Snowpark
    Returns: processing results and statistics
    """
    results = {
        'success': False,
        'steps_completed': 0,
        'total_steps': 3,
        'messages': [],
        'stats': {},
        'error': None
    }
    
    try:
        # Step 0: Refresh stage
        st.info("🔄 Step 0: Refreshing stage...")
        refresh_sql = """
        ALTER STAGE stage REFRESH;
        """
        session.sql(refresh_sql).collect()
        
        # Step 1: Parse PDF documents (incremental approach)
        st.info("🔄 Step 1: Parsing new PDF documents with Cortex...")
        
        # First ensure the table exists (idempotent)
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS cortex_parsed_docs (
            relative_path STRING,
            file_url STRING,
            company_name STRING,
            year INTEGER,
            parsed_content_ocr VARIANT,
            file_uploaded_at TIMESTAMP,
            processed_at TIMESTAMP
        )
        """
        session.sql(create_table_sql).collect()
        
        # Insert only new files that haven't been processed yet
        parse_sql = """
        INSERT INTO cortex_parsed_docs
        SELECT 
            d.relative_path,
            build_scoped_file_url(@stage, d.relative_path) AS file_url,
            
            -- Use AI to extract company name from filename
            ai_complete('snowflake-llama-3.3-70b',
                concat('extract ONLY company name from the filename, do not return anything else, just the name or empty string: ', d.relative_path))::string as company_name,
            
            -- Use AI to extract report year from filename
            ai_complete('snowflake-llama-3.3-70b',
                concat('extract ONLY annual report year from the filename, do not return anything else, just the year of form YYYY or empty string: ', d.relative_path))::integer as year,

            -- Extract text content using Cortex OCR
            SNOWFLAKE.CORTEX.PARSE_DOCUMENT('@stage', d.relative_path) AS parsed_content_ocr,
            
            -- File upload timestamp from stage metadata
            d.last_modified AS file_uploaded_at,
            
            CURRENT_TIMESTAMP() AS processed_at

        FROM directory(@stage) d
        WHERE UPPER(d.relative_path) LIKE '%.PDF'
          AND NOT EXISTS (
              SELECT 1 FROM cortex_parsed_docs p 
              WHERE p.relative_path = d.relative_path
          )
        """
        
        session.sql(parse_sql).collect()
        
        # Get parsing stats (for new files only)
        stats_df = session.sql("""
            SELECT 
                COUNT(*) as new_files_parsed,
                COUNT(CASE WHEN parsed_content_ocr IS NOT NULL THEN 1 END) as successful_parses,
                (SELECT COUNT(*) FROM cortex_parsed_docs) as total_files_in_system
            FROM cortex_parsed_docs
            WHERE processed_at >= CURRENT_TIMESTAMP() - INTERVAL '10 minutes'
        """).to_pandas()
        
        new_files_parsed = int(stats_df.iloc[0]['NEW_FILES_PARSED'])
        successful_parses = int(stats_df.iloc[0]['SUCCESSFUL_PARSES'])
        total_files = int(stats_df.iloc[0]['TOTAL_FILES_IN_SYSTEM'])
        
        results['messages'].append(f"Step 1: Parsed {new_files_parsed} new files ({successful_parses} successful), {total_files} total files in system")
        results['stats']['new_files_parsed'] = new_files_parsed
        results['stats']['total_files'] = total_files
        results['steps_completed'] = 1
        
        # Step 2: Create text chunks (incremental approach)
        st.info("🔄 Step 2: Creating searchable text chunks for new documents...")
        
        # First ensure the chunks table exists (idempotent)
        create_chunks_table_sql = """
        CREATE TABLE IF NOT EXISTS cortex_docs_chunks_table (
            relative_path STRING,
            file_url STRING,
            company_name STRING,
            year INTEGER,
            file_uploaded_at TIMESTAMP,
            processed_at TIMESTAMP,
            ocr_content STRING,
            chunk_value_ocr STRING,
            chunk_index_ocr INTEGER,
            final_chunk_ocr STRING,
            language STRING,
            chunked_at TIMESTAMP
        )
        """
        session.sql(create_chunks_table_sql).collect()
        
        # Insert chunks only for newly parsed documents
        chunk_sql = """
        INSERT INTO cortex_docs_chunks_table
        SELECT 
            p.relative_path,
            p.file_url,
            p.company_name,
            p.year,
            p.file_uploaded_at,
            p.processed_at,
            
            -- Extract text content
            p.parsed_content_ocr:content::string AS ocr_content,
            
            -- Chunk metadata
            f.value::string AS chunk_value_ocr,
            f.index AS chunk_index_ocr,
            
            -- Final searchable chunks
            CONCAT(p.relative_path, ': ', f.value::string) AS final_chunk_ocr,
            
            'English' AS language,
            CURRENT_TIMESTAMP() AS chunked_at
            
        FROM cortex_parsed_docs p,
             LATERAL FLATTEN(
                 input => SNOWFLAKE.CORTEX.SPLIT_TEXT_RECURSIVE_CHARACTER(
                     p.parsed_content_ocr:content::string,
                     'none',
                     2000,
                     300
                 )
             ) f
        WHERE p.parsed_content_ocr:content::string IS NOT NULL
          AND LENGTH(p.parsed_content_ocr:content::string) > 0
          AND NOT EXISTS (
              SELECT 1 FROM cortex_docs_chunks_table c 
              WHERE c.relative_path = p.relative_path
          )
        """
        
        session.sql(chunk_sql).collect()
        
        # Get chunking stats (for new chunks only)
        chunk_stats_df = session.sql("""
            SELECT 
                COUNT(DISTINCT relative_path) as new_files_chunked,
                COUNT(*) as new_chunks_created,
                (SELECT COUNT(DISTINCT relative_path) FROM cortex_docs_chunks_table) as total_files_chunked,
                (SELECT COUNT(*) FROM cortex_docs_chunks_table) as total_chunks_in_system
            FROM cortex_docs_chunks_table
            WHERE chunked_at >= CURRENT_TIMESTAMP() - INTERVAL '10 minutes'
        """).to_pandas()
        
        new_files_chunked = int(chunk_stats_df.iloc[0]['NEW_FILES_CHUNKED'])
        new_chunks_created = int(chunk_stats_df.iloc[0]['NEW_CHUNKS_CREATED'])
        total_files_chunked = int(chunk_stats_df.iloc[0]['TOTAL_FILES_CHUNKED'])
        total_chunks_in_system = int(chunk_stats_df.iloc[0]['TOTAL_CHUNKS_IN_SYSTEM'])
        
        results['messages'].append(f"Step 2: Created {new_chunks_created} new chunks from {new_files_chunked} files ({total_chunks_in_system} total chunks for {total_files_chunked} files)")
        results['stats']['new_files_chunked'] = new_files_chunked
        results['stats']['new_chunks_created'] = new_chunks_created
        results['stats']['total_chunks_in_system'] = total_chunks_in_system
        results['steps_completed'] = 2
        
        # Step 3: Update search service (incremental approach)
        st.info("🔄 Step 3: Refreshing Cortex Search Service...")
        
        # Check if search service exists
        try:
            session.sql("DESCRIBE CORTEX SEARCH SERVICE cortex_search_service_ocr").collect()
            search_exists = True
        except:
            search_exists = False
        
        if not search_exists:
            # Create search service if it doesn't exist
            search_sql = """
            CREATE CORTEX SEARCH SERVICE cortex_search_service_ocr
                ON final_chunk_ocr
                ATTRIBUTES language, COMPANY_NAME, year
                WAREHOUSE = top_200_wh
                TARGET_LAG = '1 hour'
                AS (
                SELECT
                    final_chunk_ocr,
                    relative_path,
                    COMPANY_NAME,
                    year,
                    file_url,
                    language
                FROM cortex_docs_chunks_table
                WHERE final_chunk_ocr IS NOT NULL
                  AND LENGTH(final_chunk_ocr) > 10
            )
            """
            session.sql(search_sql).collect()
        else:
            # Refresh existing search service to include new data
            # The search service will automatically pick up new data from the underlying table
            st.info("Search service already exists and will automatically include new chunks")
        
        # Get final stats
        search_stats_df = session.sql("""
            SELECT COUNT(*) as searchable_chunks
            FROM cortex_docs_chunks_table
            WHERE final_chunk_ocr IS NOT NULL
              AND LENGTH(final_chunk_ocr) > 10
        """).to_pandas()
        
        searchable_chunks = int(search_stats_df.iloc[0]['SEARCHABLE_CHUNKS'])
        
        results['messages'].append(f"Step 3: Search service updated with {searchable_chunks} searchable chunks")
        results['stats']['searchable_chunks'] = searchable_chunks
        results['steps_completed'] = 3
        results['success'] = True
        
        return results
        
    except Exception as e:
        results['error'] = str(e)
        return results


def get_processing_summary(session: Session) -> Dict[str, Any]:
    """Get summary statistics of processed documents"""
    try:
        summary_df = session.sql("""
            SELECT 
                COUNT(DISTINCT relative_path) AS total_files_processed,
                COUNT(*) AS total_chunks_created,
                MIN(file_uploaded_at) AS earliest_upload,
                MAX(file_uploaded_at) AS latest_upload,
                MIN(processed_at) AS processing_started,
                MAX(chunked_at) AS processing_completed,
                ROUND(AVG(LENGTH(ocr_content)), 0) AS avg_document_length,
                ROUND(AVG(LENGTH(chunk_value_ocr)), 0) AS avg_chunk_length
            FROM cortex_docs_chunks_table
        """).to_pandas()
        
        if not summary_df.empty:
            return summary_df.iloc[0].to_dict()
        return {}
        
    except Exception as e:
        st.error(f"Failed to get processing summary: {e}")
        return {} 