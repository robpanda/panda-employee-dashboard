import boto3

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def debug_drjwoo():
    try:
        # Scan for drjwoo88@gmail.com with exact match
        response = table.scan()
        
        print("All employees with gmail addresses:")
        for item in response['Items']:
            email = item.get('Email', item.get('email', ''))
            if 'gmail' in email.lower():
                print(f"  Email: '{email}' (length: {len(email)})")
                print(f"  Points Manager: {item.get('points_manager', 'No')}")
                print(f"  Password: {item.get('password', 'Not set')}")
                print(f"  ID: {item.get('id')}")
                print("  ---")
        
        # Try exact search
        response2 = table.scan(
            FilterExpression='Email = :email',
            ExpressionAttributeValues={
                ':email': 'drjwoo88@gmail.com'
            }
        )
        
        print(f"\nExact search results: {len(response2['Items'])} items")
        for item in response2['Items']:
            print(f"Found: {item}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    debug_drjwoo()