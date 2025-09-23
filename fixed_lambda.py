import json
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    print(f"Event: {json.dumps(event)}")
    
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    
    try:
        if event['httpMethod'] == 'OPTIONS':
            return {'statusCode': 200, 'headers': headers, 'body': ''}
        
        dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
        table = dynamodb.Table('panda-employees')
        
        if event['httpMethod'] == 'GET':
            print("Getting employees...")
            response = table.scan()
            print(f"Found {len(response['Items'])} items")
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'employees': response['Items']})
            }
        
        elif event['httpMethod'] == 'POST':
            print("Posting employees...")
            body = json.loads(event['body'])
            employees = body.get('employees', [])
            print(f"Received {len(employees)} employees")
            
            # Clear existing data first
            print("Clearing existing data...")
            response = table.scan()
            with table.batch_writer() as batch:
                for item in response['Items']:
                    batch.delete_item(Key={'id': item['id']})
            print(f"Cleared {len(response['Items'])} existing items")
            
            # Add new data
            count = 0
            with table.batch_writer() as batch:
                for emp in employees:
                    if 'id' not in emp:
                        emp['id'] = emp.get('employee_id', f"emp_{count}")
                    batch.put_item(Item=emp)
                    count += 1
            
            print(f"Added {count} employees")
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': f'Updated {count} employees'})
            }
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }