#!/usr/bin/env python3
import boto3
import zipfile
import os

def deploy_lambda():
    # Create zip file
    with zipfile.ZipFile('lambda_function.zip', 'w') as zip_file:
        zip_file.write('lambda_function.py')
    
    # Update Lambda function
    lambda_client = boto3.client('lambda', region_name='us-east-2')
    
    with open('lambda_function.zip', 'rb') as zip_file:
        lambda_client.update_function_code(
            FunctionName='panda-employee-dashboard',
            ZipFile=zip_file.read()
        )
    
    print("Lambda function updated successfully!")
    
    # Clean up
    os.remove('lambda_function.zip')

if __name__ == "__main__":
    deploy_lambda()