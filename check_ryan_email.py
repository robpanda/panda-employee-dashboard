import boto3

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def check_ryan_email():
    # Check for Ryan's email
    response = table.scan(
        FilterExpression='contains(#email, :email)',
        ExpressionAttributeNames={'#email': 'Email'},
        ExpressionAttributeValues={':email': 'ryan'}
    )
    
    print(f"Found {len(response['Items'])} records containing 'ryan' in email:")
    for item in response['Items']:
        print(f"ID: {item.get('id')}")
        print(f"Name: {item.get('Name')}")
        print(f"Email: {item.get('Email')}")
        print(f"Password: {item.get('password')}")
        print("---")

if __name__ == "__main__":
    check_ryan_email()