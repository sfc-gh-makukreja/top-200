-- ================================================================
-- DOCUMENT PROCESSING PIPELINE
-- Processes uploaded PDFs through parsing, chunking, and indexing
-- Called from Streamlit app for on-demand processing
-- ================================================================

-- Context is already set by Streamlit app deployment
-- Running in: top_200_db.top_200_schema with top_200_wh warehouse

-- ================================================================
-- STEP 1: PARSE NEW DOCUMENTS
-- Extract content from PDFs using Cortex PARSE_DOCUMENT
-- ================================================================

-- Create or replace the parsed documents table with new files
CREATE OR REPLACE TABLE cortex_parsed_docs AS
SELECT 
    relative_path,
    build_scoped_file_url(@top_200_db.top_200_schema.stage, relative_path) AS file_url,
    
    -- Use AI to extract company name from filename
    ai_complete('snowflake-llama-3.3-70b',
        concat('extract ONLY company name from the filename, do not return anything else, just the name or empty string: ', relative_path))::string as company_name,
    
    -- Use AI to extract report year from filename
    ai_complete('snowflake-llama-3.3-70b',
        concat('extract ONLY annual report year from the filename, do not return anything else, just the year of form YYYY or empty string: ', relative_path))::integer as year,

    -- Extract text content using native Snowflake OCR parsing
    SNOWFLAKE.CORTEX.PARSE_DOCUMENT(
        '@top_200_db.top_200_schema.stage', 
        relative_path
    ) AS parsed_content_ocr,
    
    -- Add processing metadata
    CURRENT_TIMESTAMP() AS processed_at

FROM directory(@top_200_db.top_200_schema.stage)
WHERE UPPER(relative_path) LIKE '%.PDF';

-- ================================================================
-- STEP 2: CREATE TEXT CHUNKS
-- Split parsed content into searchable chunks using Cortex
-- ================================================================

-- Create chunked text table using Cortex text splitting
CREATE OR REPLACE TABLE cortex_docs_chunks_table AS
SELECT 
    relative_path,
    file_url,
    company_name,
    year,
    processed_at,
    
    -- Extract text content from OCR parsing results
    parsed_content_ocr:content::string AS ocr_content,
    
    -- Chunk metadata from recursive character splitting
    f.value::string AS chunk_value_ocr,
    f.index AS chunk_index_ocr,
    
    -- Create final searchable chunks with file context
    CONCAT(relative_path, ': ', f.value::string) AS final_chunk_ocr,
    
    'English' AS language,
    
    -- Add chunk metadata
    CURRENT_TIMESTAMP() AS chunked_at
    
FROM cortex_parsed_docs,
     -- Use Cortex recursive character text splitter
     LATERAL FLATTEN(
         input => SNOWFLAKE.CORTEX.SPLIT_TEXT_RECURSIVE_CHARACTER(
             parsed_content_ocr:content::string,
             'none',          -- No specific format requirements
             2000,            -- Chunk size: 2000 characters
             300              -- Overlap: 300 characters for context
         )
     ) f
WHERE parsed_content_ocr:content::string IS NOT NULL
  AND LENGTH(parsed_content_ocr:content::string) > 0;

-- ================================================================
-- STEP 3: UPDATE CORTEX SEARCH SERVICE
-- Refresh the search index with new content
-- ================================================================

-- Drop and recreate the Cortex Search service to include new documents
DROP CORTEX SEARCH SERVICE IF EXISTS cortex_search_service_ocr;

CREATE CORTEX SEARCH SERVICE cortex_search_service_ocr
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
      AND LENGTH(final_chunk_ocr) > 10  -- Filter out very short chunks
);

-- ================================================================
-- STEP 4: PROCESSING SUMMARY
-- Return summary statistics about the processing results
-- ================================================================

SELECT 
    'Processing Complete' AS status,
    COUNT(DISTINCT relative_path) AS total_files_processed,
    COUNT(*) AS total_chunks_created,
    MIN(processed_at) AS processing_started,
    MAX(chunked_at) AS processing_completed,
    ROUND(AVG(LENGTH(ocr_content)), 0) AS avg_document_length,
    ROUND(AVG(LENGTH(chunk_value_ocr)), 0) AS avg_chunk_length
FROM cortex_docs_chunks_table;

-- ================================================================
-- OPTIONAL: PROCESSING VALIDATION
-- Uncomment to validate the processing results
-- ================================================================

-- Check for files that failed to process
-- SELECT 
--     'Failed Processing Check' AS check_type,
--     stage_files.relative_path,
--     CASE 
--         WHEN parsed.relative_path IS NULL THEN 'Failed to parse'
--         WHEN chunks.relative_path IS NULL THEN 'Failed to chunk'
--         ELSE 'Processed successfully'
--     END AS status
-- FROM (
--     SELECT relative_path FROM directory(@top_200_db.top_200_schema.stage)
--     WHERE UPPER(relative_path) LIKE '%.PDF'
-- ) stage_files
-- LEFT JOIN cortex_parsed_docs parsed ON stage_files.relative_path = parsed.relative_path
-- LEFT JOIN (
--     SELECT DISTINCT relative_path FROM cortex_docs_chunks_table
-- ) chunks ON stage_files.relative_path = chunks.relative_path;

-- Test search functionality
-- SELECT 
--     'Search Test' AS test_type,
--     SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
--         'cortex_search_service_ocr',
--         'revenue growth financial performance'
--     ) AS search_results; 