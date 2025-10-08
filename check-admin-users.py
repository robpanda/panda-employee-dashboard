import boto3

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-admin-users')

def check_admin_users():
    try:
        response = table.scan()
        users = response['Items']
        
        print(f"Found {len(users)} admin users:")
        for user in users:
            print(f"Email: {user.get('email')}")
            print(f"Role: {user.get('role')}")
            print(f"Active: {user.get('active')}")
            print(f"Password set: {'Yes' if user.get('password') else 'No'}")
            print(f"Permissions: {user.get('permissions', [])}")
            print("---")
        
    except Exception as e:
        print(f"❌ Error checking admin users: {str(e)}")

if __name__ == "__main__":
    check_admin_users()