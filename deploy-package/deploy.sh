#!/bin/bash

# Panda CRM Deployment Script

set -e

STACK_NAME="panda-crm-system"
REGION="us-east-1"
ENVIRONMENT="prod"

echo "🐼 Deploying Panda CRM System..."

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install AWS CLI first."
    exit 1
fi

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo "❌ SAM CLI not found. Installing..."
    pip install aws-sam-cli
fi

# Build the application
echo "📦 Building application..."
sam build

# Deploy the application
echo "🚀 Deploying to AWS..."
sam deploy \
    --stack-name $STACK_NAME \
    --region $REGION \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides Environment=$ENVIRONMENT \
    --confirm-changeset

# Get the API URL
echo "✅ Deployment complete!"
API_URL=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
    --output text)

echo ""
echo "🌐 Your API URL: $API_URL"
echo ""
echo "📝 Next steps:"
echo "1. Update leads.html with this API URL:"
echo "   const API_BASE = '$API_URL';"
echo "2. Set MOCK_MODE = false"
echo "3. Test your CRM system!"
echo ""

# Test the API
echo "🧪 Testing API endpoints..."
curl -s "$API_URL/contacts" > /dev/null && echo "✅ Contacts endpoint working" || echo "❌ Contacts endpoint failed"
curl -s "$API_URL/collections" > /dev/null && echo "✅ Collections endpoint working" || echo "❌ Collections endpoint failed"
curl -s "$API_URL/config" > /dev/null && echo "✅ Config endpoint working" || echo "❌ Config endpoint failed"

echo ""
echo "🎉 Panda CRM System is ready!"