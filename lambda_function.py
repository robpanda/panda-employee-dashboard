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
        elif path == '/diagnose-shopify':
            print('LAMBDA DEBUG: Calling diagnose_shopify')
            return diagnose_shopify(event)

        elif path == '/sync-shopify-merchandise':
            print(f'LAMBDA DEBUG: Calling sync_shopify_merchandise')
            return sync_shopify_merchandise(event)
        elif path == '/update-employee-merchandise':
            print(f'LAMBDA DEBUG: Calling update_employee_merchandise')
            return update_employee_merchandise(event)
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
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'method': http_method,
                    'path': path,
                    'event_keys': list(event.keys()),
                    'requestContext': event.get('requestContext', {}),
                    'all_paths_checked': [
                        '/employees', '/contacts', '/collections', '/config',
                        '/admin-users', '/create-admin', '/points', '/points-history',
                        '/referrals', '/employee-login', '/admin-login', '/test'
                    ],
                    'cors_test': 'CORS headers should be present',
                    'timestamp': datetime.now().isoformat()
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
                # Handle Merchandise Value strings with $ and commas
                elif key in ['Merchandise Value', 'merchandise_value'] and isinstance(value, str):
                    try:
                        # Remove $ and commas, then convert to float
                        cleaned = value.replace('$', '').replace(',', '').strip()
                        item[key] = float(cleaned) if cleaned else 0.0
                    except (ValueError, AttributeError):
                        item[key] = 0.0
            
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
                # Handle Merchandise Value strings with $ and commas
                elif key in ['Merchandise Value', 'merchandise_value'] and isinstance(value, str):
                    try:
                        # Remove $ and commas, then convert to float
                        cleaned = value.replace('$', '').replace(',', '').strip()
                        item[key] = float(cleaned) if cleaned else 0.0
                    except (ValueError, AttributeError):
                        item[key] = 0.0
        
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
                # Handle Merchandise Value strings with $ and commas
                elif key in ['Merchandise Value', 'merchandise_value'] and isinstance(value, str):
                    try:
                        # Remove $ and commas, then convert to float
                        cleaned = value.replace('$', '').replace(',', '').strip()
                        item[key] = float(cleaned) if cleaned else 0.0
                    except (ValueError, AttributeError):
                        item[key] = 0.0
            
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

def diagnose_shopify(event):
    """Diagnostic endpoint to understand Shopify data structure"""
    try:
        import urllib.request
        from collections import Counter

        # Get credentials
        try:
            secrets_client = boto3.client('secretsmanager', region_name='us-east-2')
            response = secrets_client.get_secret_value(SecretId='shopify/my-cred')
            secret = json.loads(response['SecretString'])
            access_token = secret.get('access_token')
        except:
            access_token = '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'

        store = 'pandaexteriors'
        url = f"https://{store}.myshopify.com/admin/api/2024-01/orders.json?limit=250&status=any"

        req = urllib.request.Request(url)
        req.add_header('X-Shopify-Access-Token', access_token)
        req.add_header('Content-Type', 'application/json')

        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            orders = data.get('orders', [])

        # Analyze
        ids = [str(o.get('id')) for o in orders]
        order_numbers = [str(o.get('order_number')) for o in orders]
        names = [o.get('name', '') for o in orders]

        # Find Blair's orders
        blair_orders = [o for o in orders if o.get('customer', {}).get('email', '').lower() == 'blairashepherd@gmail.com']

        blair_data = []
        for order in blair_orders:
            blair_data.append({
                'id': order.get('id'),
                'name': order.get('name'),
                'order_number': order.get('order_number'),
                'total_price': order.get('total_price'),
                'created_at': order.get('created_at'),
                'line_items': len(order.get('line_items', []))
            })

        result = {
            'total_orders': len(orders),
            'unique_ids': len(set(ids)),
            'unique_order_numbers': len(set(order_numbers)),
            'unique_names': len(set(names)),
            'order_number_duplicates': {k: v for k, v in Counter(order_numbers).items() if v > 1},
            'name_duplicates': {k: v for k, v in Counter(names).items() if v > 1},
            'blair_orders': blair_data,
            'blair_order_count': len(blair_orders)
        }

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps(result, indent=2)
        }

    except Exception as e:
        import traceback
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'error': str(e),
                'traceback': traceback.format_exc()
            })
        }

def sync_shopify_merchandise(event):
    """
    Shopify sync with CORRECT deduplication strategy:
    1. Use order_number for deduplication (since one logical order may have multiple Shopify IDs)
    2. Keep only the FIRST occurrence of each order_number
    3. Ignore subsequent orders with the same order_number (they're likely edits/updates)
    """
    try:
        import urllib.request

        print('='*80)
        print('SYNC: Starting sync_shopify_merchandise')
        print('='*80)

        # Get Shopify credentials
        try:
            secrets_client = boto3.client('secretsmanager', region_name='us-east-2')
            response = secrets_client.get_secret_value(SecretId='shopify/my-cred')
            secret = json.loads(response['SecretString'])
            access_token = secret.get('access_token', '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')
            print('SYNC: Using credentials from Secrets Manager')
        except Exception as e:
            print(f'SYNC: Using fallback credentials: {e}')
            access_token = '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'

        store = 'pandaexteriors'

        # Fetch all orders from Shopify
        url = f"https://{store}.myshopify.com/admin/api/2024-01/orders.json?limit=250&status=any"
        req = urllib.request.Request(url)
        req.add_header('X-Shopify-Access-Token', access_token)
        req.add_header('Content-Type', 'application/json')

        with urllib.request.urlopen(req) as response:
            shopify_data = json.loads(response.read().decode('utf-8'))
            shopify_orders = shopify_data.get('orders', [])

        print(f'SYNC: Fetched {len(shopify_orders)} orders from Shopify')

        # Get all employees
        employees_response = employees_table.scan()
        all_employees = employees_response['Items']

        # Build email to employee_id mapping AND load existing orders from DB
        email_map = {}
        existing_orders = {}  # {employee_id: set of order_numbers already in DB}

        for emp in all_employees:
            email = emp.get('Email', emp.get('email', '')).lower().strip()
            emp_id = emp.get('id', emp.get('employee_id'))
            if email:
                email_map[email] = emp_id

                # Parse existing orders from DB to prevent re-adding them
                existing_merch = emp.get('Merch Requested', '')
                if existing_merch:
                    existing_order_nums = set()
                    for order_text in existing_merch.split('|'):
                        order_text = order_text.strip()
                        if '[Shopify #' in order_text:
                            try:
                                order_num = order_text.split('[Shopify #')[1].split(']')[0].strip()
                                existing_order_nums.add(order_num)
                            except:
                                pass
                    existing_orders[emp_id] = existing_order_nums
                    if existing_order_nums:
                        print(f'SYNC: Employee {emp_id} ({email}) has {len(existing_order_nums)} existing orders: {existing_order_nums}')
                else:
                    existing_orders[emp_id] = set()

        print(f'SYNC: Processing {len(email_map)} employees with email addresses')

        # Build complete order list per employee
        # KEY CHANGE: Use order_number for deduplication (one logical order may have multiple Shopify IDs)
        # Keep only the FIRST occurrence of each order_number
        employee_data = {}  # {employee_id: {'orders': {order_number: {...}}, 'email': str}}

        errors = []

        # Process each Shopify order
        for idx, shopify_order in enumerate(shopify_orders):
            try:
                # Get customer email
                customer = shopify_order.get('customer')
                if not customer:
                    continue

                customer_email = customer.get('email', '').lower().strip()
                if not customer_email:
                    continue

                # Match to employee
                employee_id = email_map.get(customer_email)
                if not employee_id:
                    errors.append(f"No employee found for {customer_email}")
                    continue

                # Get order number and date - use BOTH as unique identifier
                shopify_id = str(shopify_order.get('id'))
                order_number = str(shopify_order.get('order_number', ''))
                order_name = shopify_order.get('name', '')
                created_at = shopify_order.get('created_at', '')  # e.g., "2024-01-15T10:30:00-05:00"

                # Extract just the date part (YYYY-MM-DD)
                order_date = created_at.split('T')[0] if created_at else ''

                if not order_number:
                    order_number = order_name.replace('#', '').strip()

                # Create unique key: date + order_number (e.g., "2024-01-15:1045")
                unique_key = f"{order_date}:{order_number}" if order_date else order_number

                # ENHANCED LOGGING for Blair
                if customer_email == 'blairashepherd@gmail.com':
                    print(f'BLAIR DEBUG: Shopify ID={shopify_id}, order_number={repr(order_number)}, date={order_date}, unique_key={repr(unique_key)}')

                if not order_number:
                    print(f'SYNC WARNING: Order at index {idx} has no order number')
                    continue

                # Initialize employee data if needed
                if employee_id not in employee_data:
                    employee_data[employee_id] = {'orders': {}, 'email': customer_email}
                    print(f'SYNC: Initialized data for employee {employee_id} ({customer_email})')

                # Check if we already have this order (DEDUP by date+order_number)
                # First check: already processed in THIS sync run
                if unique_key in employee_data[employee_id]['orders']:
                    if customer_email == 'blairashepherd@gmail.com':
                        print(f'BLAIR DEBUG: DEDUP (in-memory) unique_key={repr(unique_key)}')
                    print(f'SYNC DEDUP: Already processed in this run: {unique_key} (Shopify ID {shopify_id}) for {customer_email}')
                    continue

                # Second check: already exists in DB (don't re-add existing orders!)
                if order_number in existing_orders.get(employee_id, set()):
                    if customer_email == 'blairashepherd@gmail.com':
                        print(f'BLAIR DEBUG: DEDUP (from DB) order_number={repr(order_number)}, DB has: {existing_orders.get(employee_id, set())}')
                    print(f'SYNC DEDUP: Already exists in DB: order #{order_number} for {customer_email}')
                    continue

                # Build item description
                line_items = shopify_order.get('line_items', [])
                items_text = ', '.join([
                    f"{item.get('title', 'Item')} (x{item.get('quantity', 1)})"
                    for item in line_items
                ])

                # Store order data using unique_key (date:order_number) as key
                total_price = float(shopify_order.get('total_price', '0') or '0')
                employee_data[employee_id]['orders'][unique_key] = {
                    'order_number': order_number,
                    'order_date': order_date,
                    'unique_key': unique_key,
                    'text': f"[Shopify #{order_number}] {items_text}",
                    'total': total_price,
                    'status': shopify_order.get('fulfillment_status', 'pending')
                }

                if customer_email == 'blairashepherd@gmail.com':
                    print(f'BLAIR DEBUG: ADDED unique_key={repr(unique_key)}, dict keys now={list(employee_data[employee_id]["orders"].keys())}')
                print(f'SYNC: Added order {unique_key} (Shopify ID {shopify_id}) for {customer_email} (${total_price:.2f})')

            except Exception as e:
                print(f'SYNC ERROR processing order at index {idx}: {e}')
                errors.append(f"Order processing error: {str(e)}")

        print(f'\nSYNC: Finished processing orders. Found {len(employee_data)} employees with orders')

        # Update all employees
        synced_count = 0

        # Also process employees who only have existing orders (to keep their data)
        for emp in all_employees:
            emp_id = emp.get('id', emp.get('employee_id'))
            if emp_id in existing_orders and existing_orders[emp_id] and emp_id not in employee_data:
                # This employee has existing orders but no new ones from Shopify
                # Keep their existing data (don't zero it out)
                print(f'SYNC: Employee {emp_id} has existing orders but no new ones - preserving data')

        for employee_id, data in employee_data.items():
            try:
                # Get existing orders from DB for THIS employee
                emp_existing_orders = existing_orders.get(employee_id, set())

                # MERGE: Combine new orders (from Shopify) with existing orders (from DB)
                # The new orders are in data['orders'], the existing ones need to be preserved
                new_order_texts = [order_data['text'] for order_data in data['orders'].values()]
                new_total = sum(order_data['total'] for order_data in data['orders'].values())

                # Get the employee's current DB record to extract existing orders text
                emp_record = next((e for e in all_employees if e.get('id') == employee_id), None)
                if emp_record:
                    existing_merch = emp_record.get('Merch Requested', '')
                    existing_value_str = emp_record.get('Merchandise Value', '$0.00')
                    try:
                        existing_value = float(existing_value_str.replace('$', '').replace(',', ''))
                    except:
                        existing_value = 0.0

                    # Preserve existing order texts
                    if existing_merch:
                        existing_order_texts = [o.strip() for o in existing_merch.split('|') if o.strip()]
                    else:
                        existing_order_texts = []

                    # Combine: existing + new
                    all_order_texts = existing_order_texts + new_order_texts
                    merch_text = ' | '.join(all_order_texts)
                    total_value = existing_value + new_total
                else:
                    # No existing record (shouldn't happen, but handle it)
                    merch_text = ' | '.join(new_order_texts)
                    total_value = new_total

                print(f'\nSYNC: Updating employee {employee_id}:')
                print(f'  Email: {data["email"]}')
                print(f'  NEW orders from Shopify: {len(data["orders"])}')
                print(f'  New order numbers: {list(data["orders"].keys())}')
                print(f'  TOTAL orders after merge: {len(all_order_texts) if emp_record else len(new_order_texts)}')
                print(f'  Value: ${total_value:.2f}')

                # Update employee record - now with MERGED data
                employees_table.update_item(
                    Key={'id': employee_id},
                    UpdateExpression='SET #merch = :merch, #value = :value, updated_at = :timestamp',
                    ExpressionAttributeNames={
                        '#merch': 'Merch Requested',
                        '#value': 'Merchandise Value'
                    },
                    ExpressionAttributeValues={
                        ':merch': merch_text,
                        ':value': f'${total_value:.2f}',
                        ':timestamp': datetime.now().isoformat()
                    }
                )

                synced_count += 1
                print(f'SYNC: ✓ Successfully updated {data["email"]}')

            except Exception as e:
                print(f'SYNC ERROR updating {employee_id}: {e}')
                import traceback
                traceback.print_exc()
                errors.append(f"Update error for {employee_id}: {str(e)}")

        print(f'\n{"="*80}')
        print(f'SYNC: Completed - synced {synced_count} employees')
        print(f'SYNC: Errors: {len(errors)}')
        print(f'{"="*80}')

        # CLEANUP: Remove any duplicate orders that may have slipped through
        print(f'\n{"="*80}')
        print('CLEANUP: Starting automatic duplicate removal...')
        print(f'{"="*80}')

        cleanup_count = 0
        employees_response = employees_table.scan()
        all_employees_after = employees_response['Items']

        for emp in all_employees_after:
            emp_id = emp.get('id', emp.get('employee_id'))
            merch_requested = emp.get('Merch Requested', '')

            if not merch_requested or '|' not in merch_requested:
                continue  # No orders or only one order

            # Parse orders
            orders = [o.strip() for o in merch_requested.split('|') if o.strip()]

            # Deduplicate by order number
            seen_order_numbers = set()
            unique_orders = []
            removed_count = 0

            for order in orders:
                if '[Shopify #' in order:
                    try:
                        order_num = order.split('[Shopify #')[1].split(']')[0].strip()
                        if order_num not in seen_order_numbers:
                            seen_order_numbers.add(order_num)
                            unique_orders.append(order)
                        else:
                            removed_count += 1
                    except:
                        unique_orders.append(order)  # Keep if we can't parse
                else:
                    unique_orders.append(order)  # Keep non-Shopify orders

            # If duplicates were found, update the record
            if removed_count > 0:
                new_merch = ' | '.join(unique_orders)

                # Recalculate value (divide by the ratio of duplicates)
                old_value_str = emp.get('Merchandise Value', '$0.00')
                try:
                    old_value = float(old_value_str.replace('$', '').replace(',', ''))
                    new_value = old_value * len(unique_orders) / len(orders)
                except:
                    new_value = 0.0

                employees_table.update_item(
                    Key={'id': emp_id},
                    UpdateExpression='SET #merch = :merch, #value = :value',
                    ExpressionAttributeNames={
                        '#merch': 'Merch Requested',
                        '#value': 'Merchandise Value'
                    },
                    ExpressionAttributeValues={
                        ':merch': new_merch,
                        ':value': f'${new_value:.2f}'
                    }
                )

                emp_name = f"{emp.get('First Name', '')} {emp.get('Last Name', '')}"
                print(f'CLEANUP: ✓ Cleaned {emp_name}: {len(orders)} → {len(unique_orders)} orders')
                cleanup_count += 1

        print(f'\nCLEANUP: Cleaned {cleanup_count} employee records')
        print(f'{"="*80}')

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'success': True,
                'synced': synced_count,
                'cleaned': cleanup_count,
                'message': f'Successfully synced {synced_count} employees and cleaned {cleanup_count} duplicates',
                'total_orders': len(shopify_orders),
                'matched_employees': len(employee_data),
                'errors': errors[:10]
            })
        }

    except Exception as e:
        print(f'SYNC CRITICAL ERROR: {e}')
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }

def update_employee_merchandise(event):
    """
    Manually update an employee's merchandise orders and value
    POST /update-employee-merchandise
    Body: {
        "employee_id": "10701",
        "merch_requested": "[Shopify #1045] Items...",
        "merchandise_value": "$1663.20"
    }
    """
    try:
        body = json.loads(event.get('body', '{}'))
        employee_id = body.get('employee_id')
        merch_requested = body.get('merch_requested', '')
        merchandise_value = body.get('merchandise_value', '$0.00')

        if not employee_id:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'success': False, 'error': 'employee_id is required'})
            }

        print(f'UPDATE MERCH: Updating employee {employee_id}')
        print(f'  Merch: {merch_requested[:100]}...')
        print(f'  Value: {merchandise_value}')

        # Update the employee record
        employees_table.update_item(
            Key={'id': employee_id},
            UpdateExpression='SET #merch = :merch, #value = :value, updated_at = :timestamp',
            ExpressionAttributeNames={
                '#merch': 'Merch Requested',
                '#value': 'Merchandise Value'
            },
            ExpressionAttributeValues={
                ':merch': merch_requested,
                ':value': merchandise_value,
                ':timestamp': datetime.now().isoformat()
            }
        )

        print(f'UPDATE MERCH: ✓ Successfully updated employee {employee_id}')

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'success': True,
                'message': 'Employee merchandise updated successfully',
                'employee_id': employee_id
            })
        }

    except Exception as e:
        print(f'ERROR updating merchandise: {e}')
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'success': False, 'error': str(e)})
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
                # Handle Merchandise Value strings with $ and commas
                elif key in ['Merchandise Value', 'merchandise_value'] and isinstance(value, str):
                    try:
                        # Remove $ and commas, then convert to float
                        cleaned = value.replace('$', '').replace(',', '').strip()
                        item[key] = float(cleaned) if cleaned else 0.0
                    except (ValueError, AttributeError):
                        item[key] = 0.0
            
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
                    'headers': get_cors_headers(),
                    'body': json.dumps({'referrals': referrals})
                }
            except Exception as e:
                return {
                    'statusCode': 500,
                    'headers': get_cors_headers(),
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
                    'headers': get_cors_headers(),
                    'body': json.dumps({'referrals': referrals})
                }
            except Exception as e:
                return {
                    'statusCode': 500,
                    'headers': get_cors_headers(),
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
                'headers': get_cors_headers(),
                'body': json.dumps({'message': 'Referral created successfully', 'id': referral_item['id']})
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': get_cors_headers(),
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
                    'headers': get_cors_headers(),
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
                'headers': get_cors_headers(),
                'body': json.dumps({'message': 'Referral updated successfully'})
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': str(e)})
            }
    
    return {
        'statusCode': 404,
        'headers': get_cors_headers(),
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
            print(f'ADMIN_LOGIN: Scanning for manager employee with email: {email}')
            response = employees_table.scan()
            manager_employee = None
            
            print(f'ADMIN_LOGIN: Scanned {len(response["Items"])} employees')
            
            for item in response['Items']:
                item_email = item.get('Email', '').strip().lower()
                print(f'ADMIN_LOGIN: Checking email: "{item_email}" vs "{email}"')
                if item_email == email:
                    manager_employee = item
                    print(f'ADMIN_LOGIN: Found matching employee: {item.get("First Name")} {item.get("Last Name")}')
                    break
            
            if manager_employee:
                print(f'ADMIN_LOGIN: Employee found, points_manager: {manager_employee.get("points_manager")}')
                if manager_employee.get('points_manager') == 'Yes':
                    # No password check needed for points managers - just verify they have the checkbox
                    print(f'ADMIN_LOGIN: Points manager found! Granting access')
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
                                'points_budget': float(manager_employee.get('points_budget', 500) or 500),
                                'restricted_access': True
                            },
                            'message': 'Login successful'
                        })
                    }
                else:
                    print(f'ADMIN_LOGIN: Employee is not a points manager')
            else:
                print(f'ADMIN_LOGIN: No employee found with email: {email}')
        except Exception as e:
            print(f'Error checking manager employees: {e}')
        
        # Fallback to hardcoded admin (still requires password)
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
                        'name': 'System Administrator',
                        'restricted_access': False
                    },
                    'message': 'Login successful'
                })
            }
        
        print(f'ADMIN_LOGIN: All checks failed, returning 401')
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