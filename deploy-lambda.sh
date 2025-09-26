#!/bin/bash

# Deploy consolidated Lambda function
FUNCTION_NAME="panda-employee-api"
REGION="us-east-1"

echo "Creating deployment package..."
zip -r lambda-deployment.zip consolidated_lambda.py

echo "Deploying Lambda function..."
aws lambda update-function-code \
    --function-name $FUNCTION_NAME \
    --zip-file fileb://lambda-deployment.zip \
    --region $REGION

if [ $? -ne 0 ]; then
    echo "Update failed, creating new function..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime python3.9 \
        --role arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/lambda-execution-role \
        --handler consolidated_lambda.lambda_handler \
        --zip-file fileb://lambda-deployment.zip \
        --region $REGION
fi

echo "Creating function URL..."
FUNCTION_URL=$(aws lambda create-function-url-config \
    --function-name $FUNCTION_NAME \
    --cors AllowCredentials=false,AllowHeaders=Content-Type,AllowMethods=GET,POST,OPTIONS,AllowOrigins=* \
    --auth-type NONE \
    --region $REGION \
    --query FunctionUrl --output text 2>/dev/null)

if [ -z "$FUNCTION_URL" ]; then
    FUNCTION_URL=$(aws lambda get-function-url-config \
        --function-name $FUNCTION_NAME \
        --region $REGION \
        --query FunctionUrl --output text)
fi

echo "Function URL: $FUNCTION_URL"

# Update dashboard with function URL
sed -i.bak "s|const API_URL = '.*';|const API_URL = '${FUNCTION_URL%/}';|" dashboard.html

echo "Updated dashboard.html with API URL"
echo "Deployment complete!"

# Clean up
rm lambda-deployment.zip
rm dashboard.html.bak 2>/dev/null || true