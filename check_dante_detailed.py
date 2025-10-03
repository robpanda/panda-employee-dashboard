import boto3

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def check_dante_detailed():
    # Check for Dante's email specifically
    response = table.scan(
        FilterExpression='#email = :email',
        ExpressionAttributeNames={'#email': 'Email'},
        ExpressionAttributeValues={':email': 'Dantedjs0119@gmail.com'}
    )
    
    print(f"Found {len(response['Items'])} records for Dantedjs0119@gmail.com:")
    for item in response['Items']:
        print(f"ID: {item.get('id')}")
        print(f"Name: {item.get('Name')}")
        print(f"First Name: {item.get('First Name')}")
        print(f"Last Name: {item.get('Last Name')}")
        print(f"Email: {item.get('Email')}")
        print(f"Password: {item.get('password')}")
        print("Full record:", item)
        print("---")
    
    # Also check Ryan for comparison
    response2 = table.scan(
        FilterExpression='contains(#name, :name)',
        ExpressionAttributeNames={'#name': 'Name'},
        ExpressionAttributeValues={':name': 'Ryan'}
    )
    
    print(f"\nFound {len(response2['Items'])} records for Ryan:")
    for item in response2['Items']:
        print(f"ID: {item.get('id')}")
        print(f"Name: {item.get('Name')}")
        print(f"Email: {item.get('Email')}")
        print(f"Password: {item.get('password')}")
        print("---")

if __name__ == "__main__":
    check_dante_detailed()