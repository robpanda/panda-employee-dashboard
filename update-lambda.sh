#!/bin/bash

# Update existing Lambda function with new CRM endpoints

echo "Updating Lambda function..."

# Get your existing Lambda function name (replace with actual name)
FUNCTION_NAME="your-existing-lambda-function-name"

# Zip the updated function
zip lambda-update.zip lambda_function.py

# Update the function code
aws lambda update-function-code \
    --function-name $FUNCTION_NAME \
    --zip-file fileb://lambda-update.zip \
    --region us-east-1

# Update environment variables
aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --environment Variables='{
        "EMPLOYEES_TABLE":"panda-employees",
        "CONTACTS_TABLE":"panda-contacts",
        "COLLECTIONS_TABLE":"panda-collections",
        "CONFIG_TABLE":"panda-config"
    }' \
    --region us-east-1

echo "Lambda function updated successfully!"

# Get the API Gateway URL
echo "Your API Gateway URL:"
aws apigateway get-rest-apis --query 'items[?name==`your-api-name`].{id:id,name:name}' --output table --region us-east-1