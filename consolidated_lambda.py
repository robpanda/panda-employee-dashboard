import json
import boto3
import csv
import io
import urllib.request
import urllib.parse
from decimal import Decimal
import hashlib
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('panda-employees')
admin_table = dynamodb.Table('panda-admin-users')

def lambda_handler(event, context):
    try:
        # Handle CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'body': ''
            }
        
        path = event.get('path', '')
        method = event.get('httpMethod', 'GET')
        
        print(f"Lambda handler called with path: {path}, method: {method}")
        
        # Admin authentication endpoints
        if path == '/admin-login':
            return handle_admin_login(event)
        elif path == '/admin-users':
            return handle_admin_users(event)
        elif path == '/create-admin':
            return handle_create_admin(event)
        
        # Handle both root path and /employees for GET requests
        if (path == '/employees' or path == '' or path == '/') and method == 'GET':
            print("Calling get_employees()")
            return get_employees()
        elif path == '/import' and method == 'POST':
            print("Calling import_employees()")
            return import_employees()
        elif path == '/award-points' and method == 'POST':
            print("Calling award_points()")
            return award_points(event)
        elif path == '/employee-login' and method == 'POST':
            print("Calling employee_login()")
            return employee_login(event)
        elif path == '/upload-employees' and method == 'POST':
            print("Calling upload_employees()")
            return upload_employees(event)
        elif path == '/upload' and method == 'POST':
            print("Calling handle_file_upload()")
            return handle_file_upload(event)
        elif path == '/smart-import' and method == 'POST':
            print("Calling smart_import()")
            result = smart_import(event)
            print(f"Smart import result: {result}")
            return result
        elif path == '/restore-backup' and method == 'POST':
            print("Calling restore_backup()")
            return restore_backup(event)
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f'Not found - path: {path}, method: {method}'})
            }
            
    except Exception as e:
        print(f"Lambda handler error: {str(e)}")
        return {
            'statusCode': 500,
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
            'body': json.dumps({
                'message': f'Import completed. {imported_count} new employees, {updated_count} updated.',
                'imported': imported_count,
                'updated': updated_count
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
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
            'body': json.dumps({
                'message': f'Awarded {points} points to {employee["name"]}',
                'new_balance': float(new_balance)
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
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
                'body': json.dumps({'error': 'Invalid credentials'})
            }
        
        employee = response['Items'][0]
        
        # Check password (in production, use proper hashing)
        if employee.get('password') != password:
            return {
                'statusCode': 401,
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
            'body': json.dumps({
                'message': 'Login successful',
                'employee': employee_data
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
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
            'body': json.dumps({
                'message': f'Upload completed. {imported_count} new employees, {updated_count} updated.',
                'imported': imported_count,
                'updated': updated_count
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Upload failed: {str(e)}'})
        }

def handle_file_upload(event):
    """Handle file upload with optional smart import"""
    try:
        import base64
        
        # Get file content from base64 encoded body
        if event.get('isBase64Encoded'):
            body = base64.b64decode(event['body'])
        else:
            body = event['body'].encode('utf-8')
        
        # Parse multipart form data
        content_type = event.get('headers', {}).get('content-type', '') or event.get('headers', {}).get('Content-Type', '')
        
        if 'multipart/form-data' not in content_type:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Content-Type must be multipart/form-data'})
            }
        
        # Extract boundary
        boundary = content_type.split('boundary=')[1]
        parts = body.split(f'--{boundary}'.encode())
        
        csv_content = None
        is_smart_import = False
        
        for part in parts:
            if b'name="smart_import"' in part:
                is_smart_import = True
            elif b'filename=' in part and (b'.csv' in part or b'.xlsx' in part or b'.xls' in part):
                # Find the start of file content (after double CRLF)
                content_start = part.find(b'\r\n\r\n')
                if content_start != -1:
                    file_content = part[content_start + 4:].rstrip(b'\r\n')
                    csv_content = file_content.decode('utf-8')
                    break
        
        if not csv_content:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No valid CSV file found in upload'})
            }
        
        # Parse CSV into employee data
        new_employees = parse_csv_to_employees(csv_content)
        
        if not new_employees:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No valid employee data found in file'})
            }
        
        if is_smart_import:
            return perform_smart_import(new_employees, 'uploaded file')
        else:
            return perform_regular_import(new_employees)
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'File upload failed: {str(e)}'})
        }

def smart_import(event):
    """Handle smart import from Google Sheets"""
    try:
        body = json.loads(event.get('body', '{}'))
        source = body.get('source', 'sheets')
        
        if source == 'sheets':
            new_employees = fetch_from_google_sheets()
            if not new_employees:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'No data found in Google Sheets'})
                }
            return perform_smart_import(new_employees, 'Google Sheets')
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid source specified'})
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Smart import failed: {str(e)}'})
        }

def fetch_from_google_sheets():
    """Fetch employee data from Google Sheets"""
    try:
        sheet_url = "https://docs.google.com/spreadsheets/d/1vO-94iEtB8FAthneJ8Cx1Cm-iA-oHJiBwOPAGmsiM-4/export?format=csv"
        
        with urllib.request.urlopen(sheet_url) as response:
            csv_content = response.read().decode('utf-8')
        
        return parse_csv_to_employees(csv_content)
        
    except Exception as e:
        print(f"Error fetching from Google Sheets: {str(e)}")
        return []

def parse_csv_to_employees(csv_content):
    """Parse CSV content into employee data structure"""
    try:
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        employees_data = []
        
        print(f"Parsing CSV content, first 500 chars: {csv_content[:500]}")
        
        for row_num, row in enumerate(csv_reader):
            if not row.get('Last Name') or not row.get('First Name'):
                continue
                
            first_name = row.get('First Name', '').strip()
            last_name = row.get('Last Name', '').strip()
            
            # Generate email from name
            email = f"{first_name.lower()}.{last_name.lower()}@pandaexteriors.com"
            
            # Handle different status formats
            status_code = row.get('Employee Status Code', '').strip().upper()
            status = 'active'  # Default to active
            if status_code == 'T' or status_code == 'TERMINATED':
                status = 'terminated'
            
            employee_data = {
                'last_name': last_name,
                'first_name': first_name,
                'name': f"{first_name} {last_name}",
                'employee_id': row.get('Employee Id', '').strip() or row.get('Employee ID', '').strip(),
                'role': row.get('Job Title (PIT)', '').strip() or row.get('Position Description', '').strip() or row.get('Role', '').strip(),
                'supervisor': row.get('Supervisor', '').strip(),
                'office': row.get('Current Work Location Name', '').strip() or row.get('Office', '').strip(),
                'department': row.get('Department Description', '').strip() or row.get('Department', '').strip(),
                'hire_date': row.get('Hire Date', '').strip(),
                'phone': row.get('Phone', '').strip(),
                'email': email,
                'status': status,
                'password': 'Welcome2025!',
                'points_lifetime': Decimal('0'),
                'points_redeemed': Decimal('0'),
                'points_balance': Decimal('0')
            }
            
            employees_data.append(employee_data)
            
            if row_num < 3:  # Log first few employees for debugging
                print(f"Parsed employee {row_num}: {employee_data['name']} - {employee_data['status']}")
        
        print(f"Parsed {len(employees_data)} employees from CSV")
        return employees_data
        
    except Exception as e:
        print(f"Error parsing CSV: {str(e)}")
        return []

def perform_smart_import(new_employees, source_name):
    """Perform smart import with auto-termination"""
    try:
        from datetime import datetime
        
        print(f"Starting smart import from {source_name} with {len(new_employees)} new employees")
        
        # Get all existing employees
        existing_employees = []
        response = table.scan()
        existing_employees = response.get('Items', [])
        
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            existing_employees.extend(response.get('Items', []))
        
        print(f"Found {len(existing_employees)} existing employees")
        
        # Create lookup maps for new employees
        new_by_email = {emp['email'].lower(): emp for emp in new_employees}
        new_by_name = {emp['name'].lower(): emp for emp in new_employees}
        new_by_id = {emp['employee_id']: emp for emp in new_employees if emp.get('employee_id')}
        
        print(f"Created lookup maps: {len(new_by_email)} emails, {len(new_by_name)} names, {len(new_by_id)} IDs")
        
        # Track changes
        added_count = 0
        terminated_count = 0
        unchanged_count = 0
        updated_count = 0
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Check existing employees for termination or updates
        for existing_emp in existing_employees:
            email = existing_emp.get('email', '').lower()
            name = existing_emp.get('name', '').lower()
            emp_id = existing_emp.get('employee_id', '')
            
            # Check if employee exists in new list
            found_emp = None
            if email and email in new_by_email:
                found_emp = new_by_email[email]
            elif name and name in new_by_name:
                found_emp = new_by_name[name]
            elif emp_id and emp_id in new_by_id:
                found_emp = new_by_id[emp_id]
            
            if found_emp:
                # Employee found - update their info but preserve points
                found_emp['points_lifetime'] = existing_emp.get('points_lifetime', Decimal('0'))
                found_emp['points_balance'] = existing_emp.get('points_balance', Decimal('0'))
                found_emp['points_redeemed'] = existing_emp.get('points_redeemed', Decimal('0'))
                found_emp['password'] = existing_emp.get('password', 'Welcome2025!')
                
                # Ensure status is active for found employees
                found_emp['status'] = 'active'
                
                table.put_item(Item=found_emp)
                updated_count += 1
            elif existing_emp.get('status') != 'terminated':
                # Employee not found - terminate them
                existing_emp['status'] = 'terminated'
                existing_emp['termination_date'] = today
                table.put_item(Item=existing_emp)
                terminated_count += 1
                print(f"Terminated employee: {existing_emp.get('name', 'Unknown')}")
        
        # Add completely new employees
        existing_emails = {emp.get('email', '').lower() for emp in existing_employees}
        existing_names = {emp.get('name', '').lower() for emp in existing_employees}
        existing_ids = {emp.get('employee_id', '') for emp in existing_employees}
        
        for new_emp in new_employees:
            email = new_emp.get('email', '').lower()
            name = new_emp.get('name', '').lower()
            emp_id = new_emp.get('employee_id', '')
            
            # Check if this is a completely new employee
            exists = (email and email in existing_emails) or \
                    (name and name in existing_names) or \
                    (emp_id and emp_id in existing_ids)
            
            if not exists:
                # Add new employee
                new_emp['status'] = 'active'
                if not new_emp.get('hire_date'):
                    new_emp['hire_date'] = today
                
                table.put_item(Item=new_emp)
                added_count += 1
                print(f"Added new employee: {new_emp.get('name', 'Unknown')}")
        
        message = f"Smart import from {source_name} completed:\n" + \
                 f"• {added_count} new employees added\n" + \
                 f"• {updated_count} employees updated\n" + \
                 f"• {terminated_count} employees terminated"
        
        print(f"Smart import completed: {added_count} added, {updated_count} updated, {terminated_count} terminated")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': message,
                'added': added_count,
                'updated': updated_count,
                'terminated': terminated_count
            })
        }
    
    except Exception as e:
        print(f"Smart import error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Smart import failed: {str(e)}'})
        }

def perform_regular_import(new_employees):
    """Perform regular import without termination"""
    try:
        imported_count = 0
        updated_count = 0
        
        for employee in new_employees:
            try:
                existing = table.get_item(Key={'last_name': employee['last_name']})
                if 'Item' in existing:
                    # Update existing employee but preserve points
                    existing_item = existing['Item']
                    employee['points_lifetime'] = existing_item.get('points_lifetime', Decimal('0'))
                    employee['points_balance'] = existing_item.get('points_balance', Decimal('0'))
                    employee['points_redeemed'] = existing_item.get('points_redeemed', Decimal('0'))
                    updated_count += 1
                else:
                    imported_count += 1
            except:
                imported_count += 1
            
            table.put_item(Item=employee)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Import completed. {imported_count} new employees, {updated_count} updated.',
                'imported': imported_count,
                'updated': updated_count
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Regular import failed: {str(e)}'})
        }

def restore_backup(event):
    """Restore employee data from backup"""
    try:
        body = json.loads(event.get('body', '{}'))
        employees = body.get('employees', [])
        
        if not employees:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No employee data provided'})
            }
        
        # Clear existing data
        response = table.scan()
        existing_items = response.get('Items', [])
        
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            existing_items.extend(response.get('Items', []))
        
        # Delete existing items
        for item in existing_items:
            table.delete_item(Key={'last_name': item['last_name']})
        
        # Restore from backup
        restored_count = 0
        for employee in employees:
            # Convert numeric values to Decimal for DynamoDB
            for key in ['points_lifetime', 'points_balance', 'points_redeemed']:
                if key in employee and not isinstance(employee[key], Decimal):
                    employee[key] = Decimal(str(employee[key]))
            
            table.put_item(Item=employee)
            restored_count += 1
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully restored {restored_count} employees from backup',
                'count': restored_count
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Backup restore failed: {str(e)}'})
        }

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def handle_admin_login(event):
    try:
        body = json.loads(event.get('body', '{}'))
        email = body.get('email')
        password = body.get('password')
        
        if not email or not password:
            return {
                'statusCode': 400,
                'body': json.dumps({'success': False, 'message': 'Email and password required'})
            }
        
        response = admin_table.get_item(Key={'email': email})
        
        if 'Item' not in response:
            return {
                'statusCode': 401,
                'body': json.dumps({'success': False, 'message': 'Invalid credentials'})
            }
        
        admin_user = response['Item']
        if admin_user['password'] != hash_password(password) or not admin_user.get('active', True):
            return {
                'statusCode': 401,
                'body': json.dumps({'success': False, 'message': 'Invalid credentials'})
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps({'success': True, 'user': {'email': email, 'role': admin_user.get('role', 'admin')}})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'success': False, 'message': str(e)})
        }

def handle_admin_users(event):
    try:
        method = event.get('httpMethod')
        
        if method == 'GET':
            response = admin_table.scan()
            users = []
            for item in response.get('Items', []):
                users.append({
                    'email': item['email'],
                    'role': item.get('role', 'admin'),
                    'active': item.get('active', True),
                    'created_at': item.get('created_at', '')
                })
            
            return {
                'statusCode': 200,
                'body': json.dumps({'users': users})
            }
            
        elif method == 'POST':
            body = json.loads(event.get('body', '{}'))
            email = body.get('email')
            password = body.get('password')
            role = body.get('role', 'admin')
            
            if not email or not password:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'success': False, 'message': 'Email and password required'})
                }
            
            admin_table.put_item(
                Item={
                    'email': email,
                    'password': hash_password(password),
                    'role': role,
                    'active': True,
                    'created_at': datetime.now().isoformat()
                }
            )
            
            return {
                'statusCode': 200,
                'body': json.dumps({'success': True, 'message': 'Admin user created'})
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'success': False, 'message': str(e)})
        }

def handle_create_admin(event):
    try:
        super_admin_email = 'robwinters@pandaexteriors.com'
        super_admin_password = 'PandaAdmin2024!'
        
        try:
            admin_table.put_item(
                Item={
                    'email': super_admin_email,
                    'password': hash_password(super_admin_password),
                    'role': 'super_admin',
                    'active': True,
                    'created_at': datetime.now().isoformat()
                },
                ConditionExpression='attribute_not_exists(email)'
            )
            message = f'Super admin created: {super_admin_email}'
        except:
            message = f'Super admin already exists: {super_admin_email}'
        
        return {
            'statusCode': 200,
            'body': json.dumps({'success': True, 'message': message})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'success': False, 'message': str(e)})
        }