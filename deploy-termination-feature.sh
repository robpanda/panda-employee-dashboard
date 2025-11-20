#!/bin/bash

# Deploy Automatic Termination Login Blocking Feature
# This script deploys the updated Lambda function that blocks terminated employees from logging in

REGION="us-east-2"
PROFILE="mypodops"

echo "=== Deploying Termination Login Blocking Feature ==="
echo ""

# Package the Lambda function
echo "1. Packaging Lambda function..."
cd /Users/robwinters/Documents/GitHub/panda-employee-dashboard
zip -q lambda_function.zip lambda_function.py
echo "✅ Lambda packaged"
echo ""

# Find the Lambda function name by checking for the URL
echo "2. Finding Lambda function name..."
FUNCTION_NAME=$(AWS_PROFILE=$PROFILE python3 << 'EOF'
import boto3
lambda_client = boto3.client('lambda', region_name='us-east-2')
response = lambda_client.list_functions()
for func in response['Functions']:
    try:
        url_config = lambda_client.get_function_url_config(FunctionName=func['FunctionName'])
        if 'dfu3zr3dnrvgiiwa2yu77cz5fq0rqmth' in url_config.get('FunctionUrl', ''):
            print(func['FunctionName'])
            break
    except:
        pass
EOF
)

if [ -z "$FUNCTION_NAME" ]; then
    echo "❌ Could not find Lambda function with URL dfu3zr3dnrvgiiwa2yu77cz5fq0rqmth"
    echo ""
    echo "Please manually update the Lambda function by:"
    echo "1. Going to AWS Lambda console"
    echo "2. Finding the function with URL: https://dfu3zr3dnrvgiiwa2yu77cz5fq0rqmth.lambda-url.us-east-2.on.aws"
    echo "3. Uploading lambda_function.zip"
    exit 1
fi

echo "Found function: $FUNCTION_NAME"
echo ""

# Deploy the updated code
echo "3. Deploying to Lambda..."
AWS_PROFILE=$PROFILE aws lambda update-function-code \
    --function-name $FUNCTION_NAME \
    --zip-file fileb://lambda_function.zip \
    --region $REGION \
    --query 'LastModified' \
    --output text

if [ $? -eq 0 ]; then
    echo "✅ Lambda function updated successfully"
    echo ""

    # Wait for function to be ready
    echo "4. Waiting for function to be ready..."
    AWS_PROFILE=$PROFILE aws lambda wait function-updated \
        --function-name $FUNCTION_NAME \
        --region $REGION
    echo "✅ Function is ready"
    echo ""

    echo "=== Deployment Complete ==="
    echo ""
    echo "Changes deployed:"
    echo "✅ Employees with termination dates are automatically marked as inactive"
    echo "✅ Inactive employees cannot log into any Panda portals"
    echo "✅ Setting a termination date on https://pandaadmin.com/employee will:"
    echo "   - Set status = 'inactive'"
    echo "   - Set is_active = false"
    echo "   - Set Terminated = 'Yes'"
    echo "✅ Clearing the termination date will re-activate the account"
    echo ""
    echo "Test by:"
    echo "1. Go to https://pandaadmin.com/employee"
    echo "2. Add a termination date to a test employee"
    echo "3. Try logging in as that employee - should be blocked"
    echo "4. Clear the termination date"
    echo "5. Try logging in again - should work"
else
    echo "❌ Deployment failed"
    exit 1
fi
