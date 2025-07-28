-- ================================================================
-- CORTEX RAG SETUP - COMPLETE INFRASTRUCTURE & FUNCTIONALITY
-- Sets up database infrastructure and cortex-based document processing
-- using native Snowflake Cortex functions
-- ================================================================

-- ================================================================
-- SECTION 1: INITIAL INFRASTRUCTURE SETUP
-- Create roles, warehouses, databases, and core tables
-- ================================================================

-- Start with ACCOUNTADMIN privileges for setup
USE ROLE ACCOUNTADMIN;

-- Create a new role for the top 200 project
CREATE ROLE IF NOT EXISTS top_200_role;

-- Assign the role to your user (change 'mkukreja' to your username)
GRANT ROLE top_200_role TO USER mkukreja;

-- Grant all necessary privileges to the role while in ACCOUNTADMIN
GRANT CREATE WAREHOUSE ON ACCOUNT TO ROLE top_200_role;
GRANT CREATE DATABASE ON ACCOUNT TO ROLE top_200_role;

-- Now switch to the project role
USE ROLE top_200_role;

-- Create a compute warehouse for the project
CREATE WAREHOUSE IF NOT EXISTS top_200_wh
    WITH WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE;

-- Create project database and schema
CREATE DATABASE IF NOT EXISTS top_200_db;
CREATE SCHEMA IF NOT EXISTS top_200_db.top_200_schema;

-- Set context for remaining operations
USE ROLE top_200_role;
USE WAREHOUSE top_200_wh;
USE DATABASE top_200_db;
USE SCHEMA top_200_schema;

-- ================================================================
-- SECTION 2: CORE APPLICATION TABLES
-- Tables for criteria management, results, and media scanning
-- ================================================================

-- Table for storing evaluation criteria and prompts
CREATE OR ALTER TABLE input_criteria (
    id STRING,
    question STRING,
    cluster ARRAY,
    role STRING,
    instructions STRING,
    output STRING, 
    criteria_prompt STRING,
    weight FLOAT,
    version STRING,
    active BOOLEAN
);

-- Table for storing analysis results and outputs
CREATE OR ALTER TABLE cortex_output (
    criteria_id STRING,
    criteria_version STRING,
    criteria_prompt STRING,
    question STRING,
    run_id STRING,
    result STRING,
    justification STRING,
    evidence STRING,
    data_source STRING,
    output VARIANT
);

-- Table for media scanning and disqualification tracking
CREATE OR ALTER TABLE media_scan (
    company_name STRING,
    topic_of_disqualification STRING
);

-- ================================================================
-- SECTION 3: FILE STORAGE STAGE
-- Stage for uploading and processing PDF documents
-- ================================================================

-- Create encrypted stage for document storage
CREATE OR REPLACE STAGE stage
    DIRECTORY = (ENABLE = TRUE, AUTO_REFRESH = TRUE)
    ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');

-- ================================================================
-- SECTION 4: CORTEX-BASED DOCUMENT PARSING
-- using native Snowflake functions
-- ================================================================


-- Parse PDF documents using Cortex PARSE_DOCUMENT (OCR mode)
-- Note: This will be populated by process_documents.sql when files are uploaded
CREATE TABLE IF NOT EXISTS cortex_parsed_docs (
    relative_path STRING,
    file_url STRING,
    company_name STRING,
    year INTEGER,
    parsed_content_ocr VARIANT,
    processed_at TIMESTAMP
);


-- ================================================================
-- SECTION 5: CORTEX-BASED TEXT CHUNKING
-- using native Snowflake functions
-- ================================================================

-- Create chunked text table using Cortex text splitting  
-- Note: This will be populated by process_documents.sql when files are processed
CREATE TABLE IF NOT EXISTS cortex_docs_chunks_table (
    relative_path STRING,
    file_url STRING,
    company_name STRING,
    year INTEGER,
    processed_at TIMESTAMP,
    ocr_content STRING,
    chunk_value_ocr STRING,
    chunk_index_ocr INTEGER,
    final_chunk_ocr STRING,
    language STRING,
    chunked_at TIMESTAMP
);

-- ================================================================
-- SECTION 6: CORTEX SEARCH SERVICE
-- Create searchable index for RAG functionality
-- ================================================================

-- Create Cortex Search service for semantic search
-- Note: Will be recreated with actual data by process_documents.sql
CREATE CORTEX SEARCH SERVICE IF NOT EXISTS cortex_search_service_ocr
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
);

-- ================================================================
-- SECTION 7: GIT INTEGRATION & STREAMLIT APP
-- Create Git repository and deploy Streamlit app from Git
-- ================================================================
-- Instructions for manual setup for Secret and API Integration: https://docs.snowflake.com/en/developer-guide/git/git-setting-up#configure-for-authenticating-with-a-token
-- 1. Create a Secret for your Git Personal Access Token (PAT).
--    Example (run as ACCOUNTADMIN or role with CREATE SECRET privilege):
--    CREATE OR REPLACE SECRET sfc_gh_makukreja_pat
--      TYPE = PASSWORD
--      USERNAME = 'sfc-gh-makukreja'  -- Replace with your Git username
--      PASSWORD = 'github_pat_xxx';  -- Replace with your Git PAT https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token

-- 2. Create an API Integration for your Git provider.
--    Example (run as ACCOUNTADMIN or role with CREATE INTEGRATION privilege):
--    CREATE OR REPLACE API INTEGRATION sfc_gh_makukreja_integration
--      API_PROVIDER = git_https_api
--      API_ALLOWED_PREFIXES = ('https://github.com/sfc-gh-makukreja') -- Adjust for your Git provider & org/user
--      ALLOWED_AUTHENTICATION_SECRETS = ('sfc_gh_makukreja_pat') -- Must match the secret name from step 1
--      ENABLED = TRUE;

-- 3. Grant USAGE on the API Integration and READ on the Secret to top_200_role.
--    Example (run as ACCOUNTADMIN or role that owns the integration/secret):
--    GRANT USAGE ON INTEGRATION sfc_gh_makukreja_integration TO ROLE top_200_role;
--    GRANT READ ON SECRET sfc_gh_makukreja_pat TO ROLE top_200_role;

-- Create Git repository (assumes SFC_GH_MAKUKREJA_INTEGRATION exists, if not create it first see instructions above)
CREATE OR REPLACE GIT REPOSITORY top_200_repo
  API_INTEGRATION = SFC_GH_MAKUKREJA_INTEGRATION
  ORIGIN = 'https://github.com/sfc-gh-makukreja/top-200.git';

-- Verify repository connection (function not available in this version)
-- SELECT SYSTEM$GIT_REPOSITORY_VALIDATE('top_200_repo') AS git_validation_status;

-- Create Streamlit app from Git repository
CREATE OR REPLACE STREAMLIT  IDENTIFIER('"TOP_200_DB"."TOP_200_SCHEMA"."top_200_app"') 
  FROM '@"TOP_200_DB"."TOP_200_SCHEMA"."TOP_200_REPO"/branches/"main"/' 
  MAIN_FILE = 'streamlit_app.py'
  QUERY_WAREHOUSE = top_200_wh
  TITLE = 'Top 200 Companies - Document Processing';

-- Show created objects
SHOW GIT REPOSITORIES LIKE 'top_200_repo';
SHOW STREAMLITS LIKE 'top_200_app';

-- Display success message
SELECT 'Git integration and Streamlit app created successfully!' as status,
       'Navigate to Snowsight → Streamlit to access your app' as next_step;

-- once new code is pushed to the repo, run the following command to pull the latest changes
-- ALTER STREAMLIT "TOP_200_DB"."TOP_200_SCHEMA"."top_200_app" COMMIT;
-- ALTER STREAMLIT "TOP_200_DB"."TOP_200_SCHEMA"."top_200_app" PULL;

-- ================================================================
-- SECTION 8: TESTING AND VALIDATION
-- Uncomment to test search functionality
-- ================================================================

-- Test semantic search functionality (uncomment to run)
-- SELECT 'OCR Search Test' AS test_type,
--        SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
--            'cortex_search_service_ocr',
--            'revenue growth financial performance'
--        ) AS search_results;

-- ================================================================
-- SECTION 9: CLEANUP COMMANDS
-- Uncomment to remove cortex-based components if needed
-- ================================================================

-- Remove cortex-based tables and services (uncomment to run)
-- DROP TABLE cortex_parsed_docs;
-- DROP TABLE cortex_docs_chunks_table;
-- DROP CORTEX SEARCH SERVICE cortex_search_service_ocr; 