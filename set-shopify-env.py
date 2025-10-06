#!/usr/bin/env python3

import boto3

def set_shopify_environment_variables():
    """Set Shopify environment variables in Lambda function"""
    
    FUNCTION_NAME = 'panda-employee-dashboard'
    
    lambda_client = boto3.client('lambda', region_name='us-east-2')
    
    try:
        # Get current function configuration
        response = lambda_client.get_function_configuration(FunctionName=FUNCTION_NAME)
        
        # Update environment variables
        current_env = response.get('Environment', {}).get('Variables', {})
        current_env.update({
            'SHOPIFY_STORE': 'my-cred',
            'SHOPIFY_ACCESS_TOKEN': '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'
        })
        
        # Update function configuration
        lambda_client.update_function_configuration(
            FunctionName=FUNCTION_NAME,
            Environment={'Variables': current_env}
        )
        
        print(f"✅ Successfully updated environment variables for {FUNCTION_NAME}")
        print("🔐 Shopify credentials are now securely stored as environment variables")
        return True
        
    except Exception as e:
        print(f"❌ Error updating environment variables: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Setting Shopify environment variables...")
    success = set_shopify_environment_variables()
    
    if success:
        print("\n✅ Environment variables set successfully!")
        print("🛍️ Shopify gift card redemption is ready to use")
    else:
        print("\n❌ Failed to set environment variables.")