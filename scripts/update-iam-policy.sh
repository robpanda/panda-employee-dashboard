#!/bin/bash

# Update IAM policy for panda-deployment-user
USER_NAME="panda-deployment-user"
POLICY_NAME="PandaDeploymentPolicy"

echo "🔐 Updating IAM policy for $USER_NAME..."

# Delete existing policy if it exists
aws iam delete-user-policy --user-name $USER_NAME --policy-name $POLICY_NAME 2>/dev/null

# Apply new policy
aws iam put-user-policy \
    --user-name $USER_NAME \
    --policy-name $POLICY_NAME \
    --policy-document file://config/iam-policy-updated.json

if [ $? -eq 0 ]; then
    echo "✅ IAM policy updated successfully!"
    echo "You can now run ./scripts/setup-route53.sh"
else
    echo "❌ Failed to update IAM policy"
    exit 1
fi