#!/bin/bash

# Create IAM role for Lambda with DynamoDB access

ROLE_NAME="lambda-dynamodb-role"
REGION="us-east-2"

echo "Creating IAM role for Lambda..."

# Create trust policy
cat > /tmp/lambda-trust-policy.json <<EOF
{
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
}
EOF

# Create the role
aws iam create-role \
    --role-name $ROLE_NAME \
    --assume-role-policy-document file:///tmp/lambda-trust-policy.json

# Attach AWS managed policies
echo "Attaching policies..."
aws iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

# Create inline policy for specific DynamoDB tables
cat > /tmp/dynamodb-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": [
        "arn:aws:dynamodb:us-east-2:679128292059:table/panda-advocates",
        "arn:aws:dynamodb:us-east-2:679128292059:table/panda-advocates/index/*",
        "arn:aws:dynamodb:us-east-2:679128292059:table/panda-sales-reps",
        "arn:aws:dynamodb:us-east-2:679128292059:table/panda-sales-reps/index/*",
        "arn:aws:dynamodb:us-east-2:679128292059:table/panda-sales-managers",
        "arn:aws:dynamodb:us-east-2:679128292059:table/panda-sales-managers/index/*",
        "arn:aws:dynamodb:us-east-2:679128292059:table/panda-referral-leads",
        "arn:aws:dynamodb:us-east-2:679128292059:table/panda-referral-leads/index/*",
        "arn:aws:dynamodb:us-east-2:679128292059:table/panda-referral-payouts",
        "arn:aws:dynamodb:us-east-2:679128292059:table/panda-referral-payouts/index/*"
      ]
    }
  ]
}
EOF

aws iam put-role-policy \
    --role-name $ROLE_NAME \
    --policy-name ReferralDynamoDBAccess \
    --policy-document file:///tmp/dynamodb-policy.json

echo "Waiting for role to be available..."
sleep 10

ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)

echo ""
echo "✅ Role created successfully!"
echo "Role ARN: $ROLE_ARN"

# Cleanup
rm -f /tmp/lambda-trust-policy.json /tmp/dynamodb-policy.json
