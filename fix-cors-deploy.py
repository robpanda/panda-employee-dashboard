#!/usr/bin/env python3

import boto3
import zipfile
import os
import json

def deploy_lambda_fix():
    """Deploy the CORS fix to the Lambda function"""
    
    # Lambda function name
    FUNCTION_NAME = 'panda-employee-dashboard'
    
    # Create a zip file with the updated lambda function
    zip_filename = 'lambda-cors-fix.zip'
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write('lambda_function.py')
    
    # Read the zip file
    with open(zip_filename, 'rb') as zip_file:
        zip_content = zip_file.read()
    
    # Initialize Lambda client
    lambda_client = boto3.client('lambda', region_name='us-east-2')
    
    try:
        # Update the function code
        response = lambda_client.update_function_code(
            FunctionName=FUNCTION_NAME,
            ZipFile=zip_content
        )
        
        print(f"✅ Successfully updated Lambda function: {FUNCTION_NAME}")
        print(f"📦 Function ARN: {response['FunctionArn']}")
        print(f"🔄 Last Modified: {response['LastModified']}")
        
        # Clean up
        os.remove(zip_filename)
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating Lambda function: {str(e)}")
        # Clean up on error
        if os.path.exists(zip_filename):
            os.remove(zip_filename)
        return False

if __name__ == "__main__":
    print("🚀 Deploying CORS fix to Lambda function...")
    success = deploy_lambda_fix()
    
    if success:
        print("\n✅ CORS fix deployed successfully!")
        print("🌐 The admin page should now work properly with pandaadmin.com")
        print("📝 Changes made:")
        print("   - Fixed CORS headers in handle_admin_users function")
        print("   - Updated CORS origin to https://www.pandaadmin.com")
        print("   - Improved error handling in admin user creation")
    else:
        print("\n❌ Deployment failed. Please check the error messages above.")