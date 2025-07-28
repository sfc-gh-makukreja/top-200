# Top 200 Companies - AI Analysis Platform

A comprehensive multi-page Streamlit application for uploading annual reports, managing evaluation criteria, and conducting AI-powered ESG analysis using Snowflake Cortex.

## Architecture

**Multi-Page Structure with Separation of Concerns:**
- `streamlit_app.py` - Landing page and navigation hub
- `pages/document_processing.py` - Document upload and processing functionality
- `pages/criteria_management.py` - Evaluation criteria definition and management
- `pages/help.py` - User documentation and help
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

### 4. Navigate the Platform
- **Home Page**: Platform overview and system status
- **Document Processing**: Upload and process PDF documents
- **Criteria Management**: Define evaluation criteria
- **Help**: Complete documentation

### 5. Upload Documents
1. Navigate to **Document Processing** page
2. Go to "Upload Files" tab
3. Select PDF annual reports
4. Click "Upload to Snowflake Stage"

### 6. Process Documents
1. Stay in "Stage Files" tab
2. Click "Process All Files"
3. Wait for processing to complete

### 7. Verify Processing
Check the "Processed Files" tab to see searchable documents.

### 8. Manage Criteria
1. Navigate to **Criteria Management** page
2. Define evaluation criteria for AI analysis
3. Set up prompts for automated document evaluation
4. Use bulk CSV upload for multiple criteria

### 9. Load Sample Criteria (Optional)
Import the complete Deloitte criteria set:
1. Go to **Criteria Management** → **Bulk Upload**
2. Upload the provided `20250723_input_criteria.csv`
3. All 15 criteria with populated ROLE and OUTPUT fields will be imported

## Features

- **Multi-Page Navigation**: Organized interface with specialized functionality
- **Landing Page**: Platform overview with system status and quick links
- **Git Integration**: Automatic deployment from GitHub repository
- **Document Processing**: Complete PDF upload, parsing, and AI preparation
- **Criteria Management**: Full CRUD operations for evaluation criteria
- **Bulk Upload**: CSV import for multiple criteria with ARRAY support
- **Search Ready**: Creates Cortex Search Service for semantic search
- **Progress Tracking**: Real-time status updates during processing
- **Help Documentation**: Complete user guide and troubleshooting
- **Error Handling**: Graceful handling of processing failures
- **System Monitoring**: Live database and service status indicators

## File Structure

```
├── streamlit_app.py          # Landing page and navigation hub
├── pages/
│   ├── document_processing.py # Document upload and processing
│   ├── criteria_management.py # Criteria definition and management  
│   └── help.py               # User documentation and help
├── utils.py                # Python utilities and document processing engine
├── process_documents.sql    # SQL document processing pipeline
├── cortex_setup.sql        # Infrastructure setup with Git integration
├── 20250723_input_criteria.csv # Complete Deloitte criteria dataset
├── environment.yml         # Snowflake dependencies
├── deploy.sh              # Deployment script
└── requirements.md        # Project requirements
```

## Available Pages

### 🏠 **Home (streamlit_app.py)**
- Platform overview and feature summary
- System status monitoring (database, documents, criteria)
- Quick navigation links
- Getting started guide

### 📄 **Document Processing** 
- PDF file upload to Snowflake stage
- Automated document processing with AI
- Processing status and file management
- Cortex Search Service integration

### 📋 **Criteria Management**
- Create, read, update, delete evaluation criteria
- Form-based criteria definition with ID, role, instructions
- Bulk CSV upload with ARRAY type support
- Complete Deloitte methodology criteria included

### 📚 **Help & Documentation**
- Complete user guide and troubleshooting
- Feature explanations and best practices
- Platform navigation assistance

## Navigation

The application uses Streamlit's multi-page structure:
1. **Pages Menu**: Use the dropdown in the upper left corner
2. **Sidebar Links**: Quick navigation buttons in the sidebar
3. **Landing Page**: Feature cards with direct navigation buttons

## Dependencies

All dependencies are from the Snowflake Anaconda channel:
- `streamlit` - Web application framework
- `pandas` - Data manipulation
- `snowflake-snowpark-python` - Snowflake integration

## Development Notes

### Pages Structure Benefits
- **Modular Design**: Each page handles specific functionality
- **Clean Separation**: Landing page stays lightweight
- **Scalability**: Easy to add new pages and features
- **Maintainability**: Clear responsibility boundaries
- **User Experience**: Organized navigation and focused workflows

### File Organization
- **Main App**: Minimal landing page with navigation
- **Feature Pages**: Self-contained functionality modules
- **Shared Resources**: Common utilities and processors
- **Infrastructure**: Database setup and deployment scripts

## Next Steps

This foundation supports adding:
- **AI Analysis Engine**: Automated document evaluation with criteria
- **Results Dashboard**: Scoring and evidence presentation
- **Advanced Search**: Multi-criteria document filtering
- **Export Capabilities**: Report generation and data export
- **User Management**: Role-based access and permissions 