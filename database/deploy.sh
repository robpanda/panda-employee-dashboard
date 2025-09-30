#!/bin/bash

# Deploy CRM Lambda Function
echo "Deploying CRM Lambda Function..."

# Create deployment package
mkdir -p package
pip install -r requirements.txt -t package/
cp lambda_crm.py package/

# Create ZIP file
cd package
zip -r ../crm-lambda.zip .
cd ..

# Deploy to AWS Lambda
aws lambda create-function \
    --function-name panda-crm-api \
    --runtime python3.9 \
    --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role \
    --handler lambda_crm.lambda_handler \
    --zip-file fileb://crm-lambda.zip \
    --environment Variables='{
        "DB_HOST":"your-rds-endpoint.amazonaws.com",
        "DB_USER":"admin",
        "DB_PASSWORD":"your-password",
        "DB_NAME":"panda_crm"
    }'

# Create API Gateway
aws apigatewayv2 create-api \
    --name panda-crm-api \
    --protocol-type HTTP \
    --target arn:aws:lambda:us-east-1:YOUR_ACCOUNT:function:panda-crm-api

echo "Deployment complete!"
echo "Update your frontend API_BASE URL to the API Gateway endpoint"