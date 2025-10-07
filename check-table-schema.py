import boto3

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def check_schema():
    try:
        # Get table description
        table_info = table.meta.client.describe_table(TableName='panda-employees')
        
        print("Table Schema:")
        print(f"Table Name: {table_info['Table']['TableName']}")
        
        key_schema = table_info['Table']['KeySchema']
        print("Key Schema:")
        for key in key_schema:
            print(f"  {key['AttributeName']} ({key['KeyType']})")
            
        attributes = table_info['Table']['AttributeDefinitions']
        print("Attribute Definitions:")
        for attr in attributes:
            print(f"  {attr['AttributeName']}: {attr['AttributeType']}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    check_schema()