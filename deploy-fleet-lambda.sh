#!/bin/bash

set -e

echo "🚗 Deploying Fleet Management Lambda Function..."

# Variables
FUNCTION_NAME="panda-fleet-management"
LAMBDA_ROLE="arn:aws:iam::679128292059:role/lambda-dynamodb-role"
REGION="us-east-2"
API_ID="z6q74akq5f"

# Create deployment package
echo "📦 Creating deployment package..."
cd /Users/robwinters/Documents/GitHub/panda-employee-dashboard
zip -j lambda_fleet.zip lambda_fleet.py

# Check if function exists
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION 2>/dev/null; then
    echo "♻️  Updating existing Lambda function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://lambda_fleet.zip \
        --region $REGION

    echo "⏳ Waiting for function to update..."
    aws lambda wait function-updated \
        --function-name $FUNCTION_NAME \
        --region $REGION

    echo "⚙️  Updating function configuration..."
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --timeout 30 \
        --memory-size 256 \
        --region $REGION
else
    echo "🆕 Creating new Lambda function..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime python3.11 \
        --role $LAMBDA_ROLE \
        --handler lambda_fleet.lambda_handler \
        --zip-file fileb://lambda_fleet.zip \
        --timeout 30 \
        --memory-size 256 \
        --region $REGION

    echo "⏳ Waiting for function to be active..."
    aws lambda wait function-active \
        --function-name $FUNCTION_NAME \
        --region $REGION
fi

echo ""
echo "🔧 Setting up API Gateway routes..."

# Get the root resource ID
ROOT_ID=$(aws apigateway get-resources --rest-api-id $API_ID --region $REGION --query "items[?path=='/'].id" --output text)

# Create /vehicles resource if it doesn't exist
VEHICLES_RESOURCE=$(aws apigateway get-resources --rest-api-id $API_ID --region $REGION --query "items[?path=='/vehicles'].id" --output text)
if [ -z "$VEHICLES_RESOURCE" ]; then
    echo "Creating /vehicles resource..."
    VEHICLES_RESOURCE=$(aws apigateway create-resource \
        --rest-api-id $API_ID \
        --parent-id $ROOT_ID \
        --path-part vehicles \
        --region $REGION \
        --query 'id' --output text)
fi

# Create /accidents resource if it doesn't exist
ACCIDENTS_RESOURCE=$(aws apigateway get-resources --rest-api-id $API_ID --region $REGION --query "items[?path=='/accidents'].id" --output text)
if [ -z "$ACCIDENTS_RESOURCE" ]; then
    echo "Creating /accidents resource..."
    ACCIDENTS_RESOURCE=$(aws apigateway create-resource \
        --rest-api-id $API_ID \
        --parent-id $ROOT_ID \
        --path-part accidents \
        --region $REGION \
        --query 'id' --output text)
fi

# Create /ezpass resource if it doesn't exist
EZPASS_RESOURCE=$(aws apigateway get-resources --rest-api-id $API_ID --region $REGION --query "items[?path=='/ezpass'].id" --output text)
if [ -z "$EZPASS_RESOURCE" ]; then
    echo "Creating /ezpass resource..."
    EZPASS_RESOURCE=$(aws apigateway create-resource \
        --rest-api-id $API_ID \
        --parent-id $ROOT_ID \
        --path-part ezpass \
        --region $REGION \
        --query 'id' --output text)
fi

# Create /maintenance resource if it doesn't exist
MAINTENANCE_RESOURCE=$(aws apigateway get-resources --rest-api-id $API_ID --region $REGION --query "items[?path=='/maintenance'].id" --output text)
if [ -z "$MAINTENANCE_RESOURCE" ]; then
    echo "Creating /maintenance resource..."
    MAINTENANCE_RESOURCE=$(aws apigateway create-resource \
        --rest-api-id $API_ID \
        --parent-id $ROOT_ID \
        --path-part maintenance \
        --region $REGION \
        --query 'id' --output text)
fi

# Create /requests resource if it doesn't exist
REQUESTS_RESOURCE=$(aws apigateway get-resources --rest-api-id $API_ID --region $REGION --query "items[?path=='/requests'].id" --output text)
if [ -z "$REQUESTS_RESOURCE" ]; then
    echo "Creating /requests resource..."
    REQUESTS_RESOURCE=$(aws apigateway create-resource \
        --rest-api-id $API_ID \
        --parent-id $ROOT_ID \
        --path-part requests \
        --region $REGION \
        --query 'id' --output text)
fi

# Create /fleet-stats resource if it doesn't exist
STATS_RESOURCE=$(aws apigateway get-resources --rest-api-id $API_ID --region $REGION --query "items[?path=='/fleet-stats'].id" --output text)
if [ -z "$STATS_RESOURCE" ]; then
    echo "Creating /fleet-stats resource..."
    STATS_RESOURCE=$(aws apigateway create-resource \
        --rest-api-id $API_ID \
        --parent-id $ROOT_ID \
        --path-part fleet-stats \
        --region $REGION \
        --query 'id' --output text)
fi

# Function to setup method and integration
setup_method() {
    local RESOURCE_ID=$1
    local METHOD=$2
    local PATH=$3

    echo "Setting up $METHOD for $PATH..."

    # Create method
    aws apigateway put-method \
        --rest-api-id $API_ID \
        --resource-id $RESOURCE_ID \
        --http-method $METHOD \
        --authorization-type NONE \
        --region $REGION 2>/dev/null || true

    # Setup integration
    aws apigateway put-integration \
        --rest-api-id $API_ID \
        --resource-id $RESOURCE_ID \
        --http-method $METHOD \
        --type AWS_PROXY \
        --integration-http-method POST \
        --uri "arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/arn:aws:lambda:$REGION:679128292059:function:$FUNCTION_NAME/invocations" \
        --region $REGION 2>/dev/null || true

    # Add Lambda permission
    aws lambda add-permission \
        --function-name $FUNCTION_NAME \
        --statement-id "apigateway-$PATH-$METHOD-$(date +%s)" \
        --action lambda:InvokeFunction \
        --principal apigateway.amazonaws.com \
        --source-arn "arn:aws:execute-api:$REGION:679128292059:$API_ID/*/$METHOD/$PATH" \
        --region $REGION 2>/dev/null || true
}

# Setup methods for each resource
setup_method $VEHICLES_RESOURCE "GET" "vehicles"
setup_method $VEHICLES_RESOURCE "POST" "vehicles"
setup_method $VEHICLES_RESOURCE "PUT" "vehicles"
setup_method $VEHICLES_RESOURCE "DELETE" "vehicles"
setup_method $VEHICLES_RESOURCE "OPTIONS" "vehicles"

setup_method $ACCIDENTS_RESOURCE "GET" "accidents"
setup_method $ACCIDENTS_RESOURCE "POST" "accidents"
setup_method $ACCIDENTS_RESOURCE "PUT" "accidents"
setup_method $ACCIDENTS_RESOURCE "OPTIONS" "accidents"

setup_method $EZPASS_RESOURCE "GET" "ezpass"
setup_method $EZPASS_RESOURCE "POST" "ezpass"
setup_method $EZPASS_RESOURCE "PUT" "ezpass"
setup_method $EZPASS_RESOURCE "OPTIONS" "ezpass"

setup_method $MAINTENANCE_RESOURCE "GET" "maintenance"
setup_method $MAINTENANCE_RESOURCE "POST" "maintenance"
setup_method $MAINTENANCE_RESOURCE "PUT" "maintenance"
setup_method $MAINTENANCE_RESOURCE "OPTIONS" "maintenance"

setup_method $REQUESTS_RESOURCE "GET" "requests"
setup_method $REQUESTS_RESOURCE "POST" "requests"
setup_method $REQUESTS_RESOURCE "PUT" "requests"
setup_method $REQUESTS_RESOURCE "OPTIONS" "requests"

setup_method $STATS_RESOURCE "GET" "fleet-stats"
setup_method $STATS_RESOURCE "OPTIONS" "fleet-stats"

# Deploy API
echo ""
echo "🚀 Deploying API Gateway..."
aws apigateway create-deployment \
    --rest-api-id $API_ID \
    --stage-name prod \
    --region $REGION

echo ""
echo "📄 Deploying frontend to S3..."
aws s3 cp fleet-assets.html s3://pandaadmin.com/fleet-assets.html --region us-east-2

# Invalidate CloudFront cache
echo "🔄 Invalidating CloudFront cache..."
aws cloudfront create-invalidation \
    --distribution-id E3SHO6SR70F1DM \
    --paths "/fleet-assets.html"

echo ""
echo "✅ Fleet Management System deployed successfully!"
echo ""
echo "📊 Access the system at:"
echo "   https://pandaadmin.com/fleet-assets.html"
echo ""
echo "🔗 API Endpoints:"
echo "   GET/POST/PUT    https://z6q74akq5f.execute-api.us-east-2.amazonaws.com/prod/vehicles"
echo "   GET/POST/PUT    https://z6q74akq5f.execute-api.us-east-2.amazonaws.com/prod/accidents"
echo "   GET/POST/PUT    https://z6q74akq5f.execute-api.us-east-2.amazonaws.com/prod/ezpass"
echo "   GET/POST/PUT    https://z6q74akq5f.execute-api.us-east-2.amazonaws.com/prod/maintenance"
echo "   GET/POST/PUT    https://z6q74akq5f.execute-api.us-east-2.amazonaws.com/prod/requests"
echo "   GET             https://z6q74akq5f.execute-api.us-east-2.amazonaws.com/prod/fleet-stats"

# Clean up
rm lambda_fleet.zip

echo ""
echo "🎉 Deployment complete!"
