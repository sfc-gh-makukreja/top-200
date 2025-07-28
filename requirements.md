# Top 200 Companies Analysis - Requirements

## Overview
A Streamlit application for uploading annual reports and making them searchable using Snowflake Cortex AI.

## Core Functionality

### Page 1: Upload & Process Reports
**Purpose**: Upload PDF annual reports and make them AI-ready for analysis

#### Key Features
- **File Upload**: Allow users to upload PDF files (annual reports)
- **File Management**: 
  - Show currently uploaded files in the stage
  - Display file details (name, size, upload date)
  - Option to delete files if needed

- **Processing Pipeline**:
  - Parse PDFs using Cortex PARSE_DOCUMENT 
  - Extract company name and year from filename using AI
  - Split text into searchable chunks
  - Update Cortex Search Service

- **Progress Tracking**:
  - Show processing status (uploading, parsing, chunking, indexing)
  - Display success/error messages
  - Show processing time and statistics

#### User Interface
- Simple drag-and-drop file upload area
- File list with status indicators
- "Process All" and "Process Selected" buttons
- Progress bars and status messages
- Basic file validation (PDF only, size limits)

## Technical Requirements

### Infrastructure (Already exists in cortex_setup.sql)
- ✅ Database and schema: `top_200_db.top_200_schema`
- ✅ File stage with directory enabled
- ✅ Cortex Search Service: `cortex_search_service_ocr`
- ✅ Tables: `cortex_parsed_docs`, `cortex_docs_chunks_table`

### New Components Needed
- **Streamlit App**: `streamlit_app.py`
- **Processing Functions**: Wrap existing SQL logic in Python functions
- **Error Handling**: Graceful handling of parsing/processing failures
- **File Validation**: Check file types and sizes before upload

## Success Criteria
- Users can upload PDF files successfully
- Files are automatically parsed and made searchable
- Users can see processing status and results
- Cortex Search Service is updated with new content
- Simple, intuitive interface that "just works"

## Future Enhancements (Not in initial scope)
- Automated processing via Snowflake tasks
- Batch processing optimizations
- Advanced file management features
- Integration with additional analysis pages
- User authentication and access controls

## Technical Constraints
- Use only Snowflake Anaconda channel packages
- Leverage existing Cortex infrastructure
- Keep initial version simple and focused
- Handle errors gracefully without crashing 