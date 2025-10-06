#!/usr/bin/env python3

import boto3
import json

def create_shopify_secret():
    """Create Shopify credentials in AWS Secrets Manager"""
    
    secrets_client = boto3.client('secretsmanager', region_name='us-east-2')
    
    # Shopify credentials for My Cred store
    secret_value = {
        "store": "my-cred",
        "access_token": "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",
        "api_key": "275ce2d95912e3201520211ff4ad0e62",
        "api_secret": "560b36b828895cd3600dacb17e380207"
    }
    
    try:
        # Try to create the secret
        response = secrets_client.create_secret(
            Name='shopify/my-cred',
            Description='Shopify API credentials for My Cred store - Panda Points redemption',
            SecretString=json.dumps(secret_value)
        )
        print(f"✅ Created new secret: {response['ARN']}")
        
    except secrets_client.exceptions.ResourceExistsException:
        # Secret already exists, update it
        response = secrets_client.update_secret(
            SecretId='shopify/my-cred',
            SecretString=json.dumps(secret_value)
        )
        print(f"✅ Updated existing secret: {response['ARN']}")
        
    except Exception as e:
        print(f"❌ Error managing secret: {str(e)}")
        return False
    
    return True

def update_lambda_permissions():
    """Update Lambda function to have access to Secrets Manager"""
    
    iam_client = boto3.client('iam')
    
    # Policy to allow access to the specific secret
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "secretsmanager:GetSecretValue"
                ],
                "Resource": "arn:aws:secretsmanager:us-east-2:*:secret:shopify/my-cred*"
            }
        ]
    }
    
    try:
        # Create or update the policy
        policy_name = 'PandaLambdaSecretsManagerPolicy'
        
        try:
            iam_client.create_policy(
                PolicyName=policy_name,
                PolicyDocument=json.dumps(policy_document),
                Description='Allow Lambda to access Shopify secrets'
            )
            print(f"✅ Created IAM policy: {policy_name}")
        except iam_client.exceptions.EntityAlreadyExistsException:
            print(f"ℹ️ IAM policy already exists: {policy_name}")
        
        # Attach policy to Lambda execution role
        role_name = 'panda-employee-dashboard-role'  # Adjust if different
        
        try:
            iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn=f'arn:aws:iam::679128292059:policy/{policy_name}'
            )
            print(f"✅ Attached policy to role: {role_name}")
        except Exception as e:
            print(f"⚠️ Could not attach policy to role: {e}")
            print("Please manually attach the SecretsManagerReadWrite policy to your Lambda execution role")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating Lambda permissions: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔐 Setting up Shopify credentials in AWS Secrets Manager...")
    
    secret_success = create_shopify_secret()
    permissions_success = update_lambda_permissions()
    
    if secret_success:
        print("\n✅ Shopify credentials stored securely in AWS Secrets Manager!")
        print("🔑 Secret name: shopify/my-cred")
        print("🛍️ Lambda function can now access Shopify API securely")
        
        if permissions_success:
            print("🔒 Lambda permissions updated successfully")
        else:
            print("⚠️ Please manually add SecretsManager permissions to Lambda role")
    else:
        print("\n❌ Failed to set up secrets.")