#!/usr/bin/env python3
"""
Send termination email for Renee Scott to robwinters only (for testing)
"""

import boto3
from datetime import datetime

# Initialize clients
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
ses = boto3.client('ses', region_name='us-east-2')
employees_table = dynamodb.Table('panda-employees')

# Get employee data
response = employees_table.get_item(Key={'id': '11196'})
employee = response['Item']

# Calculate details
hire_date_str = employee.get('Employment Date')
term_date_str = employee.get('Termination Date')
hire_date = datetime.strptime(hire_date_str, '%Y-%m-%d')
term_date = datetime.strptime(term_date_str, '%Y-%m-%d')
days_employed = (term_date - hire_date).days

first_name = employee.get('First Name', '')
last_name = employee.get('Last Name', '')
employee_name = f"{first_name} {last_name}"
employee_email = employee.get('Email', '')
employee_id = employee.get('Employee Id', '')
merch_requested = employee.get('Merch Requested', '')
amount_to_collect = 50.00  # Default polo value

subject = f"TEST: Merch Refund Collection Required - {employee_name}"

body_html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #ffc107; color: #000; padding: 10px; text-align: center; font-weight: bold; margin-bottom: 20px;">
            ⚠️ TEST EMAIL - Termination Notification for Renee Scott
        </div>

        <h2 style="color: #d32f2f;">Merchandise Refund Collection Required</h2>

        <p>Dear Team,</p>

        <p>Employee <strong>{employee_name}</strong> has been terminated with <strong>{days_employed} days</strong> employed, which is less than 90 days.</p>

        <p>Please initiate the process to collect a refund for their store credit usage, covering the following:</p>

        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #d32f2f;">
            <p><strong>Amount to Be Collected:</strong> ${amount_to_collect:.2f} USD</p>
            <p><strong>Merchandise Items:</strong> {merch_requested}</p>
        </div>

        <h3 style="color: #333; margin-top: 30px;">Employee Details:</h3>
        <ul>
            <li><strong>Name:</strong> {employee_name}</li>
            <li><strong>Employee ID:</strong> {employee_id}</li>
            <li><strong>Email:</strong> {employee_email}</li>
            <li><strong>Hire Date:</strong> {hire_date_str}</li>
            <li><strong>Termination Date:</strong> {term_date_str}</li>
            <li><strong>Days Employed:</strong> {days_employed}</li>
            <li><strong>Department:</strong> {employee.get('Department', 'N/A')}</li>
            <li><strong>Position:</strong> {employee.get('Position', 'N/A')}</li>
            <li><strong>Office:</strong> {employee.get('office', 'N/A')}</li>
            <li><strong>Supervisor:</strong> {employee.get('supervisor', 'N/A')}</li>
            <li><strong>Merchandise Sent:</strong> {employee.get('Merch Sent', 'N/A')}</li>
        </ul>

        <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107;">
            <p><strong>⚠️ Note:</strong> This refund is required per company policy for employees terminated within 90 days of hire.</p>
        </div>

        <p style="margin-top: 30px;">Thank you,<br>HR Team</p>

        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        <p style="font-size: 12px; color: #666;">
            This is a TEST message from the Panda Employee Management system.<br>
            In production, this would be sent to all 4 HR recipients.
        </p>
    </div>
</body>
</html>
"""

print("Sending test termination email for Renee Scott...")
print(f"Employee: {employee_name}")
print(f"Days Employed: {days_employed}")
print(f"Merchandise: {merch_requested}")
print(f"Amount to Collect: ${amount_to_collect:.2f}")
print()

try:
    ses.send_email(
        Source='noreply@pandaexteriors.com',
        Destination={'ToAddresses': ['robwinters@pandaexteriors.com']},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Html': {'Data': body_html}}
        }
    )
    print("✅ TEST email sent successfully to robwinters@pandaexteriors.com")
    print()
    print("NOTE: Once all email addresses are verified in SES, this will be sent to:")
    print("  - robwinters@pandaexteriors.com")
    print("  - valerieliebno@pandaexteriors.com")
    print("  - madeleineferrerosa@pandaexteriors.com")
    print("  - sheenakurian@pandaexteriors.com")
except Exception as e:
    print(f"❌ Error: {e}")
