#!/bin/bash

echo "Creating DynamoDB tables for Fleet Management..."

# Create Vehicles Table
echo "Creating panda-fleet-vehicles table..."
aws dynamodb create-table \
    --table-name panda-fleet-vehicles \
    --attribute-definitions \
        AttributeName=vehicle_id,AttributeType=S \
        AttributeName=driver_email,AttributeType=S \
        AttributeName=status,AttributeType=S \
    --key-schema \
        AttributeName=vehicle_id,KeyType=HASH \
    --global-secondary-indexes \
        "IndexName=driver_email-index,KeySchema=[{AttributeName=driver_email,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}" \
        "IndexName=status-index,KeySchema=[{AttributeName=status,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}" \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region us-east-2

echo "Waiting for panda-fleet-vehicles table to be active..."
aws dynamodb wait table-exists --table-name panda-fleet-vehicles --region us-east-2

# Create Accidents Table
echo "Creating panda-fleet-accidents table..."
aws dynamodb create-table \
    --table-name panda-fleet-accidents \
    --attribute-definitions \
        AttributeName=accident_id,AttributeType=S \
        AttributeName=vehicle_id,AttributeType=S \
        AttributeName=status,AttributeType=S \
    --key-schema \
        AttributeName=accident_id,KeyType=HASH \
    --global-secondary-indexes \
        "IndexName=vehicle_id-index,KeySchema=[{AttributeName=vehicle_id,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}" \
        "IndexName=status-index,KeySchema=[{AttributeName=status,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}" \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region us-east-2

echo "Waiting for panda-fleet-accidents table to be active..."
aws dynamodb wait table-exists --table-name panda-fleet-accidents --region us-east-2

# Create EZ Pass Table
echo "Creating panda-fleet-ezpass table..."
aws dynamodb create-table \
    --table-name panda-fleet-ezpass \
    --attribute-definitions \
        AttributeName=ezpass_id,AttributeType=S \
        AttributeName=vehicle_id,AttributeType=S \
        AttributeName=status,AttributeType=S \
    --key-schema \
        AttributeName=ezpass_id,KeyType=HASH \
    --global-secondary-indexes \
        "IndexName=vehicle_id-index,KeySchema=[{AttributeName=vehicle_id,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}" \
        "IndexName=status-index,KeySchema=[{AttributeName=status,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}" \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region us-east-2

echo "Waiting for panda-fleet-ezpass table to be active..."
aws dynamodb wait table-exists --table-name panda-fleet-ezpass --region us-east-2

# Create Sales Table
echo "Creating panda-fleet-sales table..."
aws dynamodb create-table \
    --table-name panda-fleet-sales \
    --attribute-definitions \
        AttributeName=sale_id,AttributeType=S \
        AttributeName=vehicle_id,AttributeType=S \
    --key-schema \
        AttributeName=sale_id,KeyType=HASH \
    --global-secondary-indexes \
        "IndexName=vehicle_id-index,KeySchema=[{AttributeName=vehicle_id,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}" \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region us-east-2

echo "Waiting for panda-fleet-sales table to be active..."
aws dynamodb wait table-exists --table-name panda-fleet-sales --region us-east-2

# Create Maintenance Table
echo "Creating panda-fleet-maintenance table..."
aws dynamodb create-table \
    --table-name panda-fleet-maintenance \
    --attribute-definitions \
        AttributeName=maintenance_id,AttributeType=S \
        AttributeName=vehicle_id,AttributeType=S \
        AttributeName=status,AttributeType=S \
    --key-schema \
        AttributeName=maintenance_id,KeyType=HASH \
    --global-secondary-indexes \
        "IndexName=vehicle_id-index,KeySchema=[{AttributeName=vehicle_id,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}" \
        "IndexName=status-index,KeySchema=[{AttributeName=status,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}" \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region us-east-2

echo "Waiting for panda-fleet-maintenance table to be active..."
aws dynamodb wait table-exists --table-name panda-fleet-maintenance --region us-east-2

# Create Requests Table
echo "Creating panda-fleet-requests table..."
aws dynamodb create-table \
    --table-name panda-fleet-requests \
    --attribute-definitions \
        AttributeName=request_id,AttributeType=S \
        AttributeName=requester_email,AttributeType=S \
        AttributeName=status,AttributeType=S \
    --key-schema \
        AttributeName=request_id,KeyType=HASH \
    --global-secondary-indexes \
        "IndexName=requester_email-index,KeySchema=[{AttributeName=requester_email,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}" \
        "IndexName=status-index,KeySchema=[{AttributeName=status,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}" \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region us-east-2

echo "Waiting for panda-fleet-requests table to be active..."
aws dynamodb wait table-exists --table-name panda-fleet-requests --region us-east-2

echo ""
echo "✅ All Fleet Management tables created successfully!"
echo ""
echo "Tables created:"
echo "  - panda-fleet-vehicles"
echo "  - panda-fleet-accidents"
echo "  - panda-fleet-ezpass"
echo "  - panda-fleet-sales"
echo "  - panda-fleet-maintenance"
echo "  - panda-fleet-requests"
