import json
import boto3
import os
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

def get_cors_headers():
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, Accept',
        'Content-Type': 'application/json'
    }

dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses', region_name='us-east-2')
employees_table = dynamodb.Table(os.environ.get('EMPLOYEES_TABLE', 'panda-employees'))
contacts_table = dynamodb.Table(os.environ.get('CONTACTS_TABLE', 'panda-contacts'))
collections_table = dynamodb.Table(os.environ.get('COLLECTIONS_TABLE', 'panda-collections'))
config_table = dynamodb.Table(os.environ.get('CONFIG_TABLE', 'panda-config'))
points_history_table = dynamodb.Table(os.environ.get('POINTS_HISTORY_TABLE', 'panda-points-history'))
referrals_table = dynamodb.Table(os.environ.get('REFERRALS_TABLE', 'panda-referrals'))
try:
    admin_users_table = dynamodb.Table('panda-admin-users')
except:
    admin_users_table = None

def lambda_handler(event, context):
    print(f'LAMBDA DEBUG: Full event: {json.dumps(event, default=str)}')
    
    # Handle both API Gateway and Function URL event formats
    if 'requestContext' in event and 'http' in event['requestContext']:
        # Function URL format
        http_method = event['requestContext']['http']['method']
        path = event['requestContext']['http']['path']
        print(f'LAMBDA DEBUG: Using Function URL format')
    elif 'httpMethod' in event:
        # API Gateway format
        http_method = event['httpMethod']
        path = event.get('path', '/')
        print(f'LAMBDA DEBUG: Using API Gateway format')
    else:
        # Default fallback
        http_method = 'GET'
        path = '/'
        print(f'LAMBDA DEBUG: Using fallback format')
    
    print(f'LAMBDA DEBUG: Method={http_method}, Path={path}, Event keys: {list(event.keys())}')
    
    try:
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': get_cors_headers(),
                'body': ''
            }
        elif path == '/employees':
            print(f'LAMBDA DEBUG: Matched /employees route')
            if http_method == 'GET':
                print(f'LAMBDA DEBUG: Calling get_employees')
                return get_employees(event)
            elif http_method == 'POST':
                print(f'LAMBDA DEBUG: Calling create_employee')
                return create_employee(event)
        elif path.startswith('/employees/') and http_method == 'PUT':
            print(f'LAMBDA DEBUG: Matched PUT /employees/ route')
            return update_employee(event)
        elif path.startswith('/employees/') and http_method == 'DELETE':
            print(f'LAMBDA DEBUG: Matched DELETE /employees/ route')
            return delete_employee(event)
        elif path == '/contacts':
            return handle_contacts(event)
        elif path == '/collections':
            return handle_collections(event)
        elif path == '/config':
            return handle_config(event)
        elif path == '/admin-users':
            return handle_admin_users(event)
        elif path == '/' and 'action' in json.loads(event.get('body', '{}')):
            # Handle action-based requests to root path
            body = json.loads(event.get('body', '{}'))
            action = body.get('action')
            if action == 'get_admin_users':
                return handle_admin_users(event)
        elif path == '/create-admin':
            return create_super_admin(event)
        elif path == '/points' or path.startswith('/points/'):
            return handle_points(event)
        elif path == '/points-history':
            return handle_points_history(event)
        elif path == '/referrals' or path.startswith('/referrals/'):
            return handle_referrals(event)
        elif path == '/employee-login':
            print(f'LAMBDA DEBUG: Calling handle_employee_login')
            return handle_employee_login(event)
        elif path == '/admin-login':
            print(f'LAMBDA DEBUG: Calling handle_admin_login')
            return handle_admin_login(event)
        elif path == '/gift-cards':
            print(f'LAMBDA DEBUG: Calling handle_gift_cards')
            return handle_gift_cards(event)
        elif path.startswith('/login-history/'):
            print(f'LAMBDA DEBUG: Calling handle_login_history')
            return handle_login_history(event)
        elif path == '/test':
            return {
                'statusCode': 200,
                'body': json.dumps({'message': f'Test successful - Method: {http_method}, Path: {path}'})
            }
        elif path == '/debug':
            return {
                'statusCode': 200,
                'headers': {
                'Content-Type': 'application/json',
                },
                'body': json.dumps({
                    'method': http_method,
                    'path': path,
                    'event_keys': list(event.keys()),
                    'requestContext': event.get('requestContext', {}),
                    'all_paths_checked': [
                        '/employees', '/contacts', '/collections', '/config',
                        '/admin-users', '/create-admin', '/points', '/points-history',
                        '/referrals', '/employee-login', '/admin-login', '/test'
                    ]
                })
            }
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    },
                'body': json.dumps({'error': 'Not found'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                },
            'body': json.dumps({'error': str(e)})
        }

def get_employees(event):
    try:
        print(f'GET_EMPLOYEES: Starting function')
        query_params = event.get('queryStringParameters') or {}
        print(f'GET_EMPLOYEES: Query params: {query_params}')
        
        if 'email' in query_params:
            # Search by email
            print(f'GET_EMPLOYEES: Searching by email: {query_params["email"]}')
            response = employees_table.query(
                IndexName='email-index',
                KeyConditionExpression='Email = :email',
                ExpressionAttributeValues={':email': query_params['email']}
            )
            items = response['Items']
        else:
            # Get all employees
            print(f'GET_EMPLOYEES: Scanning all employees')
            response = employees_table.scan()
            items = response['Items']
            print(f'GET_EMPLOYEES: Found {len(items)} employees')
        
        # Convert Decimal to float for JSON serialization and ensure consistent field names
        for item in items:
            for key, value in item.items():
                if isinstance(value, Decimal):
                    item[key] = float(value)
            
            # Ensure employee_id exists
            if 'employee_id' not in item and 'id' in item:
                item['employee_id'] = item['id']
        
        print(f'GET_EMPLOYEES: Returning {len(items)} employees')
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({'employees': items})
        }
    except Exception as e:
        print(f'GET_EMPLOYEES ERROR: {str(e)}')
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                },
            'body': json.dumps({'error': f'Failed to get employees: {str(e)}'})
        }

def create_employee(event):
    try:
        body = json.loads(event.get('body', '{}'))
        print(f'Received body keys: {list(body.keys())}')
    except Exception as e:
        print(f'Error parsing body: {e}')
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                },
            'body': json.dumps({'error': 'Invalid JSON body'})
        }
    
    # Handle bulk employee data
    if 'employees' in body:
        employees_data = body['employees']
        print(f'Processing {len(employees_data)} employees for bulk import')
        
        # Don't clear existing data - we'll update/merge instead
        print(f'Processing {len(employees_data)} employees for bulk import/update')
        
        # Insert new employees
        success_count = 0
        with employees_table.batch_writer() as batch:
            for emp_data in employees_data:
                try:
                    # Handle both frontend format and API format
                    emp_id = emp_data.get('Employee Id', emp_data.get('employee_id', emp_data.get('id', str(uuid.uuid4()))))
                    if not emp_id:
                        emp_id = str(uuid.uuid4())
                    
                    # Preserve existing employee data if updating
                    existing_employee = None
                    try:
                        response = employees_table.scan(
                            FilterExpression='id = :emp_id OR employee_id = :emp_id OR #eid = :emp_id',
                            ExpressionAttributeNames={'#eid': 'Employee Id'},
                            ExpressionAttributeValues={':emp_id': str(emp_id)}
                        )
                        if response['Items']:
                            existing_employee = response['Items'][0]
                            print(f'Found existing employee {emp_id}: {existing_employee.get("First Name", "NO_FIRST")} {existing_employee.get("Last Name", "NO_LAST")}')
                    except Exception as e:
                        print(f'Error finding existing employee {emp_id}: {e}')
                    
                    print(f'Import data for {emp_id}: {emp_data}')
                    
                    # Extract first name from various possible field names
                    first_name = ''
                    if 'First Name' in emp_data and emp_data['First Name']:
                        first_name = emp_data['First Name']
                    elif 'first_name' in emp_data and emp_data['first_name']:
                        first_name = emp_data['first_name']
                    elif 'name' in emp_data and emp_data['name']:
                        first_name = emp_data['name'].split(' ')[0]
                    elif existing_employee:
                        first_name = existing_employee.get('First Name', existing_employee.get('first_name', ''))
                    
                    # Extract last name from various possible field names
                    last_name = ''
                    if 'Last Name' in emp_data and emp_data['Last Name']:
                        last_name = emp_data['Last Name']
                    elif 'last_name' in emp_data and emp_data['last_name']:
                        last_name = emp_data['last_name']
                    elif 'name' in emp_data and emp_data['name'] and len(emp_data['name'].split(' ')) > 1:
                        last_name = ' '.join(emp_data['name'].split(' ')[1:])
                    elif existing_employee:
                        last_name = existing_employee.get('Last Name', existing_employee.get('last_name', ''))
                    
                    # Extract position/title and auto-detect Points Manager
                    position = emp_data.get('Position', emp_data.get('position', existing_employee.get('Position', '') if existing_employee else ''))
                    is_points_manager = 'No'
                    if position:
                        position_lower = position.lower()
                        if any(title in position_lower for title in ['director', 'president', 'vice president', 'c-suite', 'ceo', 'cfo', 'coo', 'cto']):
                            is_points_manager = 'Yes'
                    
                    print(f'Extracted names for {emp_id}: First="{first_name}", Last="{last_name}"')
                    
                    employee = {
                        'id': str(emp_id),
                        'employee_id': str(emp_id),
                        'Employee Id': str(emp_id),
                        'First Name': first_name,
                        'first_name': first_name,  # Add both formats for compatibility
                        'Last Name': last_name,
                        'last_name': last_name,    # Add both formats for compatibility
                        'Department': emp_data.get('Department', emp_data.get('department', '')),
                        'Position': emp_data.get('Position', emp_data.get('position', '')),
                        'Employment Date': emp_data.get('Employment Date', emp_data.get('employment_date', '')),
                        'Years of Service': emp_data.get('Years of Service', emp_data.get('years_of_service', '')),
                        'Email': emp_data.get('Email', emp_data.get('email', '')),
                        'Phone': emp_data.get('Phone', emp_data.get('phone', '')),
                        'office': emp_data.get('office', ''),
                        'supervisor': emp_data.get('supervisor', ''),
                        'is_supervisor': emp_data.get('is_supervisor', 'No'),
                        'Merch Requested': emp_data.get('Merch Requested', emp_data.get('merch_requested', '')),
                        'Merch Sent': emp_data.get('Merch Sent', emp_data.get('merch_sent', 'No')),
                        'Merch Sent Date': emp_data.get('Merch Sent Date', emp_data.get('merch_sent_date', '')),
                        'Terminated': emp_data.get('Terminated', emp_data.get('terminated', 'No')),
                        'Termination Date': emp_data.get('Termination Date', emp_data.get('termination_date', '')),
                        'points_manager': is_points_manager,
                        'points_budget': 500 if is_points_manager == 'Yes' else 0,
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    # Preserve existing points and login data
                    if existing_employee:
                        employee['points'] = existing_employee.get('points', 0)
                        employee['Panda Points'] = existing_employee.get('Panda Points', 0)
                        employee['last_login'] = existing_employee.get('last_login', '')
                        employee['password'] = existing_employee.get('password', 'Panda2025!')
                        # Preserve existing Points Manager status if already set
                        if existing_employee.get('points_manager') == 'Yes':
                            employee['points_manager'] = 'Yes'
                            employee['points_budget'] = existing_employee.get('points_budget', 500)
                        # If no first/last name in import data, keep existing names
                        if not first_name and existing_employee.get('First Name'):
                            employee['First Name'] = existing_employee['First Name']
                            employee['first_name'] = existing_employee['First Name']
                        if not last_name and existing_employee.get('Last Name'):
                            employee['Last Name'] = existing_employee['Last Name']
                            employee['last_name'] = existing_employee['Last Name']
                    batch.put_item(Item=employee)
                    success_count += 1
                except Exception as e:
                    print(f'Error inserting employee {emp_data}: {e}')
                    continue
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({'message': f'{success_count} employees saved successfully (out of {len(employees_data)} processed)'})
        }
    
    # Handle single employee from admin form
    employee_id = body.get('employee_id', str(uuid.uuid4()))
    current_date = datetime.now().isoformat()
    
    employee = {
        'id': str(employee_id),
        'employee_id': str(employee_id),
        'Employee Id': str(employee_id),
        'First Name': body.get('first_name', ''),
        'Last Name': body.get('last_name', ''),
        'Email': body.get('email', ''),
        'Phone': body.get('phone', ''),
        'Department': body.get('department', ''),
        'Position': body.get('position', ''),
        'Employment Date': body.get('employment_date', current_date.split('T')[0]),
        'Terminated': body.get('terminated', 'No'),
        'office': body.get('office', ''),
        'supervisor': body.get('manager', ''),
        'is_supervisor': 'No',
        'Merch Requested': '',
        'Merch Sent': 'No',
        'Merch Sent Date': '',
        'Termination Date': '',
        'updated_at': current_date
    }
    
    employees_table.put_item(Item=employee)
    
    return {
        'statusCode': 201,
        'headers': get_cors_headers(),
        'body': json.dumps({'employee_id': employee_id, 'message': 'Employee created successfully'})
    }

def update_employee(event):
    try:
        # Handle both API Gateway and Function URL event formats
        if 'requestContext' in event and 'http' in event['requestContext']:
            # Function URL format
            path = event['requestContext']['http']['path']
        else:
            # API Gateway format
            path = event.get('path', '/')
        
        path_parts = path.split('/')
        employee_id = path_parts[-1]
        body = json.loads(event.get('body', '{}'))
        
        print(f'UPDATE: Updating employee {employee_id} with data: {body}')
        
        # Find employee by scanning for matching ID
        try:
            response = employees_table.scan(
                FilterExpression='id = :emp_id OR employee_id = :emp_id OR #eid = :emp_id',
                ExpressionAttributeNames={'#eid': 'Employee Id'},
                ExpressionAttributeValues={':emp_id': employee_id}
            )
            
            if not response['Items']:
                print(f'UPDATE: Employee {employee_id} not found')
                return {
                    'statusCode': 404,
                    'headers': get_cors_headers(),
                    'body': json.dumps({'error': 'Employee not found'})
                }
            
            employee = response['Items'][0]
            print(f'UPDATE: Found employee {employee.get("First Name")} {employee.get("Last Name")}')
            
        except Exception as e:
            print(f'UPDATE ERROR: Failed to find employee: {e}')
            return {
                'statusCode': 500,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': f'Database error: {str(e)}'})
            }
        
        # Update fields
        for key, value in body.items():
            if key not in ['id']:
                employee[key] = value
        
        employee['updated_at'] = datetime.now().isoformat()
        
        # Save updated employee
        employees_table.put_item(Item=employee)
        print(f'UPDATE: Successfully updated employee {employee_id}')
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({'message': 'Employee updated successfully'})
        }
        
    except Exception as e:
        print(f'UPDATE ERROR: {e}')
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': str(e)})
        }

def delete_employee(event):
    try:
        # Handle both API Gateway and Function URL event formats
        if 'requestContext' in event and 'http' in event['requestContext']:
            # Function URL format
            path = event['requestContext']['http']['path']
        else:
            # API Gateway format
            path = event.get('path', '/')
        
        path_parts = path.split('/')
        employee_id = path_parts[-1]
        
        print(f'DELETE: Attempting to delete employee {employee_id}')
        
        # Find employee by scanning for matching ID (since we use different ID formats)
        try:
            response = employees_table.scan(
                FilterExpression='id = :emp_id OR employee_id = :emp_id OR #eid = :emp_id',
                ExpressionAttributeNames={'#eid': 'Employee Id'},
                ExpressionAttributeValues={':emp_id': employee_id}
            )
            
            if not response['Items']:
                print(f'DELETE: Employee {employee_id} not found')
                return {
                    'statusCode': 404,
                    'headers': get_cors_headers(),
                    'body': json.dumps({'error': 'Employee not found'})
                }
            
            employee = response['Items'][0]
            print(f'DELETE: Found employee {employee.get("First Name")} {employee.get("Last Name")}')
            
            # Delete using the actual key from the found item
            employees_table.delete_item(Key={'id': employee['id']})
            print(f'DELETE: Successfully deleted employee {employee_id}')
            
        except Exception as e:
            print(f'DELETE ERROR: Failed to delete employee: {e}')
            return {
                'statusCode': 500,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': f'Database error: {str(e)}'})
            }
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({'message': 'Employee deleted successfully'})
        }
        
    except Exception as e:
        print(f'DELETE ERROR: {e}')
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': str(e)})
        }

def handle_contacts(event):
    if 'requestContext' in event and 'http' in event['requestContext']:
        method = event['requestContext']['http']['method']
    else:
        method = event.get('httpMethod', 'GET')
    
    if method == 'GET':
        response = contacts_table.scan()
        items = response['Items']
        
        for item in items:
            for key, value in item.items():
                if isinstance(value, Decimal):
                    item[key] = float(value)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                },
            'body': json.dumps({'contacts': items})
        }
    
    elif method == 'POST':
        body = json.loads(event['body'])
        action = body.get('action', 'create')
        
        if action == 'bulk_create':
            contacts = body.get('contacts', [])
            
            with contacts_table.batch_writer() as batch:
                for contact in contacts:
                    contact_item = {
                        'id': str(uuid.uuid4()),
                        'name': contact.get('name', ''),
                        'email': contact.get('email', ''),
                        'phone': contact.get('phone', ''),
                        'status': contact.get('status', 'active'),
                        'lists': contact.get('lists', []),
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat()
                    }
                    batch.put_item(Item=contact_item)
            
            return {
                'statusCode': 201,
                'headers': {
                'Content-Type': 'application/json',
                },
                'body': json.dumps({'message': f'{len(contacts)} contacts created'})
            }
        
        else:
            contact = body.get('contact', {})
            contact_item = {
                'id': str(uuid.uuid4()),
                'name': contact.get('name', ''),
                'email': contact.get('email', ''),
                'phone': contact.get('phone', ''),
                'status': contact.get('status', 'active'),
                'lists': contact.get('lists', []),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            contacts_table.put_item(Item=contact_item)
            
            return {
                'statusCode': 201,
                'headers': {
                'Content-Type': 'application/json',
                },
                'body': json.dumps({'id': contact_item['id'], 'message': 'Contact created'})
            }

def handle_collections(event):
    if 'requestContext' in event and 'http' in event['requestContext']:
        method = event['requestContext']['http']['method']
    else:
        method = event.get('httpMethod', 'GET')
    query_params = event.get('queryStringParameters') or {}
    
    if method == 'GET':
        if query_params.get('action') == 'counts':
            response = collections_table.scan()
            items = response['Items']
            
            counts = {
                '0-30': 0,
                '31-60': 0,
                '61-90': 0,
                '91-plus': 0,
                'judgment': 0,
                'resolved': 0
            }
            
            for item in items:
                stage = item.get('stage', '')
                if stage in counts:
                    counts[stage] += 1
            
            return {
                'statusCode': 200,
                'headers': {
                'Content-Type': 'application/json',
                },
                'body': json.dumps({'counts': counts})
            }
        
        else:
            response = collections_table.scan()
            items = response['Items']
            
            for item in items:
                for key, value in item.items():
                    if isinstance(value, Decimal):
                        item[key] = float(value)
            
            return {
                'statusCode': 200,
                'headers': {
                'Content-Type': 'application/json',
                },
                'body': json.dumps({'collections': items})
            }
    
    elif method == 'POST':
        body = json.loads(event['body'])
        action = body.get('action', 'create')
        
        if action == 'bulk_create':
            collections = body.get('collections', [])
            
            with collections_table.batch_writer() as batch:
                for collection in collections:
                    collection_item = {
                        'id': str(uuid.uuid4()),
                        'name': collection.get('name', ''),
                        'email': collection.get('email', ''),
                        'phone': collection.get('phone', ''),
                        'amount': Decimal(str(collection.get('amount', 0))),
                        'install_date': collection.get('installDate', ''),
                        'stage': collection.get('stage', '0-30'),
                        'status': collection.get('status', 'active'),
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat()
                    }
                    batch.put_item(Item=collection_item)
            
            return {
                'statusCode': 201,
                'headers': {
                'Content-Type': 'application/json',
                },
                'body': json.dumps({'message': f'{len(collections)} collections created'})
            }
        
        else:
            collection = body.get('collection', {})
            collection_item = {
                'id': str(uuid.uuid4()),
                'name': collection.get('name', ''),
                'email': collection.get('email', ''),
                'phone': collection.get('phone', ''),
                'amount': Decimal(str(collection.get('amount', 0))),
                'install_date': collection.get('installDate', ''),
                'stage': collection.get('stage', '0-30'),
                'status': collection.get('status', 'active'),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            collections_table.put_item(Item=collection_item)
            
            return {
                'statusCode': 201,
                'headers': {
                'Content-Type': 'application/json',
                },
                'body': json.dumps({'id': collection_item['id'], 'message': 'Collection created'})
            }

def handle_config(event):
    if 'requestContext' in event and 'http' in event['requestContext']:
        method = event['requestContext']['http']['method']
    else:
        method = event.get('httpMethod', 'GET')
    
    if method == 'GET':
        try:
            response = config_table.get_item(Key={'id': 'system_config'})
            config = response.get('Item', {
                'statuses': ['active', 'inactive', 'do-not-contact'],
                'lists': ['leads', 'customers', 'prospects'],
                'customFields': []
            })
            
            return {
                'statusCode': 200,
                'headers': {
                'Content-Type': 'application/json',
                },
                'body': json.dumps(config)
            }
        except:
            return {
                'statusCode': 200,
                'headers': {
                'Content-Type': 'application/json',
                },
                'body': json.dumps({
                    'statuses': ['active', 'inactive', 'do-not-contact'],
                    'lists': ['leads', 'customers', 'prospects'],
                    'customFields': []
                })
            }
    
    elif method == 'POST':
        body = json.loads(event['body'])
        config = body.get('config', {})
        
        config_item = {
            'id': 'system_config',
            'statuses': config.get('statuses', ['active', 'inactive', 'do-not-contact']),
            'lists': config.get('lists', ['leads', 'customers', 'prospects']),
            'customFields': config.get('customFields', []),
            'updated_at': datetime.now().isoformat()
        }
        
        config_table.put_item(Item=config_item)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                },
            'body': json.dumps({'message': 'Config saved'})
        }

def handle_admin_users(event):
    if 'requestContext' in event and 'http' in event['requestContext']:
        method = event['requestContext']['http']['method']
    else:
        method = event.get('httpMethod', 'GET')
    
    # Handle action-based requests
    try:
        body = json.loads(event.get('body', '{}'))
        if body.get('action') == 'get_admin_users':
            method = 'GET'
    except:
        pass
    
    if method == 'GET':
        try:
            if admin_users_table:
                response = admin_users_table.scan()
                admin_users = response['Items']
                
                for user in admin_users:
                    for key, value in user.items():
                        if isinstance(value, Decimal):
                            user[key] = float(value)
            else:
                admin_users = []
            
            return {
                'statusCode': 200,
                'headers': get_cors_headers(),
                'body': json.dumps({'users': admin_users})
            }
        except Exception as e:
            print(f'Error loading admin users: {e}')
            return {
                'statusCode': 500,
                'headers': get_cors_headers(),
                'body': json.dumps({'success': False, 'message': 'Error loading admin users'})
            }
    
    elif method == 'POST':
        try:
            body = json.loads(event['body'])
            email = body.get('email')
            password = body.get('password')
            role = body.get('role', 'admin')
            permissions = body.get('permissions', [])
            
            if not email or not password or not admin_users_table:
                return {
                    'statusCode': 400,
                    'headers': get_cors_headers(),
                    'body': json.dumps({'success': False, 'message': 'Email and password required'})
                }
            
            try:
                existing = admin_users_table.get_item(Key={'email': email})
                if 'Item' in existing:
                    return {
                        'statusCode': 400,
                        'headers': get_cors_headers(),
                        'body': json.dumps({'success': False, 'message': 'Admin user already exists'})
                    }
            except Exception as e:
                print(f'Error checking existing user: {e}')
            
            admin_user = {
                'email': email,
                'password': password,
                'role': role,
                'permissions': permissions,
                'active': True,
                'created_at': datetime.now().isoformat()
            }
            
            admin_users_table.put_item(Item=admin_user)
            
            return {
                'statusCode': 201,
                'headers': get_cors_headers(),
                'body': json.dumps({'success': True, 'message': 'Admin user created successfully'})
            }
        except Exception as e:
            print(f'Error creating admin user: {e}')
            return {
                'statusCode': 500,
                'headers': get_cors_headers(),
                'body': json.dumps({'success': False, 'message': 'Error creating admin user'})
            }

def handle_points(event):
    if 'requestContext' in event and 'http' in event['requestContext']:
        method = event['requestContext']['http']['method']
        path = event['requestContext']['http']['path']
    else:
        method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
    
    if method == 'GET':
        # Get points for specific employee or all employees
        if path.startswith('/points/'):
            emp_id = path.split('/')[-1]
            try:
                response = employees_table.scan(
                    FilterExpression='id = :emp_id OR employee_id = :emp_id OR #eid = :emp_id',
                    ExpressionAttributeNames={'#eid': 'Employee Id'},
                    ExpressionAttributeValues={':emp_id': emp_id}
                )
                if response['Items']:
                    emp = response['Items'][0]
                    return {
                        'statusCode': 200,
                        'headers': {
                'Content-Type': 'application/json',
                },
                        'body': json.dumps({
                            'employee_id': emp_id,
                            'name': f"{emp.get('First Name', '')} {emp.get('Last Name', '')}".strip(),
                            'points': float(emp.get('points', emp.get('Panda Points', 0)) or 0),
                            'total_received': float(emp.get('points', emp.get('Panda Points', 0)) or 0),
                            'department': emp.get('Department', ''),
                            'supervisor': emp.get('supervisor', '')
                        })
                    }
                else:
                    return {
                        'statusCode': 404,
                        'headers': {
                'Content-Type': 'application/json',
                },
                        'body': json.dumps({'error': 'Employee not found'})
                    }
            except Exception as e:
                return {
                    'statusCode': 500,
                    'headers': {
                'Content-Type': 'application/json',
                },
                    'body': json.dumps({'error': str(e)})
                }
        else:
            # Get all employee points
            try:
                response = employees_table.scan()
                points_data = []
                for emp in response['Items']:
                    points_data.append({
                        'employee_id': emp.get('id', emp.get('employee_id', '')),
                        'name': f"{emp.get('First Name', '')} {emp.get('Last Name', '')}".strip(),
                        'points': float(emp.get('points', emp.get('Panda Points', 0)) or 0),
                        'department': emp.get('Department', ''),
                        'supervisor': emp.get('supervisor', '')
                    })
                return {
                    'statusCode': 200,
                    'headers': {
                'Content-Type': 'application/json',
                },
                    'body': json.dumps({'employees': points_data})
                }
            except Exception as e:
                return {
                    'statusCode': 500,
                    'headers': {
                'Content-Type': 'application/json',
                },
                    'body': json.dumps({'error': str(e)})
                }

def handle_gift_cards(event):
    if 'requestContext' in event and 'http' in event['requestContext']:
        method = event['requestContext']['http']['method']
    else:
        method = event.get('httpMethod', 'POST')
    
    if method == 'POST':
        try:
            body = json.loads(event.get('body', '{}'))
            employee_id = body.get('employee_id')
            points_to_redeem = int(body.get('points', 0))
            
            if not employee_id or points_to_redeem <= 0:
                return {
                    'statusCode': 400,
                    'headers': get_cors_headers(),
                    'body': json.dumps({'error': 'Employee ID and points required'})
                }
            
            # Get employee data
            response = employees_table.scan(
                FilterExpression='id = :emp_id OR employee_id = :emp_id',
                ExpressionAttributeValues={':emp_id': employee_id}
            )
            
            if not response['Items']:
                return {
                    'statusCode': 404,
                    'headers': get_cors_headers(),
                    'body': json.dumps({'error': 'Employee not found'})
                }
            
            employee = response['Items'][0]
            current_points = float(employee.get('points', employee.get('Panda Points', 0)) or 0)
            
            if current_points < points_to_redeem:
                return {
                    'statusCode': 400,
                    'headers': get_cors_headers(),
                    'body': json.dumps({'error': 'Insufficient points balance'})
                }
            
            # Create Shopify gift card
            gift_card_code = create_shopify_gift_card(points_to_redeem, employee)
            
            if gift_card_code:
                # Deduct points from employee
                new_balance = current_points - points_to_redeem
                employees_table.put_item(Item={
                    **employee,
                    'points': Decimal(str(new_balance)),
                    'Panda Points': Decimal(str(new_balance)),
                    'updated_at': datetime.now().isoformat()
                })
                
                # Record redemption
                redemption_record = {
                    'id': str(uuid.uuid4()),
                    'employee_id': employee_id,
                    'employee_name': f"{employee.get('First Name', '')} {employee.get('Last Name', '')}".strip(),
                    'points_redeemed': points_to_redeem,
                    'gift_card_code': gift_card_code,
                    'gift_card_value': points_to_redeem,
                    'redeemed_at': datetime.now().isoformat(),
                    'status': 'active'
                }
                
                # Store in points history or create redemptions table
                points_history_table.put_item(Item={
                    'id': str(uuid.uuid4()),
                    'employee_id': employee_id,
                    'employee_name': redemption_record['employee_name'],
                    'points': Decimal(str(-points_to_redeem)),
                    'reason': f'Gift card redemption: {gift_card_code}',
                    'awarded_by': 'system',
                    'awarded_by_name': 'Automated Redemption',
                    'date': datetime.now().isoformat(),
                    'created_at': datetime.now().isoformat(),
                    'type': 'redemption',
                    'gift_card_code': gift_card_code
                })
                
                return {
                    'statusCode': 200,
                    'headers': get_cors_headers(),
                    'body': json.dumps({
                        'success': True,
                        'gift_card_code': gift_card_code,
                        'value': points_to_redeem,
                        'new_balance': new_balance,
                        'message': f'Successfully redeemed {points_to_redeem} points for ${points_to_redeem} gift card'
                    })
                }
            else:
                return {
                    'statusCode': 500,
                    'headers': get_cors_headers(),
                    'body': json.dumps({'error': 'Failed to create gift card'})
                }
                
        except Exception as e:
            print(f'Gift card redemption error: {e}')
            return {
                'statusCode': 500,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Redemption failed'})
            }
    
    return {
        'statusCode': 405,
        'headers': get_cors_headers(),
        'body': json.dumps({'error': 'Method not allowed'})
    }

def get_shopify_credentials():
    """Get Shopify credentials from AWS Secrets Manager"""
    import json
    
    secrets_client = boto3.client('secretsmanager', region_name='us-east-2')
    
    try:
        response = secrets_client.get_secret_value(SecretId='shopify/my-cred')
        secret = json.loads(response['SecretString'])
        return 'pandaexteriors', secret.get('access_token', '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')
    except Exception as e:
        print(f'Error retrieving Shopify credentials: {e}')
        # Fallback with working credentials for testing
        return 'pandaexteriors', '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'

def create_shopify_gift_card(value, employee):
    import requests
    
    # Get Shopify credentials from AWS Secrets Manager
    SHOPIFY_STORE, SHOPIFY_ACCESS_TOKEN = get_shopify_credentials()
    
    if not SHOPIFY_ACCESS_TOKEN:
        print('Shopify access token not available')
        return None
    
    url = f'https://{SHOPIFY_STORE}.myshopify.com/admin/api/2023-10/gift_cards.json'
    headers = {
        'X-Shopify-Access-Token': SHOPIFY_ACCESS_TOKEN,
        'Content-Type': 'application/json'
    }
    
    gift_card_data = {
        'gift_card': {
            'initial_value': str(value),
            'note': f'Panda Points Redemption - {employee.get("First Name", "")} {employee.get("Last Name", "")} (ID: {employee.get("id", employee.get("employee_id", ""))})',
            'expires_on': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
        }
    }
    
    print(f'DEBUG: Creating gift card at URL: {url}')
    print(f'DEBUG: Store: {SHOPIFY_STORE}, Token: {SHOPIFY_ACCESS_TOKEN[:10]}...')
    print(f'DEBUG: Gift card data: {gift_card_data}')
    
    try:
        response = requests.post(url, headers=headers, json=gift_card_data, timeout=30)
        print(f'DEBUG: Response status: {response.status_code}')
        print(f'DEBUG: Response text: {response.text}')
        
        if response.status_code == 201:
            gift_card = response.json()['gift_card']
            return gift_card['code']
        else:
            print(f'Shopify API error: {response.status_code} - {response.text}')
            return None
    except Exception as e:
        print(f'Shopify API request failed: {e}')
        return None

def handle_points_history(event):
    if 'requestContext' in event and 'http' in event['requestContext']:
        method = event['requestContext']['http']['method']
    else:
        method = event.get('httpMethod', 'GET')
    
    if method == 'GET':
        try:
            response = points_history_table.scan()
            items = response['Items']
            
            # Convert Decimal to float for JSON serialization
            for item in items:
                for key, value in item.items():
                    if isinstance(value, Decimal):
                        item[key] = float(value)
            
            return {
                'statusCode': 200,
                'headers': {
                'Content-Type': 'application/json',
                },
                'body': json.dumps({'history': items})
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {
                'Content-Type': 'application/json',
                },
                'body': json.dumps({'error': str(e), 'history': []})
            }
    
    elif method == 'POST':
        try:
            body = json.loads(event.get('body', '{}'))
            
            history_item = {
                'id': str(uuid.uuid4()),
                'employee_id': body.get('employee_id', ''),
                'employee_name': body.get('employee_name', ''),
                'points': int(body.get('points', 0)),
                'reason': body.get('reason', ''),
                'awarded_by': body.get('awarded_by', ''),
                'awarded_by_name': body.get('awarded_by_name', ''),
                'date': body.get('date', datetime.now().isoformat()),
                'created_at': datetime.now().isoformat()
            }
            
            points_history_table.put_item(Item=history_item)
            
            return {
                'statusCode': 201,
                'headers': {
                'Content-Type': 'application/json',
                },
                'body': json.dumps({'message': 'Points history recorded successfully'})
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {
                'Content-Type': 'application/json',
                },
                'body': json.dumps({'error': str(e)})
            }

def handle_referrals(event):
    if 'requestContext' in event and 'http' in event['requestContext']:
        method = event['requestContext']['http']['method']
        path = event['requestContext']['http']['path']
    else:
        method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
    
    if method == 'GET':
        if path.startswith('/referrals/employee/'):
            employee_id = path.split('/')[-1]
            try:
                response = referrals_table.scan(
                    FilterExpression='referred_by_id = :emp_id',
                    ExpressionAttributeValues={':emp_id': employee_id}
                )
                referrals = response['Items']
                
                for referral in referrals:
                    for key, value in referral.items():
                        if isinstance(value, Decimal):
                            referral[key] = float(value)
                
                return {
                    'statusCode': 200,
                    'headers': {
                'Content-Type': 'application/json',
                },
                    'body': json.dumps({'referrals': referrals})
                }
            except Exception as e:
                return {
                    'statusCode': 500,
                    'headers': {
                'Content-Type': 'application/json',
                },
                    'body': json.dumps({'error': str(e), 'referrals': []})
                }
        else:
            try:
                response = referrals_table.scan()
                referrals = response['Items']
                
                for referral in referrals:
                    for key, value in referral.items():
                        if isinstance(value, Decimal):
                            referral[key] = float(value)
                
                return {
                    'statusCode': 200,
                    'headers': {
                'Content-Type': 'application/json',
                },
                    'body': json.dumps({'referrals': referrals})
                }
            except Exception as e:
                return {
                    'statusCode': 500,
                    'headers': {
                'Content-Type': 'application/json',
                },
                    'body': json.dumps({'error': str(e), 'referrals': []})
                }
    
    elif method == 'POST':
        try:
            body = json.loads(event.get('body', '{}'))
            
            referral_item = {
                'id': str(uuid.uuid4()),
                'name': body.get('name', ''),
                'email': body.get('email', ''),
                'phone': body.get('phone', ''),
                'department': body.get('department', ''),
                'referred_by_id': body.get('referred_by_id', ''),
                'referred_by_name': body.get('referred_by_name', ''),
                'status': body.get('status', 'new'),
                'phone_screen_complete': body.get('phone_screen_complete', False),
                'notes': body.get('notes', ''),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            referrals_table.put_item(Item=referral_item)
            
            # Send email notification
            try:
                send_referral_notification(referral_item)
            except Exception as e:
                print(f'Email notification failed: {e}')
            
            return {
                'statusCode': 201,
                'headers': {
                'Content-Type': 'application/json',
                },
                'body': json.dumps({'message': 'Referral created successfully', 'id': referral_item['id']})
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {
                'Content-Type': 'application/json',
                },
                'body': json.dumps({'error': str(e)})
            }
    
    elif method == 'PUT':
        referral_id = path.split('/')[-1]
        try:
            body = json.loads(event.get('body', '{}'))
            
            response = referrals_table.get_item(Key={'id': referral_id})
            if 'Item' not in response:
                return {
                    'statusCode': 404,
                    'headers': {
                'Content-Type': 'application/json',
                },
                    'body': json.dumps({'error': 'Referral not found'})
                }
            
            referral = response['Item']
            
            for key, value in body.items():
                if key not in ['id', 'created_at']:
                    referral[key] = value
            
            referral['updated_at'] = datetime.now().isoformat()
            
            referrals_table.put_item(Item=referral)
            
            return {
                'statusCode': 200,
                'headers': {
                'Content-Type': 'application/json',
                },
                'body': json.dumps({'message': 'Referral updated successfully'})
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {
                'Content-Type': 'application/json',
                },
                'body': json.dumps({'error': str(e)})
            }
    
    return {
        'statusCode': 404,
        'headers': {
                'Content-Type': 'application/json',
                },
        'body': json.dumps({'error': 'Referrals endpoint not found'})
    }

def handle_employee_login(event):
    if 'requestContext' in event and 'http' in event['requestContext']:
        method = event['requestContext']['http']['method']
    elif 'httpMethod' in event:
        method = event['httpMethod']
    else:
        method = 'POST'
    
    if method != 'POST':
        return {
            'statusCode': 405,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        body = json.loads(event.get('body', '{}'))
        email = body.get('email', '').strip().lower()
        password = body.get('password', '')
        
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Email and password required'})
            }
        
        # Find employee by email (case insensitive)
        try:
            response = employees_table.scan()
            employee = None
            
            for item in response['Items']:
                item_email = item.get('Email', '').strip().lower()
                if item_email == email:
                    employee = item
                    break
            
            if not employee:
                return {
                    'statusCode': 401,
                    'headers': get_cors_headers(),
                    'body': json.dumps({'error': 'Invalid email or password'})
                }
            
            # Check if employee is terminated
            if employee.get('Terminated', 'No') == 'Yes':
                return {
                    'statusCode': 401,
                    'headers': get_cors_headers(),
                    'body': json.dumps({'error': 'Account is inactive'})
                }
            
            # Check password - default is "Panda2025!" or custom password if set
            stored_password = employee.get('password', 'Panda2025!')
            
            if password != stored_password:
                return {
                    'statusCode': 401,
                    'headers': get_cors_headers(),
                    'body': json.dumps({'error': 'Invalid email or password'})
                }
            
            # Update last login timestamp and track login history
            try:
                current_time = datetime.now().isoformat()
                employee['last_login'] = current_time
                
                # Add to login history
                if 'login_history' not in employee:
                    employee['login_history'] = []
                
                login_entry = {
                    'timestamp': current_time,
                    'status': 'Success',
                    'source': 'Employee portal',
                    'ip_address': event.get('requestContext', {}).get('identity', {}).get('sourceIp', 'Unknown')
                }
                
                employee['login_history'].append(login_entry)
                
                # Keep only last 100 login entries
                if len(employee['login_history']) > 100:
                    employee['login_history'] = employee['login_history'][-100:]
                
                employees_table.put_item(Item=employee)
            except Exception as e:
                print(f'Failed to update last login: {e}')
            
            # Successful login - return employee data
            employee_data = {
                'id': employee.get('id', employee.get('employee_id', '')),
                'employee_id': employee.get('id', employee.get('employee_id', '')),
                'name': f"{employee.get('First Name', '')} {employee.get('Last Name', '')}".strip(),
                'first_name': employee.get('First Name', ''),
                'last_name': employee.get('Last Name', ''),
                'email': employee.get('Email', ''),
                'department': employee.get('Department', ''),
                'position': employee.get('Position', ''),
                'points': float(employee.get('points', employee.get('Panda Points', 0)) or 0),
                'supervisor': employee.get('supervisor', ''),
                'manager': employee.get('supervisor', ''),
                'office': employee.get('office', ''),
                'hire_date': employee.get('Employment Date', ''),
                'employment_date': employee.get('Employment Date', ''),
                'last_login': employee.get('last_login'),
                'points_manager': employee.get('points_manager', 'No'),
                'points_budget': employee.get('points_budget', 0),
                'total_points_received': float(employee.get('total_points_received', 0) or 0),
                'total_points_redeemed': float(employee.get('total_points_redeemed', 0) or 0)
            }
            
            return {
                'statusCode': 200,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'success': True,
                    'employee': employee_data,
                    'message': 'Login successful'
                })
            }
            
        except Exception as e:
            print(f'Database error during login: {e}')
            return {
                'statusCode': 500,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Database error'})
            }
            
    except Exception as e:
        print(f'Login error: {e}')
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': 'Server error'})
        }

def send_referral_notification(referral_data):
    try:
        subject = f"New Employee Referral: {referral_data['name']}"
        
        body_html = f"""
        <html>
        <body>
            <h2>New Employee Referral Submitted</h2>
            <p><strong>Referral Details:</strong></p>
            <ul>
                <li><strong>Name:</strong> {referral_data['name']}</li>
                <li><strong>Email:</strong> {referral_data['email']}</li>
                <li><strong>Phone:</strong> {referral_data['phone']}</li>
                <li><strong>Preferred Department(s):</strong> {referral_data['department']}</li>
                <li><strong>Referred By:</strong> {referral_data['referred_by_name']} (ID: {referral_data['referred_by_id']})</li>
                <li><strong>Date Submitted:</strong> {referral_data['created_at']}</li>
            </ul>
            {f'<p><strong>Notes:</strong> {referral_data["notes"]}</p>' if referral_data.get('notes') else ''}
        </body>
        </html>
        """
        
        body_text = f"""
        New Employee Referral Submitted
        
        Referral Details:
        Name: {referral_data['name']}
        Email: {referral_data['email']}
        Phone: {referral_data['phone']}
        Preferred Department(s): {referral_data['department']}
        Referred By: {referral_data['referred_by_name']} (ID: {referral_data['referred_by_id']})
        Date Submitted: {referral_data['created_at']}
        {f'Notes: {referral_data["notes"]}' if referral_data.get('notes') else ''}
        """
        
        ses.send_email(
            Source='noreply@pandaexteriors.com',
            Destination={'ToAddresses': ['robwinters@pandaexteriors.com']},
            Message={
                'Subject': {'Data': subject},
                'Body': {
                    'Html': {'Data': body_html},
                    'Text': {'Data': body_text}
                }
            }
        )
        print(f'Email notification sent for referral: {referral_data["name"]}')
    except Exception as e:
        print(f'Failed to send email notification: {e}')
        raise e

def handle_admin_login(event):
    if 'requestContext' in event and 'http' in event['requestContext']:
        method = event['requestContext']['http']['method']
    elif 'httpMethod' in event:
        method = event['httpMethod']
    else:
        method = 'POST'
    
    if method != 'POST':
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json', },
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        body = json.loads(event.get('body', '{}'))
        email = body.get('email', '').strip().lower()
        password = body.get('password', '')
        
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', },
                'body': json.dumps({'error': 'Email and password required'})
            }
        
        # Check admin users table
        if admin_users_table:
            try:
                response = admin_users_table.get_item(Key={'email': email})
                if 'Item' in response:
                    admin = response['Item']
                    if admin.get('password') == password and admin.get('active', True):
                        return {
                            'statusCode': 200,
                            'headers': {
                                'Content-Type': 'application/json',
                                },
                            'body': json.dumps({
                                'success': True,
                                'admin': {
                                    'email': admin['email'],
                                    'role': admin.get('role', 'admin'),
                                    'permissions': admin.get('permissions', []),
                                    'name': admin.get('name', email)
                                },
                                'message': 'Login successful'
                            })
                        }
            except Exception as e:
                print(f'Error checking admin users: {e}')
        
        # Check if it's a manager/executive employee
        try:
            response = employees_table.scan()
            manager_employee = None
            
            for item in response['Items']:
                item_email = item.get('Email', '').strip().lower()
                if item_email == email:
                    manager_employee = item
                    break
            
            if manager_employee and manager_employee.get('points_manager') == 'Yes':
                # Check password
                stored_password = manager_employee.get('password', 'Panda2025!')
                if password == stored_password:
                    return {
                        'statusCode': 200,
                        'headers': get_cors_headers(),
                        'body': json.dumps({
                            'success': True,
                            'admin': {
                                'email': manager_employee.get('Email', ''),
                                'role': 'points_manager',
                                'permissions': ['points'],
                                'name': f"{manager_employee.get('First Name', '')} {manager_employee.get('Last Name', '')}".strip(),
                                'employee_id': manager_employee.get('id'),
                                'points_budget': float(manager_employee.get('points_budget', 500) or 500)
                            },
                            'message': 'Login successful'
                        })
                    }
        except Exception as e:
            print(f'Error checking manager employees: {e}')
        
        # Fallback to hardcoded admin
        if email == 'admin' and password == 'admin123':
            return {
                'statusCode': 200,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'success': True,
                    'admin': {
                        'email': 'admin',
                        'role': 'super_admin',
                        'permissions': ['employees', 'points', 'referrals', 'leads'],
                        'name': 'System Administrator'
                    },
                    'message': 'Login successful'
                })
            }
        
        return {
            'statusCode': 401,
            'headers': {'Content-Type': 'application/json', },
            'body': json.dumps({'error': 'Invalid email or password'})
        }
        
    except Exception as e:
        print(f'Admin login error: {e}')
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', },
            'body': json.dumps({'error': 'Server error'})
        }

def handle_login_history(event):
    if 'requestContext' in event and 'http' in event['requestContext']:
        path = event['requestContext']['http']['path']
    else:
        path = event.get('path', '/')
    
    emp_id = path.split('/')[-1]
    
    try:
        # Get employee login history from DynamoDB
        response = employees_table.scan(
            FilterExpression='id = :emp_id OR employee_id = :emp_id',
            ExpressionAttributeValues={':emp_id': emp_id}
        )
        
        if not response['Items']:
            return {
                'statusCode': 404,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Employee not found'})
            }
        
        employee = response['Items'][0]
        
        # Get login history from employee record
        login_history = employee.get('login_history', [])
        
        # Filter to last 60 days
        sixty_days_ago = datetime.now() - timedelta(days=60)
        recent_history = []
        
        for login in login_history:
            if isinstance(login, dict) and 'timestamp' in login:
                login_date = datetime.fromisoformat(login['timestamp'].replace('Z', '+00:00'))
                if login_date >= sixty_days_ago:
                    recent_history.append(login)
        
        # Sort by timestamp descending
        recent_history.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({'history': recent_history})
        }
        
    except Exception as e:
        print(f'Login history error: {e}')
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': 'Failed to load login history'})
        }

def create_super_admin(event):
    return {
        'statusCode': 200,
        'headers': {
                'Content-Type': 'application/json',
                },
        'body': json.dumps({'message': 'Super admin already exists'})
    }