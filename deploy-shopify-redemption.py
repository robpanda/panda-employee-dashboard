#!/usr/bin/env python3

import boto3
import zipfile
import os

def deploy_shopify_redemption():
    """Deploy the Shopify gift card redemption functionality"""
    
    FUNCTION_NAME = 'panda-employee-dashboard'
    zip_filename = 'lambda-shopify-redemption.zip'
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write('lambda_function.py')
    
    with open(zip_filename, 'rb') as zip_file:
        zip_content = zip_file.read()
    
    lambda_client = boto3.client('lambda', region_name='us-east-2')
    
    try:
        response = lambda_client.update_function_code(
            FunctionName=FUNCTION_NAME,
            ZipFile=zip_content
        )
        
        print(f"✅ Successfully updated Lambda function: {FUNCTION_NAME}")
        print(f"🎁 Shopify gift card redemption is now active!")
        
        os.remove(zip_filename)
        return True
        
    except Exception as e:
        print(f"❌ Error updating Lambda function: {str(e)}")
        if os.path.exists(zip_filename):
            os.remove(zip_filename)
        return False

if __name__ == "__main__":
    print("🚀 Deploying Shopify gift card redemption...")
    success = deploy_shopify_redemption()
    
    if success:
        print("\n✅ Shopify redemption deployed successfully!")
        print("🛍️ Employees can now redeem points for My Cred gift cards")
        print("💳 Gift cards will be created in the My Cred Shopify store")
    else:
        print("\n❌ Deployment failed.")