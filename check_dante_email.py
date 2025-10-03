import boto3
import json

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def check_dante_email():
    # Scan for Dante's email
    response = table.scan(
        FilterExpression='contains(#email, :email)',
        ExpressionAttributeNames={'#email': 'Email'},
        ExpressionAttributeValues={':email': 'Dantedjs0119@gmail.com'}
    )
    
    print(f"Found {len(response['Items'])} records for Dantedjs0119@gmail.com:")
    for item in response['Items']:
        print(f"ID: {item.get('id')}")
        print(f"Name: {item.get('Name')}")
        print(f"Email: {item.get('Email')}")
        print(f"Password: {item.get('password', 'No password field')}")
        print("---")

if __name__ == "__main__":
    check_dante_email()