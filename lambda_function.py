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
        
        # Clear existing data
        try:
            response = employees_table.scan()
            print(f'Found {len(response["Items"])} existing employees to clear')
            with employees_table.batch_writer() as batch:
                for item in response['Items']:
                    key_value = item.get('id', item.get('employee_id', item.get('Employee Id', '')))
                    if key_value:
                        batch.delete_item(Key={'id': key_value})
            print('Successfully cleared existing data')
        except Exception as e:
            print(f'Error clearing data: {e}')
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    },
                'body': json.dumps({'error': f'Failed to clear data: {str(e)}'})
            }
        
        # Insert new employees
        success_count = 0
        with employees_table.batch_writer() as batch:
            for emp_data in employees_data:
                try:
                    # Handle both frontend format and API format
                    emp_id = emp_data.get('Employee Id', emp_data.get('employee_id', emp_data.get('id', str(uuid.uuid4()))))
                    if not emp_id:
                        emp_id = str(uuid.uuid4())
                    
                    employee = {
                        'id': str(emp_id),
                        'employee_id': str(emp_id),
                        'Employee Id': str(emp_id),
                        'First Name': emp_data.get('First Name', emp_data.get('first_name', '')),
                        'Last Name': emp_data.get('Last Name', emp_data.get('last_name', '')),
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
                        'updated_at': datetime.now().isoformat()
                    }
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
    employee_id = event['pathParameters']['employee_id']
    
    employees_table.delete_item(Key={'employee_id': employee_id})
    
    return {
        'statusCode': 200,
        'headers': {
                'Content-Type': 'application/json',
                },
        'body': json.dumps({'message': 'Employee deleted successfully'})
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
                'headers': {
                    'Content-Type': 'application/json',
                    },
                'body': json.dumps({'users': admin_users})
            }
        except Exception as e:
            print(f'Error loading admin users: {e}')
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    },
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
                    'headers': {
                        'Content-Type': 'application/json',
                        },
                    'body': json.dumps({'success': False, 'message': 'Email and password required'})
                }
            
            try:
                existing = admin_users_table.get_item(Key={'email': email})
                if 'Item' in existing:
                    return {
                        'statusCode': 400,
                        'headers': {
                            'Content-Type': 'application/json',
                            },
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
                'headers': {
                    'Content-Type': 'application/json',
                    },
                'body': json.dumps({'success': True, 'message': 'Admin user created successfully'})
            }
        except Exception as e:
            print(f'Error creating admin user: {e}')
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    },
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
            'headers': {
                'Content-Type': 'application/json',
                },
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        body = json.loads(event.get('body', '{}'))
        email = body.get('email', '').strip().lower()
        password = body.get('password', '')
        
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    },
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
                    'headers': {
                        'Content-Type': 'application/json',
                        },
                    'body': json.dumps({'error': 'Invalid email or password'})
                }
            
            # Check if employee is terminated
            if employee.get('Terminated', 'No') == 'Yes':
                return {
                    'statusCode': 401,
                    'headers': {
                        'Content-Type': 'application/json',
                        },
                    'body': json.dumps({'error': 'Account is inactive'})
                }
            
            # Check password - default is "Panda2025!" or custom password if set
            stored_password = employee.get('password', 'Panda2025!')
            
            if password != stored_password:
                return {
                    'statusCode': 401,
                    'headers': {
                        'Content-Type': 'application/json',
                        },
                    'body': json.dumps({'error': 'Invalid email or password'})
                }
            
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
                'office': employee.get('office', '')
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    },
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
                'headers': {
                    'Content-Type': 'application/json',
                    },
                'body': json.dumps({'error': 'Database error'})
            }
            
    except Exception as e:
        print(f'Login error: {e}')
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                },
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
        
        # Fallback to hardcoded admin
        if email == 'admin' and password == 'admin123':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    },
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

def create_super_admin(event):
    return {
        'statusCode': 200,
        'headers': {
                'Content-Type': 'application/json',
                },
        'body': json.dumps({'message': 'Super admin already exists'})
    }