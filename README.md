# Top 200 Companies - AI Analysis Platform

A comprehensive multi-page Streamlit application for uploading annual reports, managing evaluation criteria, tracking media scan data, and conducting AI-powered ESG analysis using Snowflake Cortex.

## Architecture

**Multi-Page Structure with Separation of Concerns:**
- `streamlit_app.py` - Landing page and navigation hub
- `pages/document_processing.py` - Document upload and processing functionality
- `pages/criteria_management.py` - Evaluation criteria definition and management
- `pages/media_scan_management.py` - Media scan records and disqualification tracking
- `pages/ai_analysis.py` - AI-powered document analysis and evaluation
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
- **Media Scan Management**: Track company disqualification topics
- **AI Analysis**: Automated ESG evaluation with RAG
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

### 10. Manage Media Scan Data
Track company disqualification topics:
1. Navigate to **Media Scan Management** page
2. Add individual records or use bulk CSV upload
3. Monitor companies with negative media coverage
4. Use the data in AI analysis for comprehensive evaluation

## Features

- **Multi-Page Navigation**: Organized interface with specialized functionality
- **Landing Page**: Platform overview with system status and quick links
- **Git Integration**: Automatic deployment from GitHub repository
- **Document Processing**: Complete PDF upload, parsing, and AI preparation
- **Criteria Management**: Full CRUD operations for evaluation criteria
- **Media Scan Management**: Track company disqualification topics and negative media coverage
- **AI Analysis**: RAG-based document evaluation with media scan integration
- **Bulk Upload**: CSV import for criteria and media scan data with validation
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
│   ├── media_scan_management.py # Media scan records and disqualification tracking
│   ├── ai_analysis.py         # AI-powered document analysis with RAG
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
- System status monitoring (database, documents, criteria, media scans)
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

### 📰 **Media Scan Management**
- Track company disqualification topics and negative media coverage
- Create, read, update, delete media scan records
- Search and filter by company name or topic keywords
- Bulk CSV upload with format validation
- Visual status indicators (clean, issues found, no media)

### 🔍 **AI Analysis**
- RAG-based document analysis with semantic search
- Media scan integration for comprehensive evaluation
- Evidence-based AI scoring and justification
- Company-specific analysis with context retrieval

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

This comprehensive platform supports adding:
- **Results Dashboard**: Enhanced scoring visualization and evidence presentation
- **Advanced Search**: Multi-criteria document filtering and cross-referencing
- **Export Capabilities**: Report generation and comprehensive data export
- **User Management**: Role-based access and permissions
- **Analytics Dashboard**: Performance metrics and analysis trends
- **Automated Workflows**: Scheduled processing and notifications 