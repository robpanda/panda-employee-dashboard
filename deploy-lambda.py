import boto3
import zipfile
import json
import os

def deploy_lambda():
    # Create Lambda client
    lambda_client = boto3.client('lambda', region_name='us-east-2')
    iam_client = boto3.client('iam')
    
    function_name = 'panda-employee-dashboard'
    
    # Create deployment package
    with zipfile.ZipFile('lambda-deployment.zip', 'w') as zip_file:
        zip_file.write('consolidated_lambda.py', 'lambda_function.py')
    
    # Read the zip file
    with open('lambda-deployment.zip', 'rb') as zip_file:
        zip_content = zip_file.read()
    
    try:
        # Update existing function
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        print(f"Lambda function updated: {response['FunctionArn']}")
        
        # Update function configuration
        lambda_client.update_function_configuration(
            FunctionName=function_name,
            Runtime='python3.9',
            Handler='lambda_function.lambda_handler',
            Timeout=30,
            Environment={
                'Variables': {
                    'DYNAMODB_TABLE': 'panda-employees'
                }
            }
        )
        
    except lambda_client.exceptions.ResourceNotFoundException:
        print("Function not found. Creating new function...")
        
        # Create IAM role for Lambda
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        try:
            role_response = iam_client.create_role(
                RoleName='panda-lambda-role',
                AssumeRolePolicyDocument=json.dumps(trust_policy)
            )
            role_arn = role_response['Role']['Arn']
        except iam_client.exceptions.EntityAlreadyExistsException:
            role_response = iam_client.get_role(RoleName='panda-lambda-role')
            role_arn = role_response['Role']['Arn']
        
        # Attach policies
        policies = [
            'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
            'arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess',
            'arn:aws:iam::aws:policy/AmazonSESFullAccess'
        ]
        
        for policy in policies:
            try:
                iam_client.attach_role_policy(RoleName='panda-lambda-role', PolicyArn=policy)
            except:
                pass
        
        # Create function
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.9',
            Role=role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_content},
            Timeout=30,
            Environment={
                'Variables': {
                    'DYNAMODB_TABLE': 'panda-employees'
                }
            }
        )
        print(f"Lambda function created: {response['FunctionArn']}")
    
    # Create or update function URL
    try:
        url_response = lambda_client.create_function_url_config(
            FunctionName=function_name,
            AuthType='NONE',
            Cors={
                'AllowCredentials': False,
                'AllowHeaders': ['content-type'],
                'AllowMethods': ['*'],
                'AllowOrigins': ['*'],
                'MaxAge': 86400
            }
        )
        print(f"Function URL created: {url_response['FunctionUrl']}")
    except lambda_client.exceptions.ResourceConflictException:
        # Update existing URL config
        lambda_client.update_function_url_config(
            FunctionName=function_name,
            AuthType='NONE',
            Cors={
                'AllowCredentials': False,
                'AllowHeaders': ['content-type'],
                'AllowMethods': ['*'],
                'AllowOrigins': ['*'],
                'MaxAge': 86400
            }
        )
        url_response = lambda_client.get_function_url_config(FunctionName=function_name)
        print(f"Function URL updated: {url_response['FunctionUrl']}")
    
    # Clean up
    os.remove('lambda-deployment.zip')

def create_dynamodb_table():
    dynamodb = boto3.client('dynamodb', region_name='us-east-2')
    
    try:
        response = dynamodb.create_table(
            TableName='panda-employees',
            KeySchema=[
                {'AttributeName': 'last_name', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'last_name', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"DynamoDB table created: {response['TableDescription']['TableArn']}")
    except dynamodb.exceptions.ResourceInUseException:
        print("DynamoDB table already exists")

if __name__ == "__main__":
    create_dynamodb_table()
    deploy_lambda()