import json
import boto3
import csv
import io
import requests
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('panda-employees')

def lambda_handler(event, context):
    try:
        # Handle CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                }
            }
        
        path = event.get('path', '')
        method = event.get('httpMethod', 'GET')
        
        if path == '/employees' and method == 'GET':
            return get_employees()
        elif path == '/import' and method == 'POST':
            return import_employees()
        else:
            return {
                'statusCode': 404,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Not found'})
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }

def get_employees():
    response = table.scan()
    employees = response['Items']
    
    # Convert Decimal to float for JSON serialization
    for employee in employees:
        for key, value in employee.items():
            if isinstance(value, Decimal):
                employee[key] = float(value)
    
    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps(employees)
    }

def import_employees():
    try:
        # Google Sheets CSV URL
        sheet_url = "https://docs.google.com/spreadsheets/d/1OIWKKr527C1-E6H4fj71c_5Mq6kJev7ZjkgV_71XiRc/export?format=csv"
        
        response = requests.get(sheet_url)
        csv_content = response.text
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        imported_count = 0
        updated_count = 0
        
        for row in csv_reader:
            if not row.get('Last Name'):
                continue
                
            employee_data = {
                'last_name': row.get('Last Name', '').strip(),
                'first_name': row.get('First Name', '').strip(),
                'name': f"{row.get('First Name', '').strip()} {row.get('Last Name', '').strip()}",
                'employee_id': row.get('Employee ID', '').strip(),
                'role': row.get('Role', '').strip(),
                'supervisor': row.get('Supervisor', '').strip(),
                'office': row.get('Office', '').strip(),
                'department': row.get('Department', '').strip(),
                'hire_date': row.get('Hire Date', '').strip(),
                'phone': row.get('Phone', '').strip(),
                'email': f"{row.get('First Name', '').strip().lower()}.{row.get('Last Name', '').strip().lower()}@pandaexteriors.com",
                'status': 'active'
            }
            
            # Check if employee exists
            try:
                existing = table.get_item(Key={'last_name': employee_data['last_name']})
                if 'Item' in existing:
                    updated_count += 1
                else:
                    imported_count += 1
            except:
                imported_count += 1
            
            # Insert/update employee
            table.put_item(Item=employee_data)
        
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'message': f'Import completed. {imported_count} new employees, {updated_count} updated.',
                'imported': imported_count,
                'updated': updated_count
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': f'Import failed: {str(e)}'})
        }