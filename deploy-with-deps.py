import boto3
import zipfile
import os
import subprocess
import tempfile
import shutil

def create_deployment_package():
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Install dependencies
        subprocess.run([
            'pip', 'install', '-r', 'requirements.txt', '-t', temp_dir
        ], check=True)
        
        # Copy Lambda function
        shutil.copy('consolidated_lambda.py', os.path.join(temp_dir, 'lambda_function.py'))
        
        # Create zip file
        zip_path = 'lambda-deployment.zip'
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, temp_dir)
                    zip_file.write(file_path, arc_name)
        
        return zip_path
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)

def deploy_lambda():
    lambda_client = boto3.client('lambda', region_name='us-east-2')
    
    # Create deployment package
    zip_path = create_deployment_package()
    
    try:
        # Read the zip file
        with open(zip_path, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        # Update function code
        response = lambda_client.update_function_code(
            FunctionName='panda-employee-dashboard',
            ZipFile=zip_content
        )
        print(f"Lambda function updated: {response['FunctionArn']}")
        
        # Update configuration
        lambda_client.update_function_configuration(
            FunctionName='panda-employee-dashboard',
            Runtime='python3.9',
            Handler='lambda_function.lambda_handler',
            Timeout=30
        )
        print("Function configuration updated")
        
    finally:
        # Clean up
        if os.path.exists(zip_path):
            os.remove(zip_path)

if __name__ == "__main__":
    deploy_lambda()