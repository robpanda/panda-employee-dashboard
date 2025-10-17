"""
Panda Assets API - Enhanced Microservice for asset management
Features:
- Professional PDF generation with ReportLab
- Email notifications via SES
- Asset return workflow
- Reporting and analytics
"""

import json
import boto3
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from io import BytesIO
import base64

# Import ReportLab for PDF generation
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Warning: ReportLab not available, using text-based PDFs")

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
s3 = boto3.client('s3', region_name='us-east-2')
ses = boto3.client('ses', region_name='us-east-2')
assets_table = dynamodb.Table('panda-assets')
employees_table = dynamodb.Table('panda-employees')

# Configuration
SES_SENDER_EMAIL = 'pandanews@pandaexteriors.com'  # Must be verified in SES
COMPANY_NAME = 'Panda Exteriors'
COMPANY_ADDRESS = '123 Main Street, Delaware'
COMPANY_PHONE = '(555) 123-4567'

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


def send_email_notification(to_email, subject, body_html, body_text=None):
    """
    Send email notification via AWS SES
    """
    try:
        if body_text is None:
            body_text = body_html.replace('<br>', '\n').replace('<p>', '').replace('</p>', '\n')

        response = ses.send_email(
            Source=SES_SENDER_EMAIL,
            Destination={'ToAddresses': [to_email]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Html': {'Data': body_html, 'Charset': 'UTF-8'},
                    'Text': {'Data': body_text, 'Charset': 'UTF-8'}
                }
            }
        )
        print(f"Email sent successfully to {to_email}: {response['MessageId']}")
        return True
    except Exception as e:
        print(f"Error sending email to {to_email}: {str(e)}")
        return False


def generate_professional_pdf(request_data):
    """
    Generate professional PDF using ReportLab with company branding
    """
    if not REPORTLAB_AVAILABLE:
        # Fallback to text-based PDF
        return generate_text_pdf(request_data)

    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              leftMargin=0.75*inch, rightMargin=0.75*inch,
                              topMargin=0.75*inch, bottomMargin=0.75*inch)

        # Container for PDF elements
        elements = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=12,
            spaceBefore=12
        )

        # Header
        elements.append(Paragraph(f"{COMPANY_NAME}", title_style))
        elements.append(Paragraph("Asset Checkout Agreement", styles['Heading2']))
        elements.append(Spacer(1, 0.3*inch))

        # Request Information
        elements.append(Paragraph("Request Information", heading_style))

        request_info = [
            ['Request ID:', request_data['id'][:13] + '...'],
            ['Date:', datetime.fromisoformat(request_data['created_at']).strftime('%B %d, %Y')],
            ['Status:', request_data['status'].upper()],
        ]

        request_table = Table(request_info, colWidths=[2*inch, 4*inch])
        request_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(request_table)
        elements.append(Spacer(1, 0.2*inch))

        # Employee Information
        elements.append(Paragraph("Employee Information", heading_style))

        employee_info = [
            ['Name:', request_data['employee_name']],
            ['Email:', request_data['employee_email']],
            ['Office Location:', request_data['office_location']],
        ]

        employee_table = Table(employee_info, colWidths=[2*inch, 4*inch])
        employee_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(employee_table)
        elements.append(Spacer(1, 0.2*inch))

        # Equipment List
        elements.append(Paragraph("Equipment Requested", heading_style))

        equipment_data = [['Item', 'Description', 'Value']]
        for i, equip in enumerate(request_data.get('equipment_details', []), 1):
            equipment_data.append([
                str(i),
                equip['name'],
                f"${float(equip['value']):.2f}"
            ])

        # Add total row
        equipment_data.append(['', 'TOTAL:', f"${float(request_data['total_value']):.2f}"])

        equipment_table = Table(equipment_data, colWidths=[0.5*inch, 4.5*inch, 1.5*inch])
        equipment_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Data rows
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 10),
            ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f0f0f0')]),

            # Total row
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e0e0e0')),
            ('ALIGN', (1, -1), (1, -1), 'RIGHT'),
            ('ALIGN', (2, -1), (2, -1), 'RIGHT'),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
        ]))
        elements.append(equipment_table)
        elements.append(Spacer(1, 0.3*inch))

        # Notes
        if request_data.get('notes'):
            elements.append(Paragraph("Additional Notes", heading_style))
            elements.append(Paragraph(request_data['notes'], styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))

        # Terms and Conditions
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("Terms and Conditions", heading_style))
        terms = """
        By signing below, I acknowledge that I have received the equipment listed above in good working condition.
        I agree to use this equipment responsibly and solely for company business purposes.
        I understand that I am responsible for the care and security of this equipment and must return it
        in the same condition as received, normal wear and tear excepted. I will report any loss, theft,
        or damage immediately to my supervisor.
        """
        elements.append(Paragraph(terms, styles['Normal']))
        elements.append(Spacer(1, 0.4*inch))

        # Signature Section
        sig_data = [
            ['Employee Signature:', '_' * 40, 'Date:', '_' * 20],
        ]
        sig_table = Table(sig_data, colWidths=[1.5*inch, 2.5*inch, 0.7*inch, 1.3*inch])
        sig_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        elements.append(sig_table)

        # Approval Information (if approved)
        if request_data.get('approved_by'):
            elements.append(Spacer(1, 0.3*inch))
            elements.append(Paragraph("Approval Information", heading_style))
            approval_info = [
                ['Approved By:', request_data['approved_by']],
                ['Approval Date:', datetime.fromisoformat(request_data['approved_at']).strftime('%B %d, %Y %I:%M %p')],
            ]
            approval_table = Table(approval_info, colWidths=[2*inch, 4*inch])
            approval_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.grey),
            ]))
            elements.append(approval_table)

        # Footer
        elements.append(Spacer(1, 0.4*inch))
        footer_text = f"{COMPANY_NAME} | {COMPANY_ADDRESS} | {COMPANY_PHONE}"
        elements.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'],
                                                              fontSize=8, textColor=colors.grey,
                                                              alignment=TA_CENTER)))

        # Build PDF
        doc.build(elements)

        return buffer.getvalue()

    except Exception as e:
        print(f"Error generating professional PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        # Fallback to text PDF
        return generate_text_pdf(request_data)


def generate_text_pdf(request_data):
    """
    Fallback: Generate text-based PDF content
    """
    pdf_content = f"""
{COMPANY_NAME}
ASSET CHECKOUT AGREEMENT
{"=" * 80}

REQUEST INFORMATION:
Request ID: {request_data['id']}
Date: {datetime.fromisoformat(request_data['created_at']).strftime('%B %d, %Y')}
Status: {request_data['status'].upper()}

EMPLOYEE INFORMATION:
Name: {request_data['employee_name']}
Email: {request_data['employee_email']}
Office Location: {request_data['office_location']}

EQUIPMENT REQUESTED:
"""
    for i, equip in enumerate(request_data.get('equipment_details', []), 1):
        pdf_content += f"{i}. {equip['name']}: ${float(equip['value']):.2f}\n"

    pdf_content += f"\nTOTAL VALUE: ${float(request_data['total_value']):.2f}\n"

    if request_data.get('notes'):
        pdf_content += f"\nADDITIONAL NOTES:\n{request_data['notes']}\n"

    pdf_content += f"""
{"=" * 80}
TERMS AND CONDITIONS:
By signing below, I acknowledge that I have received the equipment listed above
in good working condition. I agree to use this equipment responsibly and solely
for company business purposes. I understand that I am responsible for the care
and security of this equipment and must return it in the same condition as
received, normal wear and tear excepted.

EMPLOYEE SIGNATURE: _______________________________  DATE: ______________
"""

    if request_data.get('approved_by'):
        pdf_content += f"""
APPROVAL INFORMATION:
Approved by: {request_data['approved_by']}
Approved on: {request_data['approved_at']}
"""

    pdf_content += f"\n{COMPANY_NAME} | {COMPANY_ADDRESS} | {COMPANY_PHONE}\n"

    return pdf_content.encode('utf-8')


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
        elif path.endswith('/return') and method == 'POST':
            request_id = path.split('/')[-2]
            return return_asset(request_id, event)
        elif path == '/inventory' and method == 'GET':
            return get_inventory(event)
        elif path == '/reports/summary' and method == 'GET':
            return get_reports_summary(event)
        elif path == '/reports/by-employee' and method == 'GET':
            return get_reports_by_employee(event)
        elif path == '/reports/by-equipment' and method == 'GET':
            return get_reports_by_equipment(event)
        elif path == '/reports/by-office' and method == 'GET':
            return get_reports_by_office(event)
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
    """
    try:
        body = json.loads(event.get('body', '{}'))

        # Validate required fields
        required_fields = ['employee_name', 'employee_email', 'office_location', 'equipment']
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

        # Get or create employee record
        employee_id = 'unknown'  # Default value (GSI doesn't allow null)
        try:
            employee_response = employees_table.scan(
                FilterExpression='email = :email',
                ExpressionAttributeValues={':email': body['employee_email'].lower().strip()}
            )
            if employee_response['Items']:
                employee_id = employee_response['Items'][0].get('id', 'unknown')
            else:
                # Employee doesn't exist - create new employee record
                employee_id = str(uuid.uuid4())
                new_employee = {
                    'id': employee_id,
                    'email': body['employee_email'].lower().strip(),
                    'name': body['employee_name'],
                    'office_location': body['office_location'],
                    'created_at': datetime.utcnow().isoformat(),
                    'source': 'asset_request',  # Track where this employee was created
                    'status': 'active'
                }
                employees_table.put_item(Item=new_employee)
                print(f"Created new employee record: {employee_id} - {body['employee_name']}")
        except Exception as e:
            print(f"Error handling employee record: {str(e)}")
            # Continue with 'unknown' if there's an error
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
            'checked_out_at': None,
            'returned_at': None,
            'return_condition': None,
            'return_notes': None
        }

        assets_table.put_item(Item=request_item)

        # Send email notification to admin (optional - requires SES setup)
        # send_email_notification(
        #     'admin@pandaexteriors.com',
        #     'New Asset Request Submitted',
        #     f'<p>New asset request from {body["employee_name"]}</p><p>Total Value: ${total_value}</p>'
        # )

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
    Approve an asset request and send email notification
    PUT /requests/{id}/approve
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

        request_data = response['Item']

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

        # Send email notification to employee
        email_body = f"""
        <html>
        <body>
            <h2>Your Asset Request Has Been Approved!</h2>
            <p>Hello {request_data['employee_name']},</p>
            <p>Great news! Your asset request has been approved by {approved_by}.</p>

            <h3>Request Details:</h3>
            <ul>
                <li><strong>Request ID:</strong> {request_id[:13]}...</li>
                <li><strong>Total Value:</strong> ${float(request_data['total_value']):.2f}</li>
                <li><strong>Approved on:</strong> {datetime.utcnow().strftime('%B %d, %Y')}</li>
            </ul>

            <p>Next steps: A PDF checkout document will be generated for your signature.</p>

            <p>Thank you,<br>{COMPANY_NAME}</p>
        </body>
        </html>
        """

        send_email_notification(
            request_data['employee_email'],
            f'{COMPANY_NAME} - Asset Request Approved',
            email_body
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
    Reject an asset request and send email notification
    PUT /requests/{id}/reject
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

        request_data = response['Item']

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

        # Send email notification to employee
        email_body = f"""
        <html>
        <body>
            <h2>Asset Request Update</h2>
            <p>Hello {request_data['employee_name']},</p>
            <p>We regret to inform you that your asset request has been declined.</p>

            <h3>Request Details:</h3>
            <ul>
                <li><strong>Request ID:</strong> {request_id[:13]}...</li>
                <li><strong>Total Value:</strong> ${float(request_data['total_value']):.2f}</li>
                <li><strong>Reason:</strong> {reason}</li>
            </ul>

            <p>If you have questions, please contact {rejected_by}.</p>

            <p>Thank you,<br>{COMPANY_NAME}</p>
        </body>
        </html>
        """

        send_email_notification(
            request_data['employee_email'],
            f'{COMPANY_NAME} - Asset Request Update',
            email_body
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
    Generate professional PDF for signature using ReportLab
    POST /requests/{id}/pdf
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

        # Generate professional PDF
        pdf_content = generate_professional_pdf(request)

        # Upload to S3
        pdf_key = f"asset-requests/{request_id}.pdf"
        s3.put_object(
            Bucket='panda-assets-docs',
            Key=pdf_key,
            Body=pdf_content,
            ContentType='application/pdf'
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

        # Send email with PDF link
        email_body = f"""
        <html>
        <body>
            <h2>Your Checkout Document is Ready</h2>
            <p>Hello {request['employee_name']},</p>
            <p>Your asset checkout document has been generated and is ready for your signature.</p>

            <p><a href="{pdf_url}" style="background-color: #1a5490; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Document</a></p>

            <p>This link will expire in 7 days.</p>

            <p>Thank you,<br>{COMPANY_NAME}</p>
        </body>
        </html>
        """

        send_email_notification(
            request['employee_email'],
            f'{COMPANY_NAME} - Checkout Document Ready',
            email_body
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

        # Update employee record with asset information
        if request.get('employee_id') and request['employee_id'] != 'unknown':
            try:
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

        # Send confirmation email
        equipment_list = '<br>'.join([f"- {item['name']}" for item in request.get('equipment_details', [])])
        email_body = f"""
        <html>
        <body>
            <h2>Asset Checkout Complete</h2>
            <p>Hello {request['employee_name']},</p>
            <p>Your asset checkout has been completed successfully!</p>

            <h3>Equipment Checked Out:</h3>
            <p>{equipment_list}</p>

            <p><strong>Total Value:</strong> ${float(request['total_value']):.2f}</p>
            <p><strong>Date:</strong> {datetime.utcnow().strftime('%B %d, %Y')}</p>

            <p>Please take care of this equipment and report any issues immediately.</p>

            <p>Thank you,<br>{COMPANY_NAME}</p>
        </body>
        </html>
        """

        send_email_notification(
            request['employee_email'],
            f'{COMPANY_NAME} - Checkout Confirmation',
            email_body
        )

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


def return_asset(request_id, event):
    """
    Process asset return
    POST /requests/{id}/return
    Body: {
        "return_condition": "good|fair|damaged",
        "return_notes": "optional notes"
    }
    """
    try:
        body = json.loads(event.get('body', '{}'))
        return_condition = body.get('return_condition', 'good')
        return_notes = body.get('return_notes', '')

        # Get request
        response = assets_table.get_item(Key={'id': request_id})
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Request not found'})
            }

        request = response['Item']

        # Check if checked out
        if request.get('status') != 'checked_out':
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Asset must be checked out before it can be returned'})
            }

        # Update request with return information
        now = datetime.utcnow().isoformat()
        assets_table.update_item(
            Key={'id': request_id},
            UpdateExpression='SET #status = :status, returned_at = :returned_at, return_condition = :condition, return_notes = :notes, updated_at = :updated_at',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'returned',
                ':returned_at': now,
                ':condition': return_condition,
                ':notes': return_notes,
                ':updated_at': now
            }
        )

        # Update employee record
        if request.get('employee_id') and request['employee_id'] != 'unknown':
            try:
                employee = employees_table.get_item(Key={'id': request['employee_id']})
                if 'Item' in employee:
                    current_assets = employee['Item'].get('assets', [])
                    if isinstance(current_assets, list):
                        # Remove returned assets
                        updated_assets = [a for a in current_assets if a.get('request_id') != request_id]

                        employees_table.update_item(
                            Key={'id': request['employee_id']},
                            UpdateExpression='SET assets = :assets, updated_at = :updated_at',
                            ExpressionAttributeValues={
                                ':assets': updated_assets,
                                ':updated_at': now
                            }
                        )
            except Exception as e:
                print(f"Warning: Could not update employee record: {str(e)}")

        # Send confirmation email
        equipment_list = '<br>'.join([f"- {item['name']}" for item in request.get('equipment_details', [])])
        email_body = f"""
        <html>
        <body>
            <h2>Asset Return Confirmed</h2>
            <p>Hello {request['employee_name']},</p>
            <p>Thank you for returning your equipment.</p>

            <h3>Equipment Returned:</h3>
            <p>{equipment_list}</p>

            <p><strong>Condition:</strong> {return_condition.upper()}</p>
            <p><strong>Return Date:</strong> {datetime.utcnow().strftime('%B %d, %Y')}</p>

            {f"<p><strong>Notes:</strong> {return_notes}</p>" if return_notes else ""}

            <p>Thank you,<br>{COMPANY_NAME}</p>
        </body>
        </html>
        """

        send_email_notification(
            request['employee_email'],
            f'{COMPANY_NAME} - Return Confirmation',
            email_body
        )

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'success': True,
                'message': 'Asset returned successfully',
                'request_id': request_id
            })
        }

    except Exception as e:
        print(f"Error processing return: {str(e)}")
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
    """
    try:
        # Scan all requests
        response = assets_table.scan()
        items = response['Items']

        # Count by status
        status_counts = {'pending': 0, 'approved': 0, 'rejected': 0, 'checked_out': 0, 'returned': 0}
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


def get_reports_summary(event):
    """
    Get comprehensive summary report
    GET /reports/summary?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
    """
    try:
        params = event.get('queryStringParameters', {}) or {}
        start_date = params.get('start_date')
        end_date = params.get('end_date')

        # Get all requests
        response = assets_table.scan()
        items = response['Items']

        # Filter by date if provided
        if start_date:
            items = [i for i in items if i.get('created_at', '') >= start_date]
        if end_date:
            items = [i for i in items if i.get('created_at', '') <= end_date]

        # Calculate metrics
        total_requests = len(items)
        total_value = sum(float(i.get('total_value', 0)) for i in items)

        status_breakdown = {}
        for item in items:
            status = item.get('status', 'pending')
            status_breakdown[status] = status_breakdown.get(status, 0) + 1

        # Average processing time (from created to approved)
        processing_times = []
        for item in items:
            if item.get('approved_at'):
                created = datetime.fromisoformat(item['created_at'])
                approved = datetime.fromisoformat(item['approved_at'])
                processing_times.append((approved - created).total_seconds() / 3600)  # hours

        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0

        # Top equipment
        equipment_freq = {}
        for item in items:
            for equip in item.get('equipment_details', []):
                name = equip['name']
                equipment_freq[name] = equipment_freq.get(name, 0) + 1

        top_equipment = sorted(equipment_freq.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'success': True,
                'report': {
                    'period': {
                        'start': start_date or 'all time',
                        'end': end_date or 'present'
                    },
                    'metrics': {
                        'total_requests': total_requests,
                        'total_value': total_value,
                        'average_processing_time_hours': round(avg_processing_time, 2),
                        'status_breakdown': status_breakdown,
                        'top_equipment': [{'name': name, 'count': count} for name, count in top_equipment]
                    }
                }
            })
        }

    except Exception as e:
        print(f"Error generating summary report: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': str(e)})
        }


def get_reports_by_employee(event):
    """
    Get report grouped by employee
    GET /reports/by-employee
    """
    try:
        response = assets_table.scan()
        items = response['Items']

        # Group by employee
        employee_data = {}
        for item in items:
            emp_email = item.get('employee_email')
            emp_name = item.get('employee_name')

            if emp_email not in employee_data:
                employee_data[emp_email] = {
                    'name': emp_name,
                    'email': emp_email,
                    'total_requests': 0,
                    'total_value': 0,
                    'checked_out_count': 0,
                    'returned_count': 0
                }

            employee_data[emp_email]['total_requests'] += 1
            employee_data[emp_email]['total_value'] += float(item.get('total_value', 0))

            if item.get('status') == 'checked_out':
                employee_data[emp_email]['checked_out_count'] += 1
            elif item.get('status') == 'returned':
                employee_data[emp_email]['returned_count'] += 1

        # Convert to list and sort by total value
        employees = sorted(employee_data.values(), key=lambda x: x['total_value'], reverse=True)

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'success': True,
                'employees': employees
            })
        }

    except Exception as e:
        print(f"Error generating employee report: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': str(e)})
        }


def get_reports_by_equipment(event):
    """
    Get report grouped by equipment type
    GET /reports/by-equipment
    """
    try:
        response = assets_table.scan()
        items = response['Items']

        # Count equipment
        equipment_data = {}
        for item in items:
            for equip in item.get('equipment_details', []):
                name = equip['name']
                if name not in equipment_data:
                    equipment_data[name] = {
                        'name': name,
                        'total_requested': 0,
                        'currently_checked_out': 0,
                        'returned': 0,
                        'total_value': 0
                    }

                equipment_data[name]['total_requested'] += 1
                equipment_data[name]['total_value'] += float(equip['value'])

                if item.get('status') == 'checked_out':
                    equipment_data[name]['currently_checked_out'] += 1
                elif item.get('status') == 'returned':
                    equipment_data[name]['returned'] += 1

        # Convert to list and sort by total requested
        equipment = sorted(equipment_data.values(), key=lambda x: x['total_requested'], reverse=True)

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'success': True,
                'equipment': equipment
            })
        }

    except Exception as e:
        print(f"Error generating equipment report: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': str(e)})
        }


def get_reports_by_office(event):
    """
    Get report grouped by office location
    GET /reports/by-office
    """
    try:
        response = assets_table.scan()
        items = response['Items']

        # Group by office
        office_data = {}
        for item in items:
            office = item.get('office_location', 'Unknown')

            if office not in office_data:
                office_data[office] = {
                    'office': office,
                    'total_requests': 0,
                    'total_value': 0,
                    'checked_out_count': 0,
                    'equipment_breakdown': {}
                }

            office_data[office]['total_requests'] += 1
            office_data[office]['total_value'] += float(item.get('total_value', 0))

            if item.get('status') == 'checked_out':
                office_data[office]['checked_out_count'] += 1

            # Track equipment per office
            for equip in item.get('equipment_details', []):
                name = equip['name']
                if name not in office_data[office]['equipment_breakdown']:
                    office_data[office]['equipment_breakdown'][name] = 0
                office_data[office]['equipment_breakdown'][name] += 1

        # Convert to list and sort by total value
        offices = sorted(office_data.values(), key=lambda x: x['total_value'], reverse=True)

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'success': True,
                'offices': offices
            })
        }

    except Exception as e:
        print(f"Error generating office report: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': str(e)})
        }
