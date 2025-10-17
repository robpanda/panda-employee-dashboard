#!/bin/bash

# Deploy Panda Assets API Lambda Function
FUNCTION_NAME="panda-assets-api"
REGION="us-east-2"
ROLE_NAME="panda-assets-lambda-role"

echo "🔧 Creating IAM role for Lambda..."

# Create IAM role with trust policy
TRUST_POLICY='{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}'

# Create role if it doesn't exist
aws iam create-role \
    --role-name $ROLE_NAME \
    --assume-role-policy-document "$TRUST_POLICY" \
    --region $REGION 2>/dev/null || echo "Role already exists"

# Attach basic Lambda execution policy
aws iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole \
    --region $REGION 2>/dev/null

# Create custom policy for DynamoDB and S3 access
POLICY_DOCUMENT='{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": [
        "arn:aws:dynamodb:us-east-2:*:table/panda-assets",
        "arn:aws:dynamodb:us-east-2:*:table/panda-assets/index/*",
        "arn:aws:dynamodb:us-east-2:*:table/panda-employees"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::panda-assets-docs/*"
    }
  ]
}'

# Create or update custom policy
POLICY_ARN=$(aws iam create-policy \
    --policy-name panda-assets-lambda-policy \
    --policy-document "$POLICY_DOCUMENT" \
    --region $REGION 2>/dev/null | jq -r '.Policy.Arn')

if [ -z "$POLICY_ARN" ] || [ "$POLICY_ARN" == "null" ]; then
    # Policy already exists, get ARN
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    POLICY_ARN="arn:aws:iam::${ACCOUNT_ID}:policy/panda-assets-lambda-policy"
fi

# Attach custom policy to role
aws iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn $POLICY_ARN \
    --region $REGION 2>/dev/null

echo "⏳ Waiting for IAM role to propagate..."
sleep 10

# Get role ARN
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"

echo "📦 Creating deployment package..."
cd /tmp
zip -q lambda-assets.zip lambda_assets.py

echo "🚀 Creating Lambda function..."
aws lambda create-function \
    --function-name $FUNCTION_NAME \
    --runtime python3.12 \
    --role $ROLE_ARN \
    --handler lambda_assets.lambda_handler \
    --zip-file fileb://lambda-assets.zip \
    --timeout 30 \
    --memory-size 256 \
    --region $REGION 2>/dev/null

if [ $? -ne 0 ]; then
    echo "📝 Function exists, updating code..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://lambda-assets.zip \
        --region $REGION
fi

echo "⏳ Waiting for Lambda to be ready..."
sleep 5

echo "🔗 Creating Function URL..."
aws lambda create-function-url-config \
    --function-name $FUNCTION_NAME \
    --auth-type NONE \
    --cors '{
        "AllowOrigins": ["*"],
        "AllowMethods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "AllowHeaders": ["*"],
        "MaxAge": 86400
    }' \
    --region $REGION 2>/dev/null || echo "Function URL already exists"

# Add permission for function URL
aws lambda add-permission \
    --function-name $FUNCTION_NAME \
    --statement-id FunctionURLAllowPublicAccess \
    --action lambda:InvokeFunctionUrl \
    --principal "*" \
    --function-url-auth-type NONE \
    --region $REGION 2>/dev/null || echo "Permission already exists"

# Get function URL
FUNCTION_URL=$(aws lambda get-function-url-config \
    --function-name $FUNCTION_NAME \
    --region $REGION \
    --query 'FunctionUrl' \
    --output text)

echo ""
echo "✅ Deployment complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Function Name: $FUNCTION_NAME"
echo "Function URL: $FUNCTION_URL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "API Endpoints:"
echo "  POST   ${FUNCTION_URL}requests"
echo "  GET    ${FUNCTION_URL}requests"
echo "  GET    ${FUNCTION_URL}requests/{id}"
echo "  PUT    ${FUNCTION_URL}requests/{id}/approve"
echo "  PUT    ${FUNCTION_URL}requests/{id}/reject"
echo "  POST   ${FUNCTION_URL}requests/{id}/pdf"
echo "  POST   ${FUNCTION_URL}requests/{id}/sign"
echo "  GET    ${FUNCTION_URL}inventory"
echo ""

# Cleanup
rm lambda-assets.zip
