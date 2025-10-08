import boto3
import json

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-admin-users')

def test_admin_login():
    try:
        # Get all admin users with their passwords
        response = table.scan()
        users = response['Items']
        
        print("Admin users and their passwords:")
        for user in users:
            print(f"Email: {user.get('email')}")
            print(f"Password: {user.get('password')}")
            print(f"Role: {user.get('role')}")
            print(f"Active: {user.get('active')}")
            print("---")
        
        # Test login for each user
        import requests
        
        api_url = 'https://dfu3zr3dnrvgiiwa2yu77cz5fq0rqmth.lambda-url.us-east-2.on.aws'
        
        for user in users:
            email = user.get('email')
            password = user.get('password')
            
            print(f"Testing login for {email}...")
            
            response = requests.post(f'{api_url}/admin-login', 
                json={'email': email, 'password': password},
                headers={'Content-Type': 'application/json'})
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            print("---")
        
    except Exception as e:
        print(f"❌ Error testing admin login: {str(e)}")

if __name__ == "__main__":
    test_admin_login()