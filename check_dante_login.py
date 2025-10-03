import boto3
import json

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def check_dante():
    # Scan for Dante's records
    response = table.scan(
        FilterExpression='contains(#name, :name)',
        ExpressionAttributeNames={'#name': 'Name'},
        ExpressionAttributeValues={':name': 'Dante'}
    )
    
    print(f"Found {len(response['Items'])} records for Dante:")
    for item in response['Items']:
        print(f"ID: {item.get('id')}")
        print(f"Name: {item.get('Name')}")
        print(f"Email: {item.get('Email')}")
        print(f"Password: {item.get('password', 'No password field')}")
        print("---")

if __name__ == "__main__":
    check_dante()