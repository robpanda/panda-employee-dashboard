import boto3

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def check_drjwoo():
    try:
        # Scan for drjwoo88@gmail.com
        response = table.scan(
            FilterExpression='contains(email, :email)',
            ExpressionAttributeValues={
                ':email': 'drjwoo88@gmail.com'
            }
        )
        
        if response['Items']:
            employee = response['Items'][0]
            print(f"✅ Found employee: {employee.get('first_name', 'N/A')} {employee.get('last_name', 'N/A')}")
            print(f"   ID: {employee.get('id', 'N/A')}")
            print(f"   Email: {employee.get('email', 'N/A')}")
            print(f"   Title: {employee.get('title', 'N/A')}")
            print(f"   Points Manager: {employee.get('points_manager', 'No')}")
            print(f"   Password: {employee.get('password', 'Not set')}")
            return employee
        else:
            print("❌ Employee drjwoo88@gmail.com not found in database")
            return None
            
    except Exception as e:
        print(f"❌ Error checking employee: {str(e)}")
        return None

if __name__ == "__main__":
    check_drjwoo()