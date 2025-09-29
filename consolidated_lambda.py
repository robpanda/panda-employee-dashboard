import json
import boto3
import csv
import io
import urllib.request
import urllib.parse
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
        
        # Handle both root path and /employees for GET requests
        if (path == '/employees' or path == '' or path == '/') and method == 'GET':
            return get_employees()
        elif path == '/import' and method == 'POST':
            return import_employees()
        elif path == '/award-points' and method == 'POST':
            return award_points(event)
        elif path == '/employee-login' and method == 'POST':
            return employee_login(event)
        elif path == '/upload-employees' and method == 'POST':
            return upload_employees(event)
        else:
            return {
                'statusCode': 404,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': f'Not found - path: {path}, method: {method}'})
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
        
        with urllib.request.urlopen(sheet_url) as response:
            csv_content = response.read().decode('utf-8')
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        imported_count = 0
        updated_count = 0
        
        for row in csv_reader:
            # Skip empty rows
            if not row.get('Last Name') or not row.get('First Name'):
                continue
                
            first_name = row.get('First Name', '').strip()
            last_name = row.get('Last Name', '').strip()
            
            # Generate email from name
            email = f"{first_name.lower()}.{last_name.lower()}@pandaexteriors.com"
            
            employee_data = {
                'last_name': last_name,
                'first_name': first_name,
                'name': f"{first_name} {last_name}",
                'employee_id': row.get('Employee ID', '').strip(),
                'role': row.get('Role', '').strip(),
                'supervisor': row.get('Supervisor', '').strip(),
                'office': row.get('Office', '').strip(),
                'department': row.get('Department', '').strip(),
                'hire_date': row.get('Hire Date', '').strip(),
                'phone': row.get('Phone', '').strip(),
                'email': email,
                'status': 'active',
                'password': 'Welcome2025!',
                'points_lifetime': Decimal('0'),
                'points_redeemed': Decimal('0'),
                'points_balance': Decimal('0')
            }
            
            # Use last_name as primary key (existing table structure)
            try:
                existing = table.get_item(Key={'last_name': last_name})
                if 'Item' in existing:
                    # Update existing employee but preserve points
                    existing_item = existing['Item']
                    employee_data['points_lifetime'] = existing_item.get('points_lifetime', Decimal('0'))
                    employee_data['points_balance'] = existing_item.get('points_balance', Decimal('0'))
                    employee_data['points_redeemed'] = existing_item.get('points_redeemed', Decimal('0'))
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
        
        # Find employee by email using scan
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

def upload_employees(event):
    try:
        import base64
        
        # Get file content from base64 encoded body
        if event.get('isBase64Encoded'):
            body = base64.b64decode(event['body'])
        else:
            body = event['body'].encode('utf-8')
        
        # Parse multipart form data
        content_type = event.get('headers', {}).get('content-type', '') or event.get('headers', {}).get('Content-Type', '')
        
        if 'multipart/form-data' in content_type:
            # Extract boundary
            boundary = content_type.split('boundary=')[1]
            parts = body.split(f'--{boundary}'.encode())
            
            csv_content = None
            for part in parts:
                if b'filename=' in part and (b'.csv' in part or b'.xlsx' in part or b'.xls' in part):
                    # Find the start of file content (after double CRLF)
                    content_start = part.find(b'\r\n\r\n')
                    if content_start != -1:
                        file_content = part[content_start + 4:].rstrip(b'\r\n')
                        csv_content = file_content.decode('utf-8')
                        break
            
            if not csv_content:
                return {
                    'statusCode': 400,
                    'headers': {'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'No valid CSV file found in upload'})
                }
        else:
            # Direct CSV content
            csv_content = body.decode('utf-8')
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        imported_count = 0
        updated_count = 0
        
        for row in csv_reader:
            if not row.get('Last Name') or not row.get('First Name'):
                continue
                
            first_name = row.get('First Name', '').strip()
            last_name = row.get('Last Name', '').strip()
            
            # Generate email from name
            email = f"{first_name.lower()}.{last_name.lower()}@pandaexteriors.com"
            
            employee_data = {
                'last_name': last_name,
                'first_name': first_name,
                'name': f"{first_name} {last_name}",
                'employee_id': row.get('Employee Id', '').strip(),
                'role': row.get('Job Title (PIT)', '').strip() or row.get('Position Description', '').strip(),
                'supervisor': row.get('Supervisor', '').strip(),
                'office': row.get('Current Work Location Name', '').strip(),
                'department': row.get('Department Description', '').strip(),
                'hire_date': row.get('Hire Date', '').strip(),
                'phone': '',
                'email': email,
                'status': 'active' if row.get('Employee Status Code', '').strip().lower() == 'active' else 'inactive',
                'password': 'Welcome2025!',
                'points_lifetime': Decimal('0'),
                'points_redeemed': Decimal('0'),
                'points_balance': Decimal('0')
            }
            
            # Check if employee exists
            try:
                existing = table.get_item(Key={'last_name': last_name})
                if 'Item' in existing:
                    # Update existing employee but preserve points
                    existing_item = existing['Item']
                    employee_data['points_lifetime'] = existing_item.get('points_lifetime', Decimal('0'))
                    employee_data['points_balance'] = existing_item.get('points_balance', Decimal('0'))
                    employee_data['points_redeemed'] = existing_item.get('points_redeemed', Decimal('0'))
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
                'message': f'Upload completed. {imported_count} new employees, {updated_count} updated.',
                'imported': imported_count,
                'updated': updated_count
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': f'Upload failed: {str(e)}'})
        }