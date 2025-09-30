#!/bin/bash

# Update frontend with deployed API URL

STACK_NAME="panda-crm-system"
REGION="us-east-1"

# Get API URL from CloudFormation
API_URL=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
    --output text)

if [ -z "$API_URL" ]; then
    echo "❌ Could not get API URL. Make sure the stack is deployed."
    exit 1
fi

echo "🔧 Updating frontend with API URL: $API_URL"

# Update leads.html
sed -i.bak "s|const API_BASE = '.*';|const API_BASE = '$API_URL';|g" ../leads.html
sed -i.bak "s|const MOCK_MODE = true;|const MOCK_MODE = false;|g" ../leads.html

echo "✅ Frontend updated successfully!"
echo "📝 Changes made to leads.html:"
echo "   - API_BASE set to: $API_URL"
echo "   - MOCK_MODE set to: false"
echo ""
echo "🎉 Your CRM system is now connected to the live API!"