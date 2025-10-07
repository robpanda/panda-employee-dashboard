#!/usr/bin/env python3

import boto3
import json

def update_shopify_secret():
    """Update the Shopify secret with correct store name"""
    
    secrets_client = boto3.client('secretsmanager', region_name='us-east-2')
    
    # Correct secret value
    secret_value = {
        "store": "pandaexteriors",
        "access_token": "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"
    }
    
    try:
        response = secrets_client.update_secret(
            SecretId='shopify/my-cred',
            SecretString=json.dumps(secret_value)
        )
        print(f"✅ Updated secret: {response['ARN']}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating secret: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Updating Shopify secret with correct store name...")
    success = update_shopify_secret()
    
    if success:
        print("✅ Secret updated successfully!")
    else:
        print("❌ Failed to update secret.")