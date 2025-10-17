#!/bin/bash

# Deploy updated Lambda function with Shopify sync fixes
FUNCTION_NAME="panda-employee-api"
REGION="us-east-2"

echo "🔧 Creating deployment package..."
zip -q lambda-shopify-fix.zip lambda_function.py

echo "📦 Deploying Lambda function to AWS..."
aws lambda update-function-code \
    --function-name $FUNCTION_NAME \
    --zip-file fileb://lambda-shopify-fix.zip \
    --region $REGION

if [ $? -eq 0 ]; then
    echo "✅ Lambda function deployed successfully!"
    
    # Wait for update to complete
    echo "⏳ Waiting for deployment to complete..."
    sleep 5
    
    # Check status
    STATUS=$(aws lambda get-function \
        --function-name $FUNCTION_NAME \
        --region $REGION \
        --query 'Configuration.LastUpdateStatus' \
        --output text)
    
    echo "Status: $STATUS"
    
    if [ "$STATUS" = "Successful" ]; then
        echo "🎉 Deployment completed successfully!"
        echo ""
        echo "✨ New features deployed:"
        echo "  - Date + order number deduplication"
        echo "  - Auto-cleanup after sync"
        echo "  - Manual edit endpoint: /update-employee-merchandise"
        echo ""
        echo "📝 Next steps:"
        echo "  1. Add manual edit UI to employee.html (see manual_edit_ui.html)"
        echo "  2. Test the sync button"
        echo "  3. Test manual editing"
    else
        echo "⚠️  Deployment status: $STATUS"
    fi
else
    echo "❌ Deployment failed!"
    exit 1
fi

# Clean up
rm lambda-shopify-fix.zip

echo ""
echo "Done! 🚀"
