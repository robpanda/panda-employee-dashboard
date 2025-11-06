import json
import boto3
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')

# Fleet tables
vehicles_table = dynamodb.Table('panda-fleet-vehicles')
accidents_table = dynamodb.Table('panda-fleet-accidents')
ezpass_table = dynamodb.Table('panda-fleet-ezpass')
sales_table = dynamodb.Table('panda-fleet-sales')
maintenance_table = dynamodb.Table('panda-fleet-maintenance')
requests_table = dynamodb.Table('panda-fleet-requests')

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization'
    }

    try:
        method = event['httpMethod']
        path = event['path']

        if method == 'OPTIONS':
            return {'statusCode': 200, 'headers': headers, 'body': ''}

        # Vehicle endpoints
        if '/vehicles' in path:
            if method == 'GET':
                return get_vehicles(event, headers)
            elif method == 'POST':
                return create_vehicle(event, headers)
            elif method == 'PUT':
                return update_vehicle(event, headers)
            elif method == 'DELETE':
                return delete_vehicle(event, headers)

        # Accident endpoints
        elif '/accidents' in path:
            if method == 'GET':
                return get_accidents(event, headers)
            elif method == 'POST':
                return create_accident(event, headers)
            elif method == 'PUT':
                return update_accident(event, headers)

        # EZ Pass endpoints
        elif '/ezpass' in path:
            if method == 'GET':
                return get_ezpass(event, headers)
            elif method == 'POST':
                return create_ezpass(event, headers)
            elif method == 'PUT':
                return update_ezpass(event, headers)

        # Sales endpoints
        elif '/sales' in path:
            if method == 'GET':
                return get_sales(event, headers)
            elif method == 'POST':
                return create_sale(event, headers)

        # Maintenance endpoints
        elif '/maintenance' in path:
            if method == 'GET':
                return get_maintenance(event, headers)
            elif method == 'POST':
                return create_maintenance(event, headers)
            elif method == 'PUT':
                return update_maintenance(event, headers)

        # Vehicle request endpoints
        elif '/requests' in path:
            if method == 'GET':
                return get_requests(event, headers)
            elif method == 'POST':
                return create_request(event, headers)
            elif method == 'PUT':
                return update_request(event, headers)

        # Check-in/Check-out endpoints
        elif '/checkout' in path and method == 'POST':
            return checkout_vehicle(event, headers)
        elif '/checkin' in path and method == 'POST':
            return checkin_vehicle(event, headers)

        # Dashboard/Stats endpoints
        elif '/fleet-stats' in path and method == 'GET':
            return get_fleet_stats(headers)
        elif '/overdue-maintenance' in path and method == 'GET':
            return get_overdue_maintenance(headers)

        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({'error': 'Endpoint not found'})
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }

# ============= VEHICLE OPERATIONS =============

def get_vehicles(event, headers):
    """Get all vehicles or filter by status, driver, department, etc."""
    query_params = event.get('queryStringParameters', {}) or {}

    response = vehicles_table.scan()
    vehicles = response.get('Items', [])

    # Apply filters
    if 'status' in query_params:
        vehicles = [v for v in vehicles if v.get('status') == query_params['status']]

    if 'driver_email' in query_params:
        vehicles = [v for v in vehicles if v.get('driver_email') == query_params['driver_email']]

    if 'department' in query_params:
        vehicles = [v for v in vehicles if v.get('department') == query_params['department']]

    if 'territory' in query_params:
        vehicles = [v for v in vehicles if v.get('territory') == query_params['territory']]

    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(vehicles, default=decimal_default)
    }

def create_vehicle(event, headers):
    """Create a new vehicle record"""
    data = json.loads(event['body'])

    vehicle_id = data.get('vehicle_id') or f"PANDA-{str(uuid.uuid4())[:8].upper()}"

    vehicle = {
        'vehicle_id': vehicle_id,
        'asset_name': data.get('asset_name', ''),
        'year': data.get('year', ''),
        'make': data.get('make', ''),
        'model': data.get('model', ''),
        'vin': data.get('vin', ''),
        'license_plate': data.get('license_plate', ''),
        'title_number': data.get('title_number', ''),
        'status': data.get('status', 'floater'),
        'department': data.get('department', ''),
        'current_driver': data.get('current_driver', ''),
        'driver_email': data.get('driver_email', ''),
        'driver_phone': data.get('driver_phone', ''),
        'driver_manager': data.get('driver_manager', ''),
        'territory': data.get('territory', ''),
        'location': data.get('location', ''),
        'panda_phone': data.get('panda_phone', ''),
        'ez_pass_id': data.get('ez_pass_id', ''),
        'registration_expiration': data.get('registration_expiration', ''),
        'insurance_expiration': data.get('insurance_expiration', ''),
        'emissions_due': data.get('emissions_due', ''),
        'mileage': int(data.get('mileage', 0)),
        'unit_value': Decimal(str(data.get('unit_value', 0))),
        'comments': data.get('comments', ''),
        'gaf_presenter': data.get('gaf_presenter', False),
        'camera_installed': data.get('camera_installed', False),
        'vanity_ordered': data.get('vanity_ordered', False),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }

    vehicles_table.put_item(Item=vehicle)

    return {
        'statusCode': 201,
        'headers': headers,
        'body': json.dumps({'message': 'Vehicle created successfully', 'vehicle_id': vehicle_id})
    }

def update_vehicle(event, headers):
    """Update an existing vehicle"""
    data = json.loads(event['body'])
    vehicle_id = data.get('vehicle_id')

    if not vehicle_id:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': 'vehicle_id is required'})
        }

    update_expr = 'SET updated_at = :updated_at'
    expr_values = {':updated_at': datetime.now().isoformat()}

    # Build dynamic update expression
    updatable_fields = [
        'asset_name', 'year', 'make', 'model', 'vin', 'license_plate', 'title_number',
        'status', 'department', 'current_driver', 'driver_email', 'driver_phone',
        'driver_manager', 'territory', 'location', 'panda_phone', 'ez_pass_id',
        'registration_expiration', 'insurance_expiration', 'emissions_due', 'mileage',
        'unit_value', 'comments', 'gaf_presenter', 'camera_installed', 'vanity_ordered'
    ]

    for field in updatable_fields:
        if field in data:
            update_expr += f', {field} = :{field}'
            value = data[field]
            if field in ['mileage']:
                value = int(value)
            elif field in ['unit_value']:
                value = Decimal(str(value))
            expr_values[f':{field}'] = value

    vehicles_table.update_item(
        Key={'vehicle_id': vehicle_id},
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expr_values
    )

    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({'message': 'Vehicle updated successfully'})
    }

def delete_vehicle(event, headers):
    """Delete a vehicle (soft delete by marking as sold/retired)"""
    query_params = event.get('queryStringParameters', {}) or {}
    vehicle_id = query_params.get('vehicle_id')

    if not vehicle_id:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': 'vehicle_id is required'})
        }

    vehicles_table.update_item(
        Key={'vehicle_id': vehicle_id},
        UpdateExpression='SET #status = :status, updated_at = :updated_at',
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={
            ':status': 'sold',
            ':updated_at': datetime.now().isoformat()
        }
    )

    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({'message': 'Vehicle marked as sold'})
    }

# ============= ACCIDENT OPERATIONS =============

def get_accidents(event, headers):
    """Get all accidents or filter by vehicle, status, date range"""
    query_params = event.get('queryStringParameters', {}) or {}

    response = accidents_table.scan()
    accidents = response.get('Items', [])

    if 'vehicle_id' in query_params:
        accidents = [a for a in accidents if a.get('vehicle_id') == query_params['vehicle_id']]

    if 'status' in query_params:
        accidents = [a for a in accidents if a.get('status') == query_params['status']]

    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(accidents, default=decimal_default)
    }

def create_accident(event, headers):
    """Create a new accident report"""
    data = json.loads(event['body'])

    accident_id = f"ACC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

    accident = {
        'accident_id': accident_id,
        'accident_date': data.get('accident_date', datetime.now().isoformat()),
        'vehicle_id': data.get('vehicle_id', ''),
        'asset_name': data.get('asset_name', ''),
        'driver': data.get('driver', ''),
        'driver_manager': data.get('driver_manager', ''),
        'docs_received': data.get('docs_received', False),
        'video': data.get('video', False),
        'driver_statement': data.get('driver_statement', False),
        'police_report': data.get('police_report', False),
        'video_description': data.get('video_description', ''),
        'claim_number': data.get('claim_number', ''),
        'insurance_provider': data.get('insurance_provider', ''),
        'panda_at_fault': data.get('panda_at_fault', False),
        'driver_estimate': Decimal(str(data.get('driver_estimate', 0))),
        'panda_repair_estimate': Decimal(str(data.get('panda_repair_estimate', 0))),
        'actual_repair_cost': Decimal(str(data.get('actual_repair_cost', 0))),
        'liability_cost': Decimal(str(data.get('liability_cost', 0))),
        'insurance_payout': Decimal(str(data.get('insurance_payout', 0))),
        'whos_paying': data.get('whos_paying', ''),
        'driver_deduction': data.get('driver_deduction', False),
        'driver_deduction_amount': Decimal(str(data.get('driver_deduction_amount', 0))),
        'repair_shop': data.get('repair_shop', ''),
        'date_completed': data.get('date_completed', ''),
        'status': data.get('status', 'pending'),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }

    accidents_table.put_item(Item=accident)

    # Update vehicle status if needed
    if data.get('vehicle_id'):
        vehicles_table.update_item(
            Key={'vehicle_id': data['vehicle_id']},
            UpdateExpression='SET #status = :status, updated_at = :updated_at',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'downed',
                ':updated_at': datetime.now().isoformat()
            }
        )

    return {
        'statusCode': 201,
        'headers': headers,
        'body': json.dumps({'message': 'Accident created successfully', 'accident_id': accident_id})
    }

def update_accident(event, headers):
    """Update an accident report"""
    data = json.loads(event['body'])
    accident_id = data.get('accident_id')

    if not accident_id:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': 'accident_id is required'})
        }

    update_expr = 'SET updated_at = :updated_at'
    expr_values = {':updated_at': datetime.now().isoformat()}

    updatable_fields = [
        'accident_date', 'driver', 'driver_manager', 'docs_received', 'video',
        'driver_statement', 'police_report', 'video_description', 'claim_number',
        'insurance_provider', 'panda_at_fault', 'driver_estimate', 'panda_repair_estimate',
        'actual_repair_cost', 'liability_cost', 'insurance_payout', 'whos_paying',
        'driver_deduction', 'driver_deduction_amount', 'repair_shop', 'date_completed', 'status'
    ]

    for field in updatable_fields:
        if field in data:
            update_expr += f', {field} = :{field}'
            value = data[field]
            if field in ['driver_estimate', 'panda_repair_estimate', 'actual_repair_cost',
                        'liability_cost', 'insurance_payout', 'driver_deduction_amount']:
                value = Decimal(str(value))
            expr_values[f':{field}'] = value

    accidents_table.update_item(
        Key={'accident_id': accident_id},
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expr_values
    )

    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({'message': 'Accident updated successfully'})
    }

# ============= EZ PASS OPERATIONS =============

def get_ezpass(event, headers):
    """Get all EZ Pass records"""
    query_params = event.get('queryStringParameters', {}) or {}

    response = ezpass_table.scan()
    ezpass_records = response.get('Items', [])

    if 'vehicle_id' in query_params:
        ezpass_records = [e for e in ezpass_records if e.get('vehicle_id') == query_params['vehicle_id']]

    if 'status' in query_params:
        ezpass_records = [e for e in ezpass_records if e.get('status') == query_params['status']]

    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(ezpass_records, default=decimal_default)
    }

def create_ezpass(event, headers):
    """Create a new EZ Pass record"""
    data = json.loads(event['body'])

    ezpass_id = data.get('ezpass_id', str(uuid.uuid4()))

    ezpass = {
        'ezpass_id': ezpass_id,
        'vehicle_id': data.get('vehicle_id', ''),
        'asset_name': data.get('asset_name', ''),
        'driver': data.get('driver', ''),
        'driver_email': data.get('driver_email', ''),
        'plate_number': data.get('plate_number', ''),
        'status': data.get('status', 'active'),
        'in_bag_id': data.get('in_bag_id', ''),
        'canceled_id': data.get('canceled_id', ''),
        'territory': data.get('territory', ''),
        'assigned_driver': data.get('assigned_driver', ''),
        'notes': data.get('notes', ''),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }

    ezpass_table.put_item(Item=ezpass)

    return {
        'statusCode': 201,
        'headers': headers,
        'body': json.dumps({'message': 'EZ Pass created successfully', 'ezpass_id': ezpass_id})
    }

def update_ezpass(event, headers):
    """Update an EZ Pass record"""
    data = json.loads(event['body'])
    ezpass_id = data.get('ezpass_id')

    if not ezpass_id:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': 'ezpass_id is required'})
        }

    update_expr = 'SET updated_at = :updated_at'
    expr_values = {':updated_at': datetime.now().isoformat()}

    updatable_fields = [
        'vehicle_id', 'asset_name', 'driver', 'driver_email', 'plate_number',
        'status', 'in_bag_id', 'canceled_id', 'territory', 'assigned_driver', 'notes'
    ]

    for field in updatable_fields:
        if field in data:
            update_expr += f', {field} = :{field}'
            expr_values[f':{field}'] = data[field]

    ezpass_table.update_item(
        Key={'ezpass_id': ezpass_id},
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expr_values
    )

    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({'message': 'EZ Pass updated successfully'})
    }

# ============= SALES OPERATIONS =============

def get_sales(event, headers):
    """Get all vehicle sales"""
    response = sales_table.scan()
    sales = response.get('Items', [])

    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(sales, default=decimal_default)
    }

def create_sale(event, headers):
    """Record a vehicle sale"""
    data = json.loads(event['body'])

    sale_id = f"SALE-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

    sale = {
        'sale_id': sale_id,
        'vehicle_id': data.get('vehicle_id', ''),
        'asset_name': data.get('asset_name', ''),
        'year': data.get('year', ''),
        'make': data.get('make', ''),
        'model': data.get('model', ''),
        'vin': data.get('vin', ''),
        'license_plate': data.get('license_plate', ''),
        'buyer': data.get('buyer', ''),
        'sale_type': data.get('sale_type', 'sold'),
        'sale_date': data.get('sale_date', datetime.now().isoformat()),
        'sale_price': Decimal(str(data.get('sale_price', 0))),
        'insurance_canceled': data.get('insurance_canceled', False),
        'plate_swapped': data.get('plate_swapped', False),
        'sold_to': data.get('sold_to', ''),
        'comments': data.get('comments', ''),
        'created_at': datetime.now().isoformat()
    }

    sales_table.put_item(Item=sale)

    # Update vehicle status to sold
    if data.get('vehicle_id'):
        vehicles_table.update_item(
            Key={'vehicle_id': data['vehicle_id']},
            UpdateExpression='SET #status = :status, updated_at = :updated_at',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'sold',
                ':updated_at': datetime.now().isoformat()
            }
        )

    return {
        'statusCode': 201,
        'headers': headers,
        'body': json.dumps({'message': 'Sale recorded successfully', 'sale_id': sale_id})
    }

# ============= MAINTENANCE OPERATIONS =============

def get_maintenance(event, headers):
    """Get maintenance records"""
    query_params = event.get('queryStringParameters', {}) or {}

    response = maintenance_table.scan()
    maintenance = response.get('Items', [])

    if 'vehicle_id' in query_params:
        maintenance = [m for m in maintenance if m.get('vehicle_id') == query_params['vehicle_id']]

    if 'status' in query_params:
        maintenance = [m for m in maintenance if m.get('status') == query_params['status']]

    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(maintenance, default=decimal_default)
    }

def create_maintenance(event, headers):
    """Create a maintenance record"""
    data = json.loads(event['body'])

    maintenance_id = f"MAINT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

    maintenance = {
        'maintenance_id': maintenance_id,
        'vehicle_id': data.get('vehicle_id', ''),
        'asset_name': data.get('asset_name', ''),
        'type': data.get('type', ''),
        'due_date': data.get('due_date', ''),
        'completed_date': data.get('completed_date', ''),
        'status': data.get('status', 'pending'),
        'provider': data.get('provider', ''),
        'cost': Decimal(str(data.get('cost', 0))),
        'notes': data.get('notes', ''),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }

    maintenance_table.put_item(Item=maintenance)

    return {
        'statusCode': 201,
        'headers': headers,
        'body': json.dumps({'message': 'Maintenance record created', 'maintenance_id': maintenance_id})
    }

def update_maintenance(event, headers):
    """Update a maintenance record"""
    data = json.loads(event['body'])
    maintenance_id = data.get('maintenance_id')

    if not maintenance_id:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': 'maintenance_id is required'})
        }

    update_expr = 'SET updated_at = :updated_at'
    expr_values = {':updated_at': datetime.now().isoformat()}

    updatable_fields = ['completed_date', 'status', 'provider', 'cost', 'notes']

    for field in updatable_fields:
        if field in data:
            update_expr += f', {field} = :{field}'
            value = data[field]
            if field == 'cost':
                value = Decimal(str(value))
            expr_values[f':{field}'] = value

    maintenance_table.update_item(
        Key={'maintenance_id': maintenance_id},
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expr_values
    )

    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({'message': 'Maintenance record updated'})
    }

# ============= REQUEST OPERATIONS =============

def get_requests(event, headers):
    """Get vehicle requests"""
    query_params = event.get('queryStringParameters', {}) or {}

    response = requests_table.scan()
    requests = response.get('Items', [])

    if 'status' in query_params:
        requests = [r for r in requests if r.get('status') == query_params['status']]

    if 'requester_email' in query_params:
        requests = [r for r in requests if r.get('requester_email') == query_params['requester_email']]

    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(requests, default=decimal_default)
    }

def create_request(event, headers):
    """Create a vehicle request"""
    data = json.loads(event['body'])

    request_id = f"REQ-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

    request = {
        'request_id': request_id,
        'requester_email': data.get('requester_email', ''),
        'requester_name': data.get('requester_name', ''),
        'request_type': data.get('request_type', 'vehicle'),
        'vehicle_type': data.get('vehicle_type', ''),
        'duration': data.get('duration', 'temporary'),
        'start_date': data.get('start_date', ''),
        'end_date': data.get('end_date', ''),
        'purpose': data.get('purpose', ''),
        'territory': data.get('territory', ''),
        'manager_approval': 'pending',
        'manager_email': data.get('manager_email', ''),
        'manager_notes': '',
        'assigned_vehicle_id': '',
        'status': 'pending',
        'request_date': datetime.now().isoformat(),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }

    requests_table.put_item(Item=request)

    return {
        'statusCode': 201,
        'headers': headers,
        'body': json.dumps({'message': 'Request created successfully', 'request_id': request_id})
    }

def update_request(event, headers):
    """Update a vehicle request (approve, reject, fulfill)"""
    data = json.loads(event['body'])
    request_id = data.get('request_id')

    if not request_id:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': 'request_id is required'})
        }

    update_expr = 'SET updated_at = :updated_at'
    expr_values = {':updated_at': datetime.now().isoformat()}

    updatable_fields = [
        'manager_approval', 'manager_notes', 'assigned_vehicle_id', 'status'
    ]

    for field in updatable_fields:
        if field in data:
            update_expr += f', {field} = :{field}'
            expr_values[f':{field}'] = data[field]

    requests_table.update_item(
        Key={'request_id': request_id},
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expr_values
    )

    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({'message': 'Request updated successfully'})
    }

# ============= CHECK-IN/CHECK-OUT =============

def checkout_vehicle(event, headers):
    """Assign a vehicle to a driver"""
    data = json.loads(event['body'])

    vehicle_id = data.get('vehicle_id')
    driver_email = data.get('driver_email')

    if not vehicle_id or not driver_email:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': 'vehicle_id and driver_email are required'})
        }

    vehicles_table.update_item(
        Key={'vehicle_id': vehicle_id},
        UpdateExpression='''SET #status = :status,
                            current_driver = :driver,
                            driver_email = :email,
                            driver_phone = :phone,
                            checkout_date = :checkout_date,
                            updated_at = :updated_at''',
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={
            ':status': 'assigned',
            ':driver': data.get('current_driver', ''),
            ':email': driver_email,
            ':phone': data.get('driver_phone', ''),
            ':checkout_date': datetime.now().isoformat(),
            ':updated_at': datetime.now().isoformat()
        }
    )

    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({'message': 'Vehicle checked out successfully'})
    }

def checkin_vehicle(event, headers):
    """Return a vehicle to the fleet"""
    data = json.loads(event['body'])

    vehicle_id = data.get('vehicle_id')

    if not vehicle_id:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': 'vehicle_id is required'})
        }

    vehicles_table.update_item(
        Key={'vehicle_id': vehicle_id},
        UpdateExpression='''SET #status = :status,
                            current_driver = :empty,
                            driver_email = :empty,
                            driver_phone = :empty,
                            mileage = :mileage,
                            updated_at = :updated_at''',
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={
            ':status': 'floater',
            ':empty': '',
            ':mileage': int(data.get('mileage', 0)),
            ':updated_at': datetime.now().isoformat()
        }
    )

    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({'message': 'Vehicle checked in successfully'})
    }

# ============= DASHBOARD/STATS =============

def get_fleet_stats(headers):
    """Get fleet statistics"""
    vehicles = vehicles_table.scan().get('Items', [])
    accidents = accidents_table.scan().get('Items', [])
    maintenance = maintenance_table.scan().get('Items', [])

    stats = {
        'total_vehicles': len(vehicles),
        'assigned': len([v for v in vehicles if v.get('status') == 'assigned']),
        'floaters': len([v for v in vehicles if v.get('status') == 'floater']),
        'downed': len([v for v in vehicles if v.get('status') == 'downed']),
        'maintenance': len([v for v in vehicles if v.get('status') == 'maintenance']),
        'sold': len([v for v in vehicles if v.get('status') == 'sold']),
        'total_accidents': len(accidents),
        'pending_accidents': len([a for a in accidents if a.get('status') == 'pending']),
        'overdue_maintenance': len([m for m in maintenance if m.get('status') == 'overdue']),
        'total_fleet_value': sum([float(v.get('unit_value', 0)) for v in vehicles if v.get('status') != 'sold'])
    }

    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(stats, default=decimal_default)
    }

def get_overdue_maintenance(headers):
    """Get vehicles with overdue maintenance"""
    vehicles = vehicles_table.scan().get('Items', [])
    today = datetime.now().date()

    overdue = []
    for vehicle in vehicles:
        if vehicle.get('status') == 'sold':
            continue

        checks = [
            ('registration_expiration', 'Registration'),
            ('insurance_expiration', 'Insurance'),
            ('emissions_due', 'Emissions')
        ]

        for date_field, type_name in checks:
            if vehicle.get(date_field):
                try:
                    due_date = datetime.fromisoformat(vehicle[date_field]).date()
                    if due_date < today:
                        overdue.append({
                            'vehicle_id': vehicle['vehicle_id'],
                            'asset_name': vehicle.get('asset_name', ''),
                            'type': type_name,
                            'due_date': vehicle[date_field],
                            'days_overdue': (today - due_date).days
                        })
                except:
                    pass

    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(overdue, default=decimal_default)
    }
