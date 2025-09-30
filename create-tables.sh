#!/bin/bash

# Create DynamoDB Tables for CRM System

echo "Creating DynamoDB tables..."

# Create Contacts Table
aws dynamodb create-table \
    --table-name panda-contacts \
    --attribute-definitions \
        AttributeName=id,AttributeType=S \
    --key-schema \
        AttributeName=id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1

# Create Collections Table
aws dynamodb create-table \
    --table-name panda-collections \
    --attribute-definitions \
        AttributeName=id,AttributeType=S \
    --key-schema \
        AttributeName=id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1

# Create Config Table
aws dynamodb create-table \
    --table-name panda-config \
    --attribute-definitions \
        AttributeName=id,AttributeType=S \
    --key-schema \
        AttributeName=id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1

echo "Tables created successfully!"
echo "Waiting for tables to become active..."

# Wait for tables to be active
aws dynamodb wait table-exists --table-name panda-contacts --region us-east-1
aws dynamodb wait table-exists --table-name panda-collections --region us-east-1
aws dynamodb wait table-exists --table-name panda-config --region us-east-1

echo "All tables are now active!"