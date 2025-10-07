import boto3

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def check_amedeo():
    try:
        # Scan for Amedeo's record
        response = table.scan(
            FilterExpression='contains(email, :email)',
            ExpressionAttributeValues={':email': 'citroamedeo9@gmail.com'}
        )
        
        if response['Items']:
            item = response['Items'][0]
            print("Found Amedeo's record:")
            for key, value in item.items():
                print(f"  {key}: {value}")
        else:
            print("No record found for citroamedeo9@gmail.com")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    check_amedeo()