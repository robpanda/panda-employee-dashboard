import boto3

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def fix_dante_name():
    # Update Dante's record with proper name
    response = table.update_item(
        Key={'id': '10730'},
        UpdateExpression='SET #name = :name',
        ExpressionAttributeNames={'#name': 'Name'},
        ExpressionAttributeValues={':name': 'Dante Snow'},
        ReturnValues='UPDATED_NEW'
    )
    
    print(f"Updated Dante's record: {response['Attributes']}")

if __name__ == "__main__":
    fix_dante_name()