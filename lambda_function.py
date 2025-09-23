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
    
    try:
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
        elif http_method == 'GET' and path == '/employees':
            return get_employees(event)
        elif http_method == 'POST' and path == '/employees':
            return create_employee(event)
        elif http_method == 'PUT' and '/employees/' in path:
            return update_employee(event)
        elif http_method == 'DELETE' and '/employees/' in path:
            return delete_employee(event)
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization'
                },
                'body': json.dumps({'error': 'Not found'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization'
            },
            'body': json.dumps({'error': str(e)})
        }

def get_employees(event):
    query_params = event.get('queryStringParameters') or {}
    
    if 'email' in query_params:
        # Search by email
        response = employees_table.query(
            IndexName='email-index',
            KeyConditionExpression='Email = :email',
            ExpressionAttributeValues={':email': query_params['email']}
        )
        items = response['Items']
    else:
        # Get all employees
        response = employees_table.scan()
        items = response['Items']
    
    # Convert Decimal to float for JSON serialization and ensure consistent field names
    for item in items:
        for key, value in item.items():
            if isinstance(value, Decimal):
                item[key] = float(value)
        
        # Ensure employee_id exists
        if 'employee_id' not in item and 'id' in item:
            item['employee_id'] = item['id']
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization'
        },
        'body': json.dumps({'employees': items})
    }

def create_employee(event):
    body = json.loads(event['body'])
    
    # Handle bulk employee data
    if 'employees' in body:
        employees_data = body['employees']
        
        # Clear existing data and insert new
        response = employees_table.scan()
        with employees_table.batch_writer() as batch:
            for item in response['Items']:
                batch.delete_item(Key={'id': item.get('id', item.get('employee_id', ''))})
        
        # Insert new employees
        with employees_table.batch_writer() as batch:
            for emp_data in employees_data:
                # Handle both frontend format and API format
                employee = {
                    'id': emp_data.get('employee_id', emp_data.get('id', str(uuid.uuid4()))),
                    'employee_id': emp_data.get('employee_id', emp_data.get('id', str(uuid.uuid4()))),
                    'First Name': emp_data.get('First Name', emp_data.get('first_name', '')),
                    'Last Name': emp_data.get('Last Name', emp_data.get('last_name', '')),
                    'Department': emp_data.get('Department', emp_data.get('department', '')),
                    'Position': emp_data.get('Position', emp_data.get('position', '')),
                    'Employment Date': emp_data.get('Employment Date', emp_data.get('employment_date', '')),
                    'Years of Service': emp_data.get('Years of Service', emp_data.get('years_of_service', '')),
                    'Email': emp_data.get('Email', emp_data.get('email', '')),
                    'Phone': emp_data.get('Phone', emp_data.get('phone', '')),
                    'Merch Requested': emp_data.get('Merch Requested', emp_data.get('merch_requested', '')),
                    'Merch Sent': emp_data.get('Merch Sent', emp_data.get('merch_sent', 'No')),
                    'Merch Sent Date': emp_data.get('Merch Sent Date', emp_data.get('merch_sent_date', '')),
                    'Terminated': emp_data.get('Terminated', emp_data.get('terminated', 'No')),
                    'Termination Date': emp_data.get('Termination Date', emp_data.get('termination_date', '')),
                    'updated_at': datetime.now().isoformat()
                }
                batch.put_item(Item=employee)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization'
            },
            'body': json.dumps({'message': f'{len(employees_data)} employees saved successfully'})
        }
    
    # Handle single employee
    employee_id = str(uuid.uuid4())
    current_date = datetime.now().isoformat()
    
    employee = {
        'id': employee_id,
        'employee_id': employee_id,
        'last_name': body['last_name'],
        'first_name': body['first_name'],
        'email': body['email'],
        'employment_date': body.get('employment_date', current_date),
        'terminated': body.get('terminated', 'No'),
        'updated_at': current_date
    }
    
    employees_table.put_item(Item=employee)
    
    return {
        'statusCode': 201,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization'
        },
        'body': json.dumps({'employee_id': employee_id, 'message': 'Employee created successfully'})
    }

def update_employee(event):
    # Extract employee ID from path
    path_parts = event['path'].split('/')
    employee_id = path_parts[-1]  # Get last part of path
    body = json.loads(event['body'])
    
    # Get existing employee
    response = employees_table.get_item(Key={'employee_id': employee_id})
    if 'Item' not in response:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Employee not found'})
        }
    
    employee = response['Item']
    
    # Update fields
    for key, value in body.items():
        if key != 'employee_id':  # Don't allow updating the primary key
            employee[key] = value
    
    # Recalculate days employed and years worked if employment_date changed
    if 'employment_date' in body or 'registration_date' in body:
        employment_date = body.get('employment_date', body.get('registration_date', employee.get('employment_date')))
        employment_datetime = datetime.fromisoformat(employment_date)
        days_employed = (datetime.now() - employment_datetime).days
        years_worked = round(days_employed / 365.25, 1)
        employee['employment_date'] = employment_date
        employee['days_employed'] = days_employed
        employee['years_worked'] = years_worked
    
    employee['updated_at'] = datetime.now().isoformat()
    
    employees_table.put_item(Item=employee)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization'
        },
        'body': json.dumps({'message': 'Employee updated successfully'})
    }

def delete_employee(event):
    employee_id = event['pathParameters']['employee_id']
    
    employees_table.delete_item(Key={'employee_id': employee_id})
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization'
        },
        'body': json.dumps({'message': 'Employee deleted successfully'})
    }