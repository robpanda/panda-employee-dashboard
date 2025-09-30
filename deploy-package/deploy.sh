#!/bin/bash

# Panda CRM Deployment Script

set -e

STACK_NAME="panda-crm-system"
REGION="us-east-1"
ENVIRONMENT="prod"

# Generate Riley API Key
RILEY_API_KEY="riley_$(openssl rand -hex 16)"

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
    --parameter-overrides Environment=$ENVIRONMENT RileyApiKey=$RILEY_API_KEY \
    --confirm-changeset

# Get the API URL
echo "✅ Deployment complete!"
API_URL=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
    --output text)

RILEY_SECRET_ID=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`RileySecretId`].OutputValue' \
    --output text)

echo ""
echo "🌐 Your API URL: $API_URL"
echo "🔑 Riley Secret ID: $RILEY_SECRET_ID"
echo "🔐 Riley API Key: $RILEY_API_KEY"
echo ""
echo "📝 Next steps:"
echo "1. Update leads.html with this API URL:"
echo "   const API_BASE = '$API_URL';"
echo "2. Set MOCK_MODE = false"
echo "3. Configure Riley platform with:"
echo "   - Secret ID: $RILEY_SECRET_ID"
echo "   - API Key: $RILEY_API_KEY"
echo "4. Test your CRM system!"
echo ""

# Test the API
echo "🧪 Testing API endpoints..."
curl -s "$API_URL/contacts" > /dev/null && echo "✅ Contacts endpoint working" || echo "❌ Contacts endpoint failed"
curl -s "$API_URL/collections" > /dev/null && echo "✅ Collections endpoint working" || echo "❌ Collections endpoint failed"
curl -s "$API_URL/config" > /dev/null && echo "✅ Config endpoint working" || echo "❌ Config endpoint failed"
curl -s "$API_URL/riley/auth" > /dev/null && echo "✅ Riley auth endpoint working" || echo "❌ Riley auth endpoint failed"

echo ""
echo "🎉 Panda CRM System is ready!"