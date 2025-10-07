import boto3

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def list_employees():
    try:
        response = table.scan()
        items = response['Items']
        
        print(f"Found {len(items)} employees:")
        for item in items:
            email = item.get('email', 'No email')
            name = item.get('name', 'No name')
            print(f"  {name} - {email}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    list_employees()