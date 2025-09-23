import json
import boto3

def lambda_handler(event, context):
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
        table = dynamodb.Table('panda-employees')
        
        if event['httpMethod'] == 'GET':
            response = table.scan()
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps({'employees': response['Items']})
            }
        
        elif event['httpMethod'] == 'POST':
            body = json.loads(event['body'])
            employees = body.get('employees', [])
            
            # Update existing data without clearing
            with table.batch_writer() as batch:
                for emp in employees:
                    # Ensure each employee has an id
                    if 'id' not in emp and 'employee_id' in emp:
                        emp['id'] = emp['employee_id']
                    elif 'id' not in emp:
                        emp['id'] = emp.get('Email', str(hash(emp.get('First Name', '') + emp.get('Last Name', ''))))
                    batch.put_item(Item=emp)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps({'message': 'Success'})
            }
        
        elif event['httpMethod'] == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': ''
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }