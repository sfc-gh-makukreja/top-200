# Top 200 Companies - Document Upload & Processing

A Streamlit application for uploading annual reports and making them searchable using Snowflake Cortex AI.

## Architecture

**Separation of Concerns:**
- `streamlit_app.py` - UI and user interaction logic
- `process_documents.sql` - Document processing pipeline (parsing, chunking, indexing)
- `cortex_setup.sql` - Infrastructure setup (database, tables, roles, Git integration)

## Quick Start

### 1. Setup Infrastructure
```bash
./deploy.sh
```

### 2. Git-Based Deployment
The Streamlit app is automatically deployed from Git during infrastructure setup.

### 3. Access the App
Navigate to Snowsight → Streamlit → top_200_app

### 4. Upload Documents
1. Navigate to the "Upload Files" tab
2. Select PDF annual reports
3. Click "Upload to Snowflake Stage"

### 5. Process Documents
1. Go to "Stage Files" tab
2. Click "Process All Files"
3. Wait for processing to complete

### 6. Verify Processing
Check the "Processed Files" tab to see searchable documents.

## Features

- **Git Integration**: Automatic deployment from GitHub repository
- **File Upload**: Drag-and-drop PDF upload to Snowflake stage
- **Document Processing**: Automatic parsing, text extraction, and chunking
- **Search Ready**: Creates Cortex Search Service for semantic search
- **Progress Tracking**: Real-time status updates during processing
- **Error Handling**: Graceful handling of processing failures

## File Structure

```
├── streamlit_app.py          # Main Streamlit application
├── process_documents.sql     # Document processing pipeline
├── cortex_setup.sql         # Infrastructure setup with Git integration
├── environment.yml          # Snowflake dependencies
├── deploy.sh               # Deployment script
└── requirements.md         # Project requirements
```

## Dependencies

All dependencies are from the Snowflake Anaconda channel:
- `streamlit` - Web application framework
- `pandas` - Data manipulation
- `snowflake-snowpark-python` - Snowflake integration

## Next Steps

This foundation supports adding:
- Document analysis with AI prompts
- Company evaluation workflows  
- Advanced search and filtering
- Multi-page application features 