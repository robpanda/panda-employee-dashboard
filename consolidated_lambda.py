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
        elif path == '/award-points' and method == 'POST':
            return award_points(event)
        elif path == '/employee-login' and method == 'POST':
            return employee_login(event)
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
        sheet_url = "https://docs.google.com/spreadsheets/d/1vO-94iEtB8FAthneJ8Cx1Cm-iA-oHJiBwOPAGmsiM-4/export?format=csv"
        
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
                'status': 'active',
                'password': 'Welcome2025!',
                'points_lifetime': Decimal('0'),
                'points_redeemed': Decimal('0'),
                'points_balance': Decimal('0')
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

def award_points(event):
    try:
        body = json.loads(event.get('body', '{}'))
        employee_email = body.get('employee_email')
        points = Decimal(str(body.get('points', 0)))
        reason = body.get('reason', '')
        manager = body.get('manager', '')
        
        if not employee_email or points <= 0:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Invalid employee or points amount'})
            }
        
        # Find employee by email
        response = table.scan(
            FilterExpression='email = :email',
            ExpressionAttributeValues={':email': employee_email}
        )
        
        if not response['Items']:
            return {
                'statusCode': 404,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Employee not found'})
            }
        
        employee = response['Items'][0]
        
        # Update points
        new_lifetime = (employee.get('points_lifetime', Decimal('0')) + points)
        new_balance = (employee.get('points_balance', Decimal('0')) + points)
        
        table.update_item(
            Key={'last_name': employee['last_name']},
            UpdateExpression='SET points_lifetime = :lifetime, points_balance = :balance',
            ExpressionAttributeValues={
                ':lifetime': new_lifetime,
                ':balance': new_balance
            }
        )
        
        # Send email notification
        try:
            ses = boto3.client('ses', region_name='us-east-1')
            ses.send_email(
                Source='noreply@pandaexteriors.com',
                Destination={'ToAddresses': [employee_email]},
                Message={
                    'Subject': {'Data': 'You received Panda Points!'},
                    'Body': {
                        'Text': {
                            'Data': f"Congratulations {employee['name']}!\n\nYou have been awarded {points} Panda Points by {manager}.\n\nReason: {reason or 'Great work!'}\n\nYour new balance: {new_balance} points\n\nRedeem your points at MyPandaPoints.com"
                        }
                    }
                }
            )
        except Exception as e:
            print(f"Email notification failed: {e}")
        
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'message': f'Awarded {points} points to {employee["name"]}',
                'new_balance': float(new_balance)
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': f'Award failed: {str(e)}'})
        }

def employee_login(event):
    try:
        body = json.loads(event.get('body', '{}'))
        email = body.get('email')
        password = body.get('password')
        
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Email and password required'})
            }
        
        # Find employee by email
        response = table.scan(
            FilterExpression='email = :email AND #status = :status',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':email': email,
                ':status': 'active'
            }
        )
        
        if not response['Items']:
            return {
                'statusCode': 401,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Invalid credentials'})
            }
        
        employee = response['Items'][0]
        
        # Check password (in production, use proper hashing)
        if employee.get('password') != password:
            return {
                'statusCode': 401,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Invalid credentials'})
            }
        
        # Convert Decimal to float for JSON
        employee_data = {}
        for key, value in employee.items():
            if isinstance(value, Decimal):
                employee_data[key] = float(value)
            else:
                employee_data[key] = value
        
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'message': 'Login successful',
                'employee': employee_data
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': f'Login failed: {str(e)}'})
        }