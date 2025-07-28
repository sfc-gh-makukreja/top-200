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
        # Step 1: Parse PDF documents
        st.info("🔄 Step 1: Parsing PDF documents with Cortex...")
        
        parse_sql = """
        CREATE OR REPLACE TABLE cortex_parsed_docs AS
        SELECT 
            relative_path,
            build_scoped_file_url(@stage, relative_path) AS file_url,
            
            -- Use AI to extract company name from filename
            SNOWFLAKE.CORTEX.COMPLETE('llama3-8b',
                'Extract only the company name from this filename: ' || relative_path || '. Return just the company name.'
            ) as company_name,
            
            -- Use AI to extract report year from filename  
            TRY_CAST(
                SNOWFLAKE.CORTEX.COMPLETE('llama3-8b',
                    'Extract only the year from this filename: ' || relative_path || '. Return just the 4-digit year.'
                ) AS INTEGER
            ) as year,

            -- Extract text content using Cortex OCR
            SNOWFLAKE.CORTEX.PARSE_DOCUMENT('@stage', relative_path) AS parsed_content_ocr,
            
            CURRENT_TIMESTAMP() AS processed_at

        FROM directory(@stage)
        WHERE UPPER(relative_path) LIKE '%.PDF'
        """
        
        session.sql(parse_sql).collect()
        
        # Get parsing stats
        stats_df = session.sql("""
            SELECT 
                COUNT(*) as files_parsed,
                COUNT(CASE WHEN parsed_content_ocr IS NOT NULL THEN 1 END) as successful_parses
            FROM cortex_parsed_docs
        """).to_pandas()
        
        files_parsed = int(stats_df.iloc[0]['FILES_PARSED'])
        successful_parses = int(stats_df.iloc[0]['SUCCESSFUL_PARSES'])
        
        results['messages'].append(f"Step 1: Parsed {files_parsed} files ({successful_parses} successful)")
        results['stats']['files_parsed'] = files_parsed
        results['steps_completed'] = 1
        
        # Step 2: Create text chunks
        st.info("🔄 Step 2: Creating searchable text chunks...")
        
        chunk_sql = """
        CREATE OR REPLACE TABLE cortex_docs_chunks_table AS
        SELECT 
            relative_path,
            file_url,
            company_name,
            year,
            processed_at,
            
            -- Extract text content
            parsed_content_ocr:content::string AS ocr_content,
            
            -- Chunk metadata
            f.value::string AS chunk_value_ocr,
            f.index AS chunk_index_ocr,
            
            -- Final searchable chunks
            CONCAT(relative_path, ': ', f.value::string) AS final_chunk_ocr,
            
            'English' AS language,
            CURRENT_TIMESTAMP() AS chunked_at
            
        FROM cortex_parsed_docs,
             LATERAL FLATTEN(
                 input => SNOWFLAKE.CORTEX.SPLIT_TEXT_RECURSIVE_CHARACTER(
                     parsed_content_ocr:content::string,
                     'none',
                     2000,
                     300
                 )
             ) f
        WHERE parsed_content_ocr:content::string IS NOT NULL
          AND LENGTH(parsed_content_ocr:content::string) > 0
        """
        
        session.sql(chunk_sql).collect()
        
        # Get chunking stats
        chunk_stats_df = session.sql("""
            SELECT 
                COUNT(DISTINCT relative_path) as files_chunked,
                COUNT(*) as total_chunks
            FROM cortex_docs_chunks_table
        """).to_pandas()
        
        files_chunked = int(chunk_stats_df.iloc[0]['FILES_CHUNKED'])
        total_chunks = int(chunk_stats_df.iloc[0]['TOTAL_CHUNKS'])
        
        results['messages'].append(f"Step 2: Created {total_chunks} chunks from {files_chunked} files")
        results['stats']['files_chunked'] = files_chunked
        results['stats']['total_chunks'] = total_chunks
        results['steps_completed'] = 2
        
        # Step 3: Update search service
        st.info("🔄 Step 3: Updating Cortex Search Service...")
        
        # Create or replace search service
        search_sql = """
        CREATE OR REPLACE CORTEX SEARCH SERVICE cortex_search_service_ocr
            ON final_chunk_ocr
            ATTRIBUTES language, company_name, year
            WAREHOUSE = top_200_wh
            TARGET_LAG = '1 hour'
            AS (
            SELECT
                final_chunk_ocr,
                relative_path,
                company_name,
                year,
                file_url,
                language
            FROM cortex_docs_chunks_table
            WHERE final_chunk_ocr IS NOT NULL
              AND LENGTH(final_chunk_ocr) > 10
        )
        """
        
        session.sql(search_sql).collect()
        
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