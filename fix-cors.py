import boto3
import time

lambda_client = boto3.client('lambda', region_name='us-east-2')
function_name = 'panda-employee-dashboard'

# Wait for function to be ready
print("Waiting for function to be ready...")
time.sleep(10)

try:
    # Update function URL config
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
    
    # Get the URL
    url_response = lambda_client.get_function_url_config(FunctionName=function_name)
    print(f"Function URL configured: {url_response['FunctionUrl']}")
    
except Exception as e:
    print(f"Error: {e}")
    # Try creating if it doesn't exist
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
    except Exception as e2:
        print(f"Failed to create URL: {e2}")