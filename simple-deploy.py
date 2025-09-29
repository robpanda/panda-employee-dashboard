import boto3
import zipfile
import json

# Create simple deployment package
with zipfile.ZipFile('lambda-deployment.zip', 'w') as zip_file:
    zip_file.write('consolidated_lambda.py', 'lambda_function.py')

# Deploy to Lambda
lambda_client = boto3.client('lambda', region_name='us-east-2')

with open('lambda-deployment.zip', 'rb') as zip_file:
    zip_content = zip_file.read()

try:
    response = lambda_client.update_function_code(
        FunctionName='panda-employee-dashboard',
        ZipFile=zip_content
    )
    print(f"Lambda function updated: {response['FunctionArn']}")
    
    # Test the function
    test_event = {
        'httpMethod': 'GET',
        'path': '/employees',
        'headers': {},
        'body': None
    }
    
    test_response = lambda_client.invoke(
        FunctionName='panda-employee-dashboard',
        Payload=json.dumps(test_event)
    )
    
    result = json.loads(test_response['Payload'].read())
    print(f"Test result: {result}")
    
except Exception as e:
    print(f"Error: {e}")

# Clean up
import os
os.remove('lambda-deployment.zip')