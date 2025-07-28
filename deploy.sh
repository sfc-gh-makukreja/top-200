#!/bin/bash
set -e

echo "🚀 Starting Top 200 Companies App Deployment..."

# Validate Snowflake connection
echo "🔍 Testing Snowflake connection..."
if ! snow connection test --connection top_200; then
    echo "❌ Snowflake connection failed. Please check your connection settings."
    exit 1
fi

# Deploy infrastructure (if not already done)
echo "🏗️  Setting up infrastructure..."
snow sql -f cortex_setup.sql --connection top_200

echo "✅ Infrastructure and Git-based Streamlit app deployed successfully!"
echo "📱 Your app is now available in Snowsight under Streamlit Apps."
echo ""
echo "Next steps:"
echo "1. Navigate to Snowsight → Streamlit → top_200_app"
echo "2. Upload PDF annual reports using the app"
echo "3. Click 'Process All Files' to make them searchable"
echo "4. Documents will be ready for AI analysis" 