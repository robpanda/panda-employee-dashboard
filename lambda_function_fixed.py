import json
import boto3
import os
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

dynamodb = boto3.resource('dynamodb')
employees_table = dynamodb.Table(os.environ.get('EMPLOYEES_TABLE', 'panda-employees'))

def lambda_handler(event, context):
    http_method = event['httpMethod']
    path = event['path']
    
    if http_method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization,Accept',
                'Access-Control-Allow-Credentials': 'false'
            },
            'body': ''
        }
    
    if path == '/employees':
        if http_method == 'GET':
            return get_employees(event)
        elif http_method == 'POST':
            return bulk_import_employees(event)
    
    return {
        'statusCode': 404,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': 'Not found'})
    }

def get_employees(event):
    response = employees_table.scan()
    items = response['Items']
    
    for item in items:
        for key, value in item.items():
            if isinstance(value, Decimal):
                item[key] = float(value)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({'employees': items})
    }

def bulk_import_employees(event):
    try:
        body = json.loads(event['body'])
        employees_data = body.get('employees', [])
        
        print(f'BULK IMPORT: Starting import of {len(employees_data)} employees')
        
        # Delete all existing employees
        response = employees_table.scan()
        for item in response['Items']:
            employees_table.delete_item(Key={'id': item['id']})
        
        print(f'BULK IMPORT: Deleted {len(response["Items"])} existing employees')
        
        # Insert new employees
        success_count = 0
        for emp_data in employees_data:
            try:
                emp_id = emp_data.get('Employee Id', str(uuid.uuid4()))
                
                employee = {
                    'id': str(emp_id),
                    'employee_id': str(emp_id),
                    'Employee Id': str(emp_id),
                    'First Name': emp_data.get('First Name', ''),
                    'Last Name': emp_data.get('Last Name', ''),
                    'Email': emp_data.get('Email', ''),
                    'Department': emp_data.get('Department', ''),
                    'Position': emp_data.get('Position', ''),
                    'Employment Date': emp_data.get('Employment Date', ''),
                    'office': emp_data.get('office', ''),
                    'supervisor': emp_data.get('supervisor', ''),
                    'is_supervisor': emp_data.get('is_supervisor', 'No'),
                    'Terminated': emp_data.get('Terminated', 'No'),
                    'Termination Date': emp_data.get('Termination Date', ''),
                    'Phone': emp_data.get('Phone', ''),
                    'Merch Requested': '',
                    'Merch Sent': 'No',
                    'Merch Sent Date': '',
                    'Years of Service': '',
                    'updated_at': datetime.now().isoformat()
                }
                
                employees_table.put_item(Item=employee)
                success_count += 1
                
            except Exception as e:
                print(f'Error inserting employee {emp_data.get("Employee Id", "unknown")}: {e}')
        
        print(f'BULK IMPORT: Successfully imported {success_count} employees')
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': f'Successfully imported {success_count} employees',
                'imported': success_count,
                'total': len(employees_data)
            })
        }
        
    except Exception as e:
        print(f'BULK IMPORT ERROR: {e}')
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }