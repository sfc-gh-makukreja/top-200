import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Help & Documentation",
    page_icon="❓",
    layout="wide"
)

def main():
    st.title("Help & Documentation")
    st.markdown("Complete guide to using the Top 200 Companies application")
    
    # Sidebar navigation
    with st.sidebar:
        st.title("📚 Help Topics")
        topic = st.radio(
            "Select a topic:",
            [
                "Overview",
                "Document Processing",
                "Criteria Management", 
                "Analysis Workflow",
                "Troubleshooting"
            ]
        )
    
    if topic == "Overview":
        st.header("🏢 Application Overview")
        
        st.markdown("""
        The Top 200 Companies application is designed to process annual reports and perform 
        AI-powered analysis using Snowflake Cortex. The system allows you to:
        
        - **Upload PDF Documents**: Load annual reports into Snowflake
        - **Process with AI**: Extract and chunk text using Cortex AI
        - **Manage Criteria**: Define evaluation criteria for analysis
        - **Run Analysis**: Query documents based on specific criteria
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔄 Workflow")
            st.markdown("""
            1. **Upload** PDF files to the stage
            2. **Process** documents with Cortex AI
            3. **Define** evaluation criteria
            4. **Analyze** documents against criteria
            5. **Review** results and insights
            """)
        
        with col2:
            st.subheader("🛠️ Key Features")
            st.markdown("""
            - **PDF Processing**: OCR and text extraction
            - **Semantic Search**: AI-powered document search
            - **Flexible Criteria**: Customizable evaluation framework
            - **Version Control**: Track criteria versions
            - **Role-based Analysis**: Different analytical perspectives
            """)
    
    elif topic == "Document Processing":
        st.header("📄 Document Processing Guide")
        
        st.subheader("1. Upload Files")
        st.markdown("""
        - Go to the main **Document Processing** page
        - Use the **Upload Files** tab
        - Select one or more PDF files
        - Click **Upload to Snowflake Stage**
        """)
        
        st.subheader("2. Process Documents")
        st.markdown("""
        - Switch to the **Stage Files** tab
        - Review uploaded files
        - Click **Process All Files** to start AI processing
        - Wait for completion (processing time varies by document size)
        """)
        
        st.subheader("3. Verify Processing")
        st.markdown("""
        - Check the **Processed Files** tab
        - Verify all documents appear with chunk counts
        - Documents are now searchable via Cortex Search
        """)
        
        st.info("💡 **Tip**: Processing can take several minutes for large documents. The system uses OCR for text extraction.")
    
    elif topic == "Criteria Management":
        st.header("⚙️ Criteria Management Guide")
        
        st.markdown("""
        The Criteria Management page allows you to define evaluation criteria for document analysis.
        Each criterion represents a specific question or evaluation framework.
        """)
        
        st.subheader("📋 Criteria Fields")
        
        with st.expander("Field Descriptions"):
            st.markdown("""
            - **Question** (*required*): The main evaluation question
            - **Cluster**: Categories or themes (comma-separated)
            - **Role**: Analytical perspective (e.g., Financial Analyst, ESG Expert)
            - **Instructions**: Detailed evaluation instructions
            - **Expected Output**: Format of the expected result
            - **Criteria Prompt** (*required*): The actual AI prompt
            - **Weight**: Importance weighting (0.0 - 10.0)
            - **Version**: Version identifier for tracking
            - **Active**: Whether the criteria is currently active
            """)
        
        st.subheader("🔧 Managing Criteria")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Adding New Criteria:**")
            st.markdown("""
            1. Click **➕ Add New**
            2. Fill in the form fields
            3. Write a clear criteria prompt
            4. Set appropriate weight
            5. Click **💾 Save**
            """)
        
        with col2:
            st.markdown("**Editing Criteria:**")
            st.markdown("""
            1. Find the criteria in the list
            2. Click **✏️ Edit**
            3. Modify the fields as needed
            4. Click **💾 Save**
            """)
        
        st.subheader("💡 Best Practices")
        
        st.markdown("""
        - **Clear Questions**: Write specific, actionable questions
        - **Detailed Prompts**: Include context and expected format in prompts
        - **Version Control**: Use version numbers when updating criteria
        - **Appropriate Weights**: Assign weights based on importance
        - **Test Criteria**: Deactivate rather than delete when testing
        """)
        
        st.subheader("📝 Example Criteria")
        
        with st.expander("Sample Financial Performance Criteria"):
            st.code("""
Question: What is the company's revenue growth trend over the past 3 years?

Role: Financial Analyst

Instructions: Analyze revenue figures from the annual report and calculate year-over-year growth rates. Look for trends and any explanations provided by management.

Criteria Prompt: Based on the annual report, calculate the revenue growth rate for each of the past 3 years. Provide the growth percentages and briefly explain any significant changes. Format: "Year 1: X%, Year 2: Y%, Year 3: Z%. Key factors: [explanation]"

Expected Output: Percentage growth rates with brief explanation

Weight: 3.0

Version: 1.0
            """, language="text")
    
    elif topic == "Analysis Workflow":
        st.header("🔍 Analysis Workflow")
        
        st.markdown("""
        Once you have processed documents and defined criteria, you can run analysis 
        using the Cortex Search functionality.
        """)
        
        st.subheader("🔄 Typical Analysis Process")
        
        st.markdown("""
        1. **Prepare Documents**: Ensure PDFs are uploaded and processed
        2. **Define Criteria**: Create relevant evaluation criteria
        3. **Run Queries**: Use semantic search to find relevant content
        4. **Apply Criteria**: Analyze found content against criteria
        5. **Review Results**: Examine outputs and justifications
        """)
        
        st.subheader("🎯 Search Tips")
        
        st.markdown("""
        - Use **semantic terms** rather than exact phrases
        - Try **different wordings** for the same concept
        - **Combine criteria** for comprehensive analysis
        - **Filter by company** or year for targeted analysis
        """)
        
        st.info("💡 **Note**: The current version focuses on document processing and criteria management. Full analysis workflows will be available in future updates.")
    
    elif topic == "Troubleshooting":
        st.header("🔧 Troubleshooting")
        
        st.subheader("🔗 Connection Issues")
        st.markdown("""
        **Problem**: "Failed to connect to Snowflake"
        
        **Solutions**:
        - Verify your Snowflake credentials in Streamlit
        - Check that the warehouse is running
        - Ensure you have the correct role permissions
        """)
        
        st.subheader("📄 Processing Issues")
        st.markdown("""
        **Problem**: Documents not processing correctly
        
        **Solutions**:
        - Ensure PDFs are not password-protected
        - Check file size limits
        - Verify stage permissions
        - Try processing one file at a time
        """)
        
        st.subheader("⚙️ Criteria Issues")
        st.markdown("""
        **Problem**: Cannot save criteria
        
        **Solutions**:
        - Check that required fields are filled
        - Verify database permissions
        - Ensure cluster field uses proper comma separation
        - Try refreshing the page
        """)
        
        st.subheader("🔍 Search Issues")
        st.markdown("""
        **Problem**: Search not returning results
        
        **Solutions**:
        - Verify documents are fully processed
        - Check that Cortex Search service is created
        - Try different search terms
        - Ensure content contains the searched information
        """)
        
        st.subheader("📞 Getting Help")
        st.info("""
        For additional support:
        - Check the Snowflake documentation
        - Review error messages carefully
        - Try refreshing the application
        - Contact your system administrator
        """)

if __name__ == "__main__":
    main() 