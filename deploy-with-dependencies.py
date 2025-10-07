#!/usr/bin/env python3

import boto3
import zipfile
import os
import subprocess
import shutil

def deploy_lambda_with_dependencies():
    """Deploy Lambda function with requests dependency"""
    
    FUNCTION_NAME = 'panda-employee-dashboard'
    
    # Create temporary directory for dependencies
    temp_dir = 'lambda_package'
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    try:
        # Install dependencies
        print("📦 Installing dependencies...")
        subprocess.run([
            'pip3', 'install', '-r', 'requirements.txt', '-t', temp_dir
        ], check=True)
        
        # Copy Lambda function
        shutil.copy('lambda_function.py', temp_dir)
        
        # Create deployment package
        zip_filename = 'lambda-with-deps.zip'
        print("🗜️ Creating deployment package...")
        
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
        
        # Deploy to Lambda
        print("🚀 Deploying to Lambda...")
        with open(zip_filename, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        lambda_client = boto3.client('lambda', region_name='us-east-2')
        response = lambda_client.update_function_code(
            FunctionName=FUNCTION_NAME,
            ZipFile=zip_content
        )
        
        print(f"✅ Successfully deployed Lambda function with dependencies!")
        print(f"📦 Function ARN: {response['FunctionArn']}")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        os.remove(zip_filename)
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        # Cleanup on error
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        if os.path.exists(zip_filename):
            os.remove(zip_filename)
        return False

if __name__ == "__main__":
    print("🔧 Deploying Lambda function with Shopify dependencies...")
    success = deploy_lambda_with_dependencies()
    
    if success:
        print("\n✅ Deployment successful!")
        print("🎁 Shopify gift card redemption should now work correctly")
    else:
        print("\n❌ Deployment failed.")