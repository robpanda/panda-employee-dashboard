#!/bin/bash

# Create DynamoDB tables for GTR replacement referral system

echo "Creating referral system tables..."

# 1. Sales Managers table
echo "Creating sales-managers table..."
aws dynamodb create-table \
    --table-name panda-sales-managers \
    --attribute-definitions \
        AttributeName=managerId,AttributeType=S \
        AttributeName=email,AttributeType=S \
    --key-schema \
        AttributeName=managerId,KeyType=HASH \
    --global-secondary-indexes \
        "[{
            \"IndexName\": \"email-index\",
            \"KeySchema\": [{\"AttributeName\": \"email\", \"KeyType\": \"HASH\"}],
            \"Projection\": {\"ProjectionType\": \"ALL\"},
            \"ProvisionedThroughput\": {\"ReadCapacityUnits\": 5, \"WriteCapacityUnits\": 5}
        }]" \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region us-east-2

# 2. Sales Reps table
echo "Creating sales-reps table..."
aws dynamodb create-table \
    --table-name panda-sales-reps \
    --attribute-definitions \
        AttributeName=repId,AttributeType=S \
        AttributeName=managerId,AttributeType=S \
        AttributeName=email,AttributeType=S \
    --key-schema \
        AttributeName=repId,KeyType=HASH \
    --global-secondary-indexes \
        "[{
            \"IndexName\": \"manager-index\",
            \"KeySchema\": [{\"AttributeName\": \"managerId\", \"KeyType\": \"HASH\"}],
            \"Projection\": {\"ProjectionType\": \"ALL\"},
            \"ProvisionedThroughput\": {\"ReadCapacityUnits\": 5, \"WriteCapacityUnits\": 5}
        },
        {
            \"IndexName\": \"email-index\",
            \"KeySchema\": [{\"AttributeName\": \"email\", \"KeyType\": \"HASH\"}],
            \"Projection\": {\"ProjectionType\": \"ALL\"},
            \"ProvisionedThroughput\": {\"ReadCapacityUnits\": 5, \"WriteCapacityUnits\": 5}
        }]" \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region us-east-2

# 3. Advocates table
echo "Creating advocates table..."
aws dynamodb create-table \
    --table-name panda-advocates \
    --attribute-definitions \
        AttributeName=advocateId,AttributeType=S \
        AttributeName=repId,AttributeType=S \
        AttributeName=email,AttributeType=S \
        AttributeName=referralCode,AttributeType=S \
    --key-schema \
        AttributeName=advocateId,KeyType=HASH \
    --global-secondary-indexes \
        "[{
            \"IndexName\": \"rep-index\",
            \"KeySchema\": [{\"AttributeName\": \"repId\", \"KeyType\": \"HASH\"}],
            \"Projection\": {\"ProjectionType\": \"ALL\"},
            \"ProvisionedThroughput\": {\"ReadCapacityUnits\": 5, \"WriteCapacityUnits\": 5}
        },
        {
            \"IndexName\": \"email-index\",
            \"KeySchema\": [{\"AttributeName\": \"email\", \"KeyType\": \"HASH\"}],
            \"Projection\": {\"ProjectionType\": \"ALL\"},
            \"ProvisionedThroughput\": {\"ReadCapacityUnits\": 5, \"WriteCapacityUnits\": 5}
        },
        {
            \"IndexName\": \"referralCode-index\",
            \"KeySchema\": [{\"AttributeName\": \"referralCode\", \"KeyType\": \"HASH\"}],
            \"Projection\": {\"ProjectionType\": \"ALL\"},
            \"ProvisionedThroughput\": {\"ReadCapacityUnits\": 5, \"WriteCapacityUnits\": 5}
        }]" \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region us-east-2

# 4. Leads table
echo "Creating leads table..."
aws dynamodb create-table \
    --table-name panda-referral-leads \
    --attribute-definitions \
        AttributeName=leadId,AttributeType=S \
        AttributeName=advocateId,AttributeType=S \
        AttributeName=repId,AttributeType=S \
        AttributeName=status,AttributeType=S \
        AttributeName=createdAt,AttributeType=N \
    --key-schema \
        AttributeName=leadId,KeyType=HASH \
    --global-secondary-indexes \
        "[{
            \"IndexName\": \"advocate-index\",
            \"KeySchema\": [
                {\"AttributeName\": \"advocateId\", \"KeyType\": \"HASH\"},
                {\"AttributeName\": \"createdAt\", \"KeyType\": \"RANGE\"}
            ],
            \"Projection\": {\"ProjectionType\": \"ALL\"},
            \"ProvisionedThroughput\": {\"ReadCapacityUnits\": 5, \"WriteCapacityUnits\": 5}
        },
        {
            \"IndexName\": \"rep-index\",
            \"KeySchema\": [
                {\"AttributeName\": \"repId\", \"KeyType\": \"HASH\"},
                {\"AttributeName\": \"createdAt\", \"KeyType\": \"RANGE\"}
            ],
            \"Projection\": {\"ProjectionType\": \"ALL\"},
            \"ProvisionedThroughput\": {\"ReadCapacityUnits\": 5, \"WriteCapacityUnits\": 5}
        },
        {
            \"IndexName\": \"status-index\",
            \"KeySchema\": [
                {\"AttributeName\": \"status\", \"KeyType\": \"HASH\"},
                {\"AttributeName\": \"createdAt\", \"KeyType\": \"RANGE\"}
            ],
            \"Projection\": {\"ProjectionType\": \"ALL\"},
            \"ProvisionedThroughput\": {\"ReadCapacityUnits\": 5, \"WriteCapacityUnits\": 5}
        }]" \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region us-east-2

# 5. Payouts table
echo "Creating payouts table..."
aws dynamodb create-table \
    --table-name panda-referral-payouts \
    --attribute-definitions \
        AttributeName=payoutId,AttributeType=S \
        AttributeName=advocateId,AttributeType=S \
        AttributeName=leadId,AttributeType=S \
        AttributeName=status,AttributeType=S \
        AttributeName=createdAt,AttributeType=N \
    --key-schema \
        AttributeName=payoutId,KeyType=HASH \
    --global-secondary-indexes \
        "[{
            \"IndexName\": \"advocate-index\",
            \"KeySchema\": [
                {\"AttributeName\": \"advocateId\", \"KeyType\": \"HASH\"},
                {\"AttributeName\": \"createdAt\", \"KeyType\": \"RANGE\"}
            ],
            \"Projection\": {\"ProjectionType\": \"ALL\"},
            \"ProvisionedThroughput\": {\"ReadCapacityUnits\": 5, \"WriteCapacityUnits\": 5}
        },
        {
            \"IndexName\": \"lead-index\",
            \"KeySchema\": [{\"AttributeName\": \"leadId\", \"KeyType\": \"HASH\"}],
            \"Projection\": {\"ProjectionType\": \"ALL\"},
            \"ProvisionedThroughput\": {\"ReadCapacityUnits\": 5, \"WriteCapacityUnits\": 5}
        },
        {
            \"IndexName\": \"status-index\",
            \"KeySchema\": [
                {\"AttributeName\": \"status\", \"KeyType\": \"HASH\"},
                {\"AttributeName\": \"createdAt\", \"KeyType\": \"RANGE\"}
            ],
            \"Projection\": {\"ProjectionType\": \"ALL\"},
            \"ProvisionedThroughput\": {\"ReadCapacityUnits\": 5, \"WriteCapacityUnits\": 5}
        }]" \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region us-east-2

echo "Waiting for tables to be created..."
aws dynamodb wait table-exists --table-name panda-sales-managers --region us-east-2
aws dynamodb wait table-exists --table-name panda-sales-reps --region us-east-2
aws dynamodb wait table-exists --table-name panda-advocates --region us-east-2
aws dynamodb wait table-exists --table-name panda-referral-leads --region us-east-2
aws dynamodb wait table-exists --table-name panda-referral-payouts --region us-east-2

echo "✅ All tables created successfully!"
