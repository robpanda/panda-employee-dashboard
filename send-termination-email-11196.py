#!/usr/bin/env python3
"""
Manually send termination email for Renee Scott (Employee ID 11196)
"""

import boto3
from datetime import datetime

# Initialize clients
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
ses = boto3.client('ses', region_name='us-east-2')
employees_table = dynamodb.Table('panda-employees')

def send_termination_refund_email_if_needed(employee, termination_date):
    try:
        print('EMAIL: Starting termination email check')

        # Calculate days employed
        hire_date_str = employee.get('Employment Date') or employee.get('hire_date') or employee.get('employment_date')
        print(f'EMAIL: Hire date string: {hire_date_str}')

        if not hire_date_str:
            print('EMAIL: No hire date found, cannot calculate employment duration - SKIPPING EMAIL')
            return

        hire_date = datetime.strptime(hire_date_str, '%Y-%m-%d')
        term_date = datetime.strptime(termination_date, '%Y-%m-%d')
        days_employed = (term_date - hire_date).days

        print(f'EMAIL: Employee employed for {days_employed} days (hire: {hire_date_str}, term: {termination_date})')

        # Only send email if employed for 90 days or less
        if days_employed > 90:
            print(f'EMAIL: Employee employed for {days_employed} days (> 90), no refund email needed - SKIPPING EMAIL')
            return

        print(f'EMAIL: Employee employed <= 90 days ({days_employed}), checking merchandise...')

        # Get employee name and email
        first_name = employee.get('First Name', employee.get('first_name', ''))
        last_name = employee.get('Last Name', employee.get('last_name', ''))
        employee_name = f"{first_name} {last_name}".strip() or 'Unknown Employee'
        employee_email = employee.get('Email', employee.get('email', ''))

        # Get merchandise info from employee record
        merch_requested = employee.get('Merch Requested', employee.get('merch_requested', ''))
        merch_value = float(employee.get('merchandise_value', employee.get('Merchandise Value', 0)) or 0)

        print(f'EMAIL: Merch requested: {merch_requested}, Merch value: {merch_value}')

        if not merch_requested and merch_value == 0:
            print('EMAIL: No merchandise purchases found, no refund email needed - SKIPPING EMAIL')
            return

        print('EMAIL: Merchandise found, preparing email...')

        # Set default merch value if we have items but no value
        if merch_requested and merch_value == 0:
            merch_value = 50.00  # Default polo shirt value
            print(f'EMAIL: No value found, using default ${merch_value}')

        purchase_details = merch_requested or 'Merchandise items'
        amount_to_collect = merch_value

        # Format employment duration
        if days_employed < 30:
            duration_text = f"{days_employed} days"
        else:
            duration_text = f"{days_employed} days"

        subject = f"Merch Refund Collection Required for Terminated Employee: {employee_name}"

        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #d32f2f;">Merchandise Refund Collection Required</h2>

                <p>Dear Team,</p>

                <p>Employee <strong>{employee_name}</strong> has been terminated with <strong>{duration_text}</strong> employed, which is less than 90 days.</p>

                <p>Please initiate the process to collect a refund for their store credit usage, covering the following:</p>

                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #d32f2f;">
                    <p><strong>Amount to Be Collected:</strong> ${amount_to_collect:.2f} USD</p>
                    <p><strong>Merchandise Items:</strong> {purchase_details}</p>
                </div>

                <h3 style="color: #333; margin-top: 30px;">Employee Details:</h3>
                <ul>
                    <li><strong>Name:</strong> {employee_name}</li>
                    <li><strong>Employee ID:</strong> {employee.get('Employee Id', employee.get('id', 'N/A'))}</li>
                    <li><strong>Email:</strong> {employee_email}</li>
                    <li><strong>Hire Date:</strong> {hire_date_str}</li>
                    <li><strong>Termination Date:</strong> {termination_date}</li>
                    <li><strong>Days Employed:</strong> {days_employed}</li>
                    <li><strong>Department:</strong> {employee.get('Department', 'N/A')}</li>
                    <li><strong>Position:</strong> {employee.get('Position', 'N/A')}</li>
                    <li><strong>Termination Status:</strong> Yes</li>
                </ul>

                <p style="margin-top: 30px;">Thank you,<br>HR Team</p>

                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="font-size: 12px; color: #666;">This is an automated message from the Panda Employee Management system.</p>
            </div>
        </body>
        </html>
        """

        body_text = f"""
        Merchandise Refund Collection Required

        Dear Team,

        Employee {employee_name} has been terminated with {duration_text} employed, which is less than 90 days.

        Please initiate the process to collect a refund for their store credit usage, covering the following:

        Amount to Be Collected: ${amount_to_collect:.2f} USD
        Merchandise Items: {purchase_details}

        Details:
        - Name: {employee_name}
        - Employee ID: {employee.get('Employee Id', employee.get('id', 'N/A'))}
        - Email: {employee_email}
        - Hire Date: {hire_date_str}
        - Termination Date: {termination_date}
        - Days Employed: {days_employed}
        - Department: {employee.get('Department', 'N/A')}
        - Position: {employee.get('Position', 'N/A')}
        - Termination Status: Yes

        Thank you,
        HR Team
        """

        # Send to multiple recipients
        recipients = [
            'robwinters@pandaexteriors.com',
            'valerieliebno@pandaexteriors.com',
            'madeleineferrerosa@pandaexteriors.com',
            'sheenakurian@pandaexteriors.com'
        ]

        print(f'EMAIL: Sending email to: {", ".join(recipients)}')
        print(f'EMAIL: Subject: {subject}')
        print(f'EMAIL: Amount to collect: ${amount_to_collect:.2f}')

        ses.send_email(
            Source='noreply@pandaexteriors.com',
            Destination={'ToAddresses': recipients},
            Message={
                'Subject': {'Data': subject},
                'Body': {
                    'Html': {'Data': body_html},
                    'Text': {'Data': body_text}
                }
            }
        )
        print(f'EMAIL: ✅ SUCCESS - Termination refund email sent for: {employee_name} (${amount_to_collect:.2f})')
        return True
    except Exception as e:
        print(f'EMAIL: ❌ ERROR - Failed to send email: {e}')
        import traceback
        print(f'EMAIL: Traceback: {traceback.format_exc()}')
        return False


if __name__ == '__main__':
    # Get employee data
    print("=" * 60)
    print("SENDING TERMINATION EMAIL FOR RENEE SCOTT (ID: 11196)")
    print("=" * 60)

    response = employees_table.get_item(Key={'id': '11196'})

    if 'Item' not in response:
        print("❌ Employee 11196 not found in database")
        exit(1)

    employee = response['Item']

    print(f"\nEmployee: {employee.get('First Name')} {employee.get('Last Name')}")
    print(f"Hire Date: {employee.get('Employment Date')}")
    print(f"Termination Date: {employee.get('Termination Date')}")
    print(f"Merchandise: {employee.get('Merch Requested')}")
    print()

    # Send the email
    success = send_termination_refund_email_if_needed(employee, employee.get('Termination Date'))

    print()
    print("=" * 60)
    if success:
        print("✅ Termination email sent successfully!")
        print("Recipients:")
        print("  - robwinters@pandaexteriors.com")
        print("  - valerieliebno@pandaexteriors.com")
        print("  - madeleineferrerosa@pandaexteriors.com")
        print("  - sheenakurian@pandaexteriors.com")
    else:
        print("❌ Failed to send termination email")
    print("=" * 60)
