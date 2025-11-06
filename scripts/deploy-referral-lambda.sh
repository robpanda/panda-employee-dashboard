#!/bin/bash

# Deploy Referral System Lambda Function

FUNCTION_NAME="panda-referral-system-api"
REGION="us-east-2"
ROLE_ARN="arn:aws:iam::679128292059:role/lambda-dynamodb-role"

echo "Deploying Referral System Lambda..."

# Navigate to lambda directory
cd "$(dirname "$0")/../lambda/referral-system"

# Create deployment package
echo "Creating deployment package..."
rm -f function.zip
zip -r function.zip index.js package.json

# Check if function exists
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION 2>/dev/null; then
    echo "Updating existing function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://function.zip \
        --region $REGION

    echo "Waiting for update to complete..."
    aws lambda wait function-updated --function-name $FUNCTION_NAME --region $REGION

    echo "Updating function configuration..."
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --timeout 30 \
        --memory-size 512 \
        --region $REGION
else
    echo "Creating new function..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime nodejs18.x \
        --role $ROLE_ARN \
        --handler index.handler \
        --zip-file fileb://function.zip \
        --timeout 30 \
        --memory-size 512 \
        --region $REGION

    echo "Waiting for function to be ready..."
    aws lambda wait function-active --function-name $FUNCTION_NAME --region $REGION
fi

# Get function ARN
FUNCTION_ARN=$(aws lambda get-function --function-name $FUNCTION_NAME --region $REGION --query 'Configuration.FunctionArn' --output text)

echo ""
echo "✅ Lambda function deployed successfully!"
echo "Function ARN: $FUNCTION_ARN"

# Setup API Gateway integration
echo ""
echo "Setting up API Gateway integration..."

API_ID="7paaginnvg"  # Your existing API Gateway ID

# Get the root resource ID
ROOT_RESOURCE_ID=$(aws apigateway get-resources --rest-api-id $API_ID --region $REGION --query 'items[?path==`/`].id' --output text)

# Create /referral resource if it doesn't exist
REFERRAL_RESOURCE_ID=$(aws apigateway get-resources --rest-api-id $API_ID --region $REGION --query 'items[?path==`/referral`].id' --output text)

if [ -z "$REFERRAL_RESOURCE_ID" ]; then
    echo "Creating /referral resource..."
    REFERRAL_RESOURCE_ID=$(aws apigateway create-resource \
        --rest-api-id $API_ID \
        --parent-id $ROOT_RESOURCE_ID \
        --path-part referral \
        --region $REGION \
        --query 'id' --output text)
fi

echo "Referral resource ID: $REFERRAL_RESOURCE_ID"

# Create proxy resource for all paths under /referral
PROXY_RESOURCE_ID=$(aws apigateway get-resources --rest-api-id $API_ID --region $REGION --query 'items[?path==`/referral/{proxy+}`].id' --output text)

if [ -z "$PROXY_RESOURCE_ID" ]; then
    echo "Creating /referral/{proxy+} resource..."
    PROXY_RESOURCE_ID=$(aws apigateway create-resource \
        --rest-api-id $API_ID \
        --parent-id $REFERRAL_RESOURCE_ID \
        --path-part '{proxy+}' \
        --region $REGION \
        --query 'id' --output text)
fi

# Setup ANY method on proxy resource
echo "Setting up ANY method..."
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $PROXY_RESOURCE_ID \
    --http-method ANY \
    --authorization-type NONE \
    --region $REGION 2>/dev/null || echo "Method already exists"

# Setup integration
echo "Setting up Lambda integration..."
aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $PROXY_RESOURCE_ID \
    --http-method ANY \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri "arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/${FUNCTION_ARN}/invocations" \
    --region $REGION

# Add Lambda permission for API Gateway
echo "Adding API Gateway invoke permission..."
aws lambda add-permission \
    --function-name $FUNCTION_NAME \
    --statement-id apigateway-referral-any \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:${REGION}:679128292059:${API_ID}/*/*/*" \
    --region $REGION 2>/dev/null || echo "Permission already exists"

# Setup OPTIONS method for CORS
echo "Setting up OPTIONS method for CORS..."
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $PROXY_RESOURCE_ID \
    --http-method OPTIONS \
    --authorization-type NONE \
    --region $REGION 2>/dev/null || echo "OPTIONS method already exists"

aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $PROXY_RESOURCE_ID \
    --http-method OPTIONS \
    --type MOCK \
    --request-templates '{"application/json": "{\"statusCode\": 200}"}' \
    --region $REGION 2>/dev/null || echo "OPTIONS integration already exists"

aws apigateway put-method-response \
    --rest-api-id $API_ID \
    --resource-id $PROXY_RESOURCE_ID \
    --http-method OPTIONS \
    --status-code 200 \
    --response-parameters '{"method.response.header.Access-Control-Allow-Headers": true, "method.response.header.Access-Control-Allow-Methods": true, "method.response.header.Access-Control-Allow-Origin": true}' \
    --region $REGION 2>/dev/null || echo "OPTIONS method response already exists"

aws apigateway put-integration-response \
    --rest-api-id $API_ID \
    --resource-id $PROXY_RESOURCE_ID \
    --http-method OPTIONS \
    --status-code 200 \
    --response-parameters '{"method.response.header.Access-Control-Allow-Headers": "'"'"'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"'"'", "method.response.header.Access-Control-Allow-Methods": "'"'"'GET,POST,PUT,DELETE,OPTIONS'"'"'", "method.response.header.Access-Control-Allow-Origin": "'"'"'*'"'"'"}' \
    --region $REGION 2>/dev/null || echo "OPTIONS integration response already exists"

# Deploy API
echo "Deploying API..."
aws apigateway create-deployment \
    --rest-api-id $API_ID \
    --stage-name prod \
    --region $REGION

echo ""
echo "✅ API Gateway configured successfully!"
echo ""
echo "API Endpoint: https://${API_ID}.execute-api.${REGION}.amazonaws.com/prod/referral"
echo ""
echo "Available endpoints:"
echo "  GET  /referral/advocates"
echo "  POST /referral/advocates"
echo "  GET  /referral/advocates/{id}"
echo "  PUT  /referral/advocates/{id}"
echo "  GET  /referral/leads"
echo "  POST /referral/leads"
echo "  GET  /referral/leads/{id}"
echo "  PUT  /referral/leads/{id}"
echo "  GET  /referral/payouts"
echo "  PUT  /referral/payouts/{id}"
echo "  GET  /referral/reps"
echo "  GET  /referral/stats"
echo "  GET  /referral/dashboard"

# Cleanup
rm -f function.zip

echo ""
echo "Deployment complete!"
