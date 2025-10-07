import boto3
import zipfile
import os

def deploy_lambda():
    # Create a zip file with the lambda function
    with zipfile.ZipFile('lambda_function.zip', 'w') as zip_file:
        zip_file.write('lambda_function.py')
    
    # Update the Lambda function
    lambda_client = boto3.client('lambda', region_name='us-east-2')
    
    try:
        with open('lambda_function.zip', 'rb') as zip_file:
            response = lambda_client.update_function_code(
                FunctionName='panda-employee-api',  # Replace with actual function name
                ZipFile=zip_file.read()
            )
        
        print("✅ Lambda function updated successfully!")
        print(f"   Version: {response.get('Version')}")
        print(f"   Last Modified: {response.get('LastModified')}")
        
    except Exception as e:
        print(f"❌ Error updating Lambda function: {str(e)}")
        print("   You may need to update the function manually in AWS Console")
    
    # Clean up
    if os.path.exists('lambda_function.zip'):
        os.remove('lambda_function.zip')

if __name__ == "__main__":
    deploy_lambda()