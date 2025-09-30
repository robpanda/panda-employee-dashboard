# CRM API Deployment Guide

## Step 1: Create DynamoDB Tables
```bash
./create-tables.sh
```

## Step 2: Update Lambda Function
1. Find your existing Lambda function name in AWS Console
2. Edit `update-lambda.sh` and replace `your-existing-lambda-function-name`
3. Run:
```bash
./update-lambda.sh
```

## Step 3: Get API Gateway URL
```bash
aws apigateway get-rest-apis --query 'items[].{id:id,name:name}' --output table
```

## Step 4: Update Frontend
1. Copy your API Gateway URL from step 3
2. Update `leads.html` line with your actual URL:
```javascript
const API_BASE = 'https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/prod';
```
3. Set `MOCK_MODE = false`

## Step 5: Test API
1. Update `test-api.sh` with your API URL
2. Run:
```bash
./test-api.sh
```

## Quick Setup (if you know your Lambda function name):
```bash
# Replace 'your-lambda-name' with actual name
sed -i 's/your-existing-lambda-function-name/your-lambda-name/g' update-lambda.sh

# Run all setup
./create-tables.sh && ./update-lambda.sh
```

## Troubleshooting:
- **Permission errors**: Ensure Lambda has DynamoDB permissions
- **CORS errors**: Check API Gateway CORS settings
- **404 errors**: Verify API Gateway routes include new endpoints

Your CRM system will be live once these steps are complete!