"""
Panda Assets API - Microservice for asset management
Handles equipment requests, approvals, PDF generation, and checkout tracking
"""

import json
import boto3
import uuid
from datetime import datetime
from decimal import Decimal
from io import BytesIO
import base64

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
s3 = boto3.client('s3', region_name='us-east-2')
assets_table = dynamodb.Table('panda-assets')
employees_table = dynamodb.Table('panda-employees')

# Equipment options from JotForm
EQUIPMENT_OPTIONS = {
    'desktop_setup': {'name': 'Complete Desktop Setup', 'value': 100.00},
    'new_hire_kit': {'name': 'Complete New Hire Kit for Sales Rep', 'value': 100.00},
    'desktop_computer': {'name': 'Desktop Computer', 'value': 100.00},
    'desktop_screens': {'name': 'Desktop Screens', 'value': 100.00},
    'laptop': {'name': 'Laptop', 'value': 100.00},
    'ipad': {'name': 'iPad w/case and charger', 'value': 100.00},
    'ladder_32ft': {'name': '32 ft Ladder', 'value': 100.00},
    'ladder_18ft': {'name': '18 ft Little Giant ladder', 'value': 100.00},
    'gaf_sales_kit': {'name': 'GAF Sales Kit', 'value': 100.00},
    'goat_steep_roof': {'name': 'GOAT Steep Roof Assist', 'value': 100.00},
}

OFFICE_LOCATIONS = [
    'Delaware',
    'King of Prussia',
    'Maryland',
    'New Jersey',
    'North Carolina',
    'Tampa',
    'Virginia'
]


def get_cors_headers():
    """Return CORS headers for all responses"""
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
        'Content-Type': 'application/json'
    }


def decimal_default(obj):
    """JSON serializer for Decimal objects"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def lambda_handler(event, context):
    """Main Lambda handler - routes requests to appropriate functions"""
    print(f"Event: {json.dumps(event)}")

    # Lambda Function URLs use v2.0 format
    # Extract path and method from either v1.0 or v2.0 event format
    if 'requestContext' in event and 'http' in event['requestContext']:
        # v2.0 format (Lambda Function URLs)
        path = event.get('rawPath', '').rstrip('/')
        method = event['requestContext']['http']['method']
    else:
        # v1.0 format (API Gateway)
        path = event.get('path', '').rstrip('/')
        method = event.get('httpMethod', '')

    # Handle OPTIONS preflight requests
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': ''
        }

    try:
        # Route to appropriate handler
        if path == '/requests' and method == 'POST':
            return create_request(event)
        elif path == '/requests' and method == 'GET':
            return list_requests(event)
        elif path.startswith('/requests/') and method == 'GET':
            request_id = path.split('/')[-1]
            return get_request(request_id)
        elif path.endswith('/approve') and method == 'PUT':
            request_id = path.split('/')[-2]
            return approve_request(request_id, event)
        elif path.endswith('/reject') and method == 'PUT':
            request_id = path.split('/')[-2]
            return reject_request(request_id, event)
        elif path.endswith('/pdf') and method == 'POST':
            request_id = path.split('/')[-2]
            return generate_pdf(request_id)
        elif path.endswith('/sign') and method == 'POST':
            request_id = path.split('/')[-2]
            return sign_document(request_id, event)
        elif path == '/inventory' and method == 'GET':
            return get_inventory(event)
        else:
            return {
                'statusCode': 404,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Not found', 'path': path, 'method': method})
            }

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': str(e)})
        }


def create_request(event):
    """
    Create a new asset request
    POST /requests
    Body: {
        "employee_email": "user@example.com",
        "employee_name": "John Doe",
        "office_location": "Delaware",
        "equipment": ["laptop", "ipad"],
        "notes": "Additional notes"
    }
    """
    try:
        body = json.loads(event.get('body', '{}'))

        # Validate required fields
        required_fields = ['employee_email', 'employee_name', 'office_location', 'equipment']
        for field in required_fields:
            if field not in body:
                return {
                    'statusCode': 400,
                    'headers': get_cors_headers(),
                    'body': json.dumps({'error': f'Missing required field: {field}'})
                }

        # Validate equipment items
        equipment = body['equipment']
        if not isinstance(equipment, list) or len(equipment) == 0:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Equipment must be a non-empty array'})
            }

        for item in equipment:
            if item not in EQUIPMENT_OPTIONS:
                return {
                    'statusCode': 400,
                    'headers': get_cors_headers(),
                    'body': json.dumps({'error': f'Invalid equipment item: {item}'})
                }

        # Calculate total value
        total_value = sum(EQUIPMENT_OPTIONS[item]['value'] for item in equipment)

        # Get employee_id from employees table if exists
        employee_id = 'unknown'  # Default value (GSI doesn't allow null)
        try:
            employee_response = employees_table.scan(
                FilterExpression='email = :email',
                ExpressionAttributeValues={':email': body['employee_email'].lower().strip()}
            )
            if employee_response['Items']:
                employee_id = employee_response['Items'][0].get('id', 'unknown')
        except:
            pass

        # Create request record
        request_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        request_item = {
            'id': request_id,
            'employee_id': employee_id,
            'employee_email': body['employee_email'],
            'employee_name': body['employee_name'],
            'office_location': body['office_location'],
            'equipment': equipment,
            'equipment_details': [
                {
                    'code': item,
                    'name': EQUIPMENT_OPTIONS[item]['name'],
                    'value': Decimal(str(EQUIPMENT_OPTIONS[item]['value']))
                }
                for item in equipment
            ],
            'total_value': Decimal(str(total_value)),
            'notes': body.get('notes', ''),
            'status': 'pending',
            'created_at': now,
            'updated_at': now,
            'approved_by': None,
            'approved_at': None,
            'rejected_by': None,
            'rejected_at': None,
            'rejection_reason': None,
            'pdf_url': None,
            'signature_data': None,
            'signed_at': None,
            'checked_out_at': None
        }

        assets_table.put_item(Item=request_item)

        return {
            'statusCode': 201,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'success': True,
                'request_id': request_id,
                'total_value': total_value,
                'message': 'Asset request created successfully'
            }, default=decimal_default)
        }

    except Exception as e:
        print(f"Error creating request: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': str(e)})
        }


def list_requests(event):
    """
    List asset requests with optional filtering
    GET /requests?status=pending&employee_id=xxx
    """
    try:
        params = event.get('queryStringParameters', {}) or {}
        status_filter = params.get('status')
        employee_id_filter = params.get('employee_id')

        # Query by status if provided
        if status_filter:
            response = assets_table.query(
                IndexName='status-index',
                KeyConditionExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':status': status_filter},
                ScanIndexForward=False  # Most recent first
            )
            items = response['Items']

        # Query by employee_id if provided
        elif employee_id_filter:
            response = assets_table.query(
                IndexName='employee-index',
                KeyConditionExpression='employee_id = :employee_id',
                ExpressionAttributeValues={':employee_id': employee_id_filter},
                ScanIndexForward=False  # Most recent first
            )
            items = response['Items']

        # Otherwise, scan all
        else:
            response = assets_table.scan()
            items = response['Items']
            # Sort by created_at descending
            items.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'success': True,
                'count': len(items),
                'requests': items
            }, default=decimal_default)
        }

    except Exception as e:
        print(f"Error listing requests: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': str(e)})
        }


def get_request(request_id):
    """
    Get a single asset request
    GET /requests/{id}
    """
    try:
        response = assets_table.get_item(Key={'id': request_id})

        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Request not found'})
            }

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'success': True,
                'request': response['Item']
            }, default=decimal_default)
        }

    except Exception as e:
        print(f"Error getting request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': str(e)})
        }


def approve_request(request_id, event):
    """
    Approve an asset request
    PUT /requests/{id}/approve
    Body: {
        "approved_by": "admin@example.com"
    }
    """
    try:
        body = json.loads(event.get('body', '{}'))
        approved_by = body.get('approved_by')

        if not approved_by:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'approved_by is required'})
            }

        # Check if request exists
        response = assets_table.get_item(Key={'id': request_id})
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Request not found'})
            }

        # Update request status
        now = datetime.utcnow().isoformat()
        assets_table.update_item(
            Key={'id': request_id},
            UpdateExpression='SET #status = :status, approved_by = :approved_by, approved_at = :approved_at, updated_at = :updated_at',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'approved',
                ':approved_by': approved_by,
                ':approved_at': now,
                ':updated_at': now
            }
        )

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'success': True,
                'message': 'Request approved successfully',
                'request_id': request_id
            })
        }

    except Exception as e:
        print(f"Error approving request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': str(e)})
        }


def reject_request(request_id, event):
    """
    Reject an asset request
    PUT /requests/{id}/reject
    Body: {
        "rejected_by": "admin@example.com",
        "reason": "Budget constraints"
    }
    """
    try:
        body = json.loads(event.get('body', '{}'))
        rejected_by = body.get('rejected_by')
        reason = body.get('reason', 'No reason provided')

        if not rejected_by:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'rejected_by is required'})
            }

        # Check if request exists
        response = assets_table.get_item(Key={'id': request_id})
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Request not found'})
            }

        # Update request status
        now = datetime.utcnow().isoformat()
        assets_table.update_item(
            Key={'id': request_id},
            UpdateExpression='SET #status = :status, rejected_by = :rejected_by, rejected_at = :rejected_at, rejection_reason = :reason, updated_at = :updated_at',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'rejected',
                ':rejected_by': rejected_by,
                ':rejected_at': now,
                ':reason': reason,
                ':updated_at': now
            }
        )

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'success': True,
                'message': 'Request rejected',
                'request_id': request_id
            })
        }

    except Exception as e:
        print(f"Error rejecting request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': str(e)})
        }


def generate_pdf(request_id):
    """
    Generate PDF for signature
    POST /requests/{id}/pdf

    Note: Requires reportlab library in Lambda layer
    For now, returns a placeholder response
    """
    try:
        # Get request
        response = assets_table.get_item(Key={'id': request_id})
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Request not found'})
            }

        request = response['Item']

        # Check if approved
        if request.get('status') != 'approved':
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Request must be approved before generating PDF'})
            }

        # TODO: Generate actual PDF with reportlab
        # For now, create a simple text-based PDF placeholder
        pdf_content = f"""
PANDA ASSET CHECKOUT FORM
========================

Request ID: {request_id}
Date: {datetime.utcnow().strftime('%Y-%m-%d')}

EMPLOYEE INFORMATION:
- Name: {request.get('employee_name')}
- Email: {request.get('employee_email')}
- Office: {request.get('office_location')}

EQUIPMENT REQUESTED:
"""
        for item in request.get('equipment_details', []):
            pdf_content += f"- {item['name']}: ${item['value']:.2f}\n"

        pdf_content += f"""
TOTAL VALUE: ${float(request.get('total_value', 0)):.2f}

NOTES:
{request.get('notes', 'None')}

APPROVAL:
Approved by: {request.get('approved_by')}
Approved on: {request.get('approved_at')}

EMPLOYEE SIGNATURE:
_______________________________
Date: _________________________

By signing, I acknowledge receipt of the above equipment and agree to return it in good condition.
"""

        # Upload to S3
        pdf_key = f"asset-requests/{request_id}.txt"
        s3.put_object(
            Bucket='panda-assets-docs',
            Key=pdf_key,
            Body=pdf_content.encode('utf-8'),
            ContentType='text/plain'
        )

        # Generate presigned URL (valid for 7 days)
        pdf_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': 'panda-assets-docs', 'Key': pdf_key},
            ExpiresIn=604800  # 7 days
        )

        # Update request with PDF URL
        now = datetime.utcnow().isoformat()
        assets_table.update_item(
            Key={'id': request_id},
            UpdateExpression='SET pdf_url = :url, updated_at = :updated_at',
            ExpressionAttributeValues={
                ':url': pdf_url,
                ':updated_at': now
            }
        )

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'success': True,
                'pdf_url': pdf_url,
                'message': 'PDF generated successfully'
            })
        }

    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': str(e)})
        }


def sign_document(request_id, event):
    """
    Complete checkout with signature
    POST /requests/{id}/sign
    Body: {
        "signature_data": "base64-encoded-signature-image"
    }
    """
    try:
        body = json.loads(event.get('body', '{}'))
        signature_data = body.get('signature_data')

        if not signature_data:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'signature_data is required'})
            }

        # Get request
        response = assets_table.get_item(Key={'id': request_id})
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Request not found'})
            }

        request = response['Item']

        # Check if approved
        if request.get('status') != 'approved':
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Request must be approved before signing'})
            }

        # Update request with signature and mark as checked out
        now = datetime.utcnow().isoformat()
        assets_table.update_item(
            Key={'id': request_id},
            UpdateExpression='SET #status = :status, signature_data = :signature, signed_at = :signed_at, checked_out_at = :checked_out_at, updated_at = :updated_at',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'checked_out',
                ':signature': signature_data,
                ':signed_at': now,
                ':checked_out_at': now,
                ':updated_at': now
            }
        )

        # TODO: Update employee record with asset information
        if request.get('employee_id'):
            try:
                # Add asset info to employee record
                employee = employees_table.get_item(Key={'id': request['employee_id']})
                if 'Item' in employee:
                    current_assets = employee['Item'].get('assets', [])
                    if not isinstance(current_assets, list):
                        current_assets = []

                    # Add new assets
                    for item in request.get('equipment_details', []):
                        current_assets.append({
                            'request_id': request_id,
                            'equipment': item['name'],
                            'value': float(item['value']),
                            'checked_out_at': now
                        })

                    employees_table.update_item(
                        Key={'id': request['employee_id']},
                        UpdateExpression='SET assets = :assets, updated_at = :updated_at',
                        ExpressionAttributeValues={
                            ':assets': current_assets,
                            ':updated_at': now
                        }
                    )
            except Exception as e:
                print(f"Warning: Could not update employee record: {str(e)}")

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'success': True,
                'message': 'Document signed and equipment checked out',
                'request_id': request_id
            })
        }

    except Exception as e:
        print(f"Error signing document: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': str(e)})
        }


def get_inventory(event):
    """
    Get inventory summary
    GET /inventory
    Returns counts by status and equipment type
    """
    try:
        # Scan all requests
        response = assets_table.scan()
        items = response['Items']

        # Count by status
        status_counts = {'pending': 0, 'approved': 0, 'rejected': 0, 'checked_out': 0}
        for item in items:
            status = item.get('status', 'pending')
            status_counts[status] = status_counts.get(status, 0) + 1

        # Count equipment currently checked out
        equipment_counts = {}
        total_value_out = 0

        for item in items:
            if item.get('status') == 'checked_out':
                for equip_detail in item.get('equipment_details', []):
                    equip_name = equip_detail['name']
                    equipment_counts[equip_name] = equipment_counts.get(equip_name, 0) + 1
                    total_value_out += float(equip_detail.get('value', 0))

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'success': True,
                'summary': {
                    'status_counts': status_counts,
                    'equipment_checked_out': equipment_counts,
                    'total_value_checked_out': total_value_out,
                    'total_requests': len(items)
                }
            })
        }

    except Exception as e:
        print(f"Error getting inventory: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': str(e)})
        }
