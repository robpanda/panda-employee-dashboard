#!/usr/bin/env python3
"""
Import employees from CSV file directly to DynamoDB
This version PRESERVES existing points and other data while updating core fields
"""
import boto3
import csv
from datetime import datetime
from decimal import Decimal

# CSV file path - UPDATE THIS PATH as needed
CSV_FILE = '/Users/robwinters/Downloads/Active_Headcount__location_and_email_ - Report (1).csv'

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def import_employees():
    """Import employees from CSV to DynamoDB"""

    updated_count = 0
    with_emails = 0
    without_emails = 0

    print(f"Reading CSV: {CSV_FILE}\n")

    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Skip empty rows
            if not row.get('Employee Id') or not row.get('Last Name'):
                continue

            employee_id = row.get('Employee Id', '').strip()
            first_name = row.get('First Name', '').strip()
            last_name = row.get('Last Name', '').strip()

            # READ ACTUAL EMAIL COLUMNS FROM CSV
            email = row.get('Email', '').strip()
            work_email = row.get('Work Email', '').strip()

            # Get existing employee data to preserve points, etc.
            existing = None
            try:
                response = table.get_item(Key={'employee_id': employee_id})
                existing = response.get('Item', {})
            except:
                pass

            # Create employee record with ACTUAL emails from CSV
            employee_data = {
                'employee_id': employee_id,
                'id': employee_id,  # Duplicate for compatibility
                'first_name': first_name,
                'last_name': last_name,
                'First Name': first_name,  # Capitalized version
                'Last Name': last_name,     # Capitalized version
                'name': f"{first_name} {last_name}",  # IMPORTANT: Build full name

                # ACTUAL EMAILS FROM CSV
                'Email': email,              # Capitalized version (primary)
                'email': email.lower() if email else '',  # Lowercase version
                'Work Email': work_email,    # Capitalized version
                'work_email': work_email.lower() if work_email else '',  # Lowercase version

                # Other fields from CSV
                'Department': row.get('Department Description', '').strip(),
                'department': row.get('Department Description', '').strip(),
                'Position': row.get('Position Description', '').strip(),
                'office': row.get('Current Work Location Name', '').strip(),
                'Office Location': row.get('Current Work Location Name', '').strip(),
                'supervisor': row.get('Supervisor', '').strip(),
                'Terminated': 'Yes' if row.get('Employee Status Code', '').strip() != 'A' else 'No',
                'Termination Date': row.get('Termination Date', '').strip() if row.get('Employee Status Code', '').strip() != 'A' else '',
                'Employment Date': row.get('Hire Date', '').strip(),
                'Phone': row.get('Phone', '').strip(),
                'Employee Id': employee_id,

                # PRESERVE existing points data if it exists
                'points': existing.get('points', Decimal('0.0')) if existing else Decimal('0.0'),
                'Panda Points': existing.get('Panda Points', Decimal('0.0')) if existing else Decimal('0.0'),
                'points_budget': existing.get('points_budget', Decimal('0.0')) if existing else Decimal('0.0'),

                # Preserve other important fields
                'points_manager': existing.get('points_manager', 'No') if existing else 'No',
                'is_supervisor': existing.get('is_supervisor', 'No') if existing else 'No',
                'password': existing.get('password', 'Panda2025!') if existing else 'Panda2025!',
                'last_login': existing.get('last_login', '') if existing else '',

                # Update timestamp
                'updated_at': datetime.utcnow().isoformat(),

                # Merch fields
                'Merch Requested': existing.get('Merch Requested', '') if existing else '',
                'Merch Sent': existing.get('Merch Sent', 'No') if existing else 'No',
                'Merch Sent Date': existing.get('Merch Sent Date', '') if existing else '',
                'Years of Service': existing.get('Years of Service', '') if existing else ''
            }

            # Update or create employee
            table.put_item(Item=employee_data)
            updated_count += 1

            if email or work_email:
                with_emails += 1
                status = "✓" if row.get('Employee Status Code', '').strip() == 'A' else "○"
                print(f"{status} {employee_data['name']:35} Email: {email:40} Status: {'Active' if status == '✓' else 'Terminated'}")
            else:
                without_emails += 1
                print(f"○ {employee_data['name']:35} NO EMAILS")

    print(f"\n{'='*100}")
    print(f"IMPORT COMPLETE")
    print(f"{'='*100}")
    print(f"Total employees updated: {updated_count}")
    print(f"  With emails: {with_emails} ({with_emails/updated_count*100:.1f}%)")
    print(f"  Without emails: {without_emails} ({without_emails/updated_count*100:.1f}%)")
    print(f"{'='*100}")

if __name__ == '__main__':
    print(f"Importing employees from: {CSV_FILE}")
    print(f"Target DynamoDB table: panda-employees (us-east-2)")
    print(f"{'='*100}\n")

    import_employees()

    print(f"\n✅ Import complete! Employee data updated in DynamoDB.")
    print(f"\nNext steps:")
    print(f"  1. Test the employee search at https://www.pandaadmin.com/assets.html")
    print(f"  2. Verify emails appear in the admin dashboard")
