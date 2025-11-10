#!/usr/bin/env python3
"""
Import employees from CSV file directly to DynamoDB
CORRECTED VERSION - Uses proper column names and handles terminations
"""
import boto3
import csv
from datetime import datetime
from decimal import Decimal

# CSV file path
CSV_FILE = '/Users/robwinters/Downloads/Active_Headcount__location_and_email_ (3) - Report.csv'

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def get_all_existing_employees():
    """Get all existing employee IDs from DynamoDB"""
    print("Fetching existing employees from DynamoDB...")
    response = table.scan(ProjectionExpression='id')
    employee_ids = set()

    for item in response.get('Items', []):
        if 'id' in item:
            employee_ids.add(item['id'])

    # Handle pagination
    while 'LastEvaluatedKey' in response:
        response = table.scan(
            ProjectionExpression='id',
            ExclusiveStartKey=response['LastEvaluatedKey']
        )
        for item in response.get('Items', []):
            if 'id' in item:
                employee_ids.add(item['id'])

    print(f"Found {len(employee_ids)} existing employees in DynamoDB")
    return employee_ids

def import_employees():
    """Import employees from CSV to DynamoDB"""

    # Get all existing employee IDs
    existing_employee_ids = get_all_existing_employees()

    updated_count = 0
    new_count = 0
    with_emails = 0
    without_emails = 0
    csv_employee_ids = set()

    print(f"\nImporting from: {CSV_FILE}\n")

    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Skip empty rows
            if not row.get('Employee Id') or not row.get('Last Name'):
                continue

            employee_id = row.get('Employee Id', '').strip()
            first_name = row.get('First Name', '').strip()
            last_name = row.get('Last Name', '').strip()

            # Track which employees are in the CSV
            csv_employee_ids.add(employee_id)

            # READ ACTUAL EMAIL COLUMNS FROM CSV - CORRECTED COLUMN NAMES
            email = row.get('Email', '').strip()
            work_email = row.get('Current Work Email', '').strip()  # FIXED: Was 'Work Email'

            # Determine if terminated based on Employee Status Code
            status_code = row.get('Employee Status Code', '').strip()
            terminated = 'Yes' if status_code != 'A' else 'No'

            # Create employee record with ACTUAL emails from CSV
            employee_data = {
                'employee_id': employee_id,
                'id': employee_id,
                'first_name': first_name,
                'last_name': last_name,
                'First Name': first_name,
                'Last Name': last_name,
                'name': f"{first_name} {last_name}",

                # CORRECTED: Using 'Current Work Email' from CSV
                'Email': email,
                'email': email.lower() if email else '',
                'Work Email': work_email,
                'work_email': work_email.lower() if work_email else '',

                # Other fields
                'Department': row.get('Department Description', '').strip(),
                'department': row.get('Department Description', '').strip(),
                'Position': row.get('Position Description', '').strip() or row.get('Job Title (PIT)', '').strip(),
                'office': row.get('Current Work Location Name', '').strip(),
                'Office Location': row.get('Current Work Location Name', '').strip(),
                'supervisor': row.get('Supervisor', '').strip(),
                'Terminated': terminated,
                'Employee Status Code': status_code,
                'Employment Date': row.get('Hire Date', '').strip(),
                'Rehire Date': row.get('Rehire Date', '').strip(),
                'Employment Type': row.get('Employment Type Description', '').strip(),
                'Job Title': row.get('Job Title (PIT)', '').strip(),
                'Phone': row.get('Phone', '').strip() if row.get('Phone') else '',

                # Default values
                'points': Decimal('0.0'),
                'Panda Points': Decimal('0.0'),
                'points_budget': Decimal('0.0'),
                'points_manager': 'No',
                'is_supervisor': 'No',
                'password': 'Panda2025!',
                'updated_at': datetime.utcnow().isoformat(),
                'Merch Requested': '',
                'Merch Sent': 'No',
                'Merch Sent Date': '',
                'Years of Service': ''
            }

            # Check if this is a new employee
            is_new = employee_id not in existing_employee_ids
            if is_new:
                new_count += 1

            # Update or create employee
            table.put_item(Item=employee_data)
            updated_count += 1

            if email or work_email:
                with_emails += 1
                status_icon = "+" if is_new else "✓"
                term_status = " [TERMINATED]" if terminated == 'Yes' else ""
                print(f"{status_icon} {employee_data['name']:30} Email: {email:40} Work: {work_email}{term_status}")
            else:
                without_emails += 1
                status_icon = "+" if is_new else "○"
                term_status = " [TERMINATED]" if terminated == 'Yes' else ""
                print(f"{status_icon} {employee_data['name']:30} NO EMAILS{term_status}")

    # Find employees that were in DynamoDB but NOT in the CSV (should be marked as terminated)
    missing_employee_ids = existing_employee_ids - csv_employee_ids
    terminated_count = 0

    if missing_employee_ids:
        print(f"\n{'='*80}")
        print(f"MARKING EMPLOYEES AS TERMINATED (not in CSV)")
        print(f"{'='*80}")

        for emp_id in missing_employee_ids:
            try:
                table.update_item(
                    Key={'id': emp_id},  # Fixed: Use 'id' as the primary key, not 'employee_id'
                    UpdateExpression='SET #term = :term, updated_at = :updated',
                    ExpressionAttributeNames={
                        '#term': 'Terminated'  # Use placeholder for reserved keyword
                    },
                    ExpressionAttributeValues={
                        ':term': 'Yes',
                        ':updated': datetime.utcnow().isoformat()
                    }
                )
                terminated_count += 1
                print(f"✗ Marked employee {emp_id} as terminated")
            except Exception as e:
                print(f"Error updating employee {emp_id}: {e}")

    print(f"\n{'='*80}")
    print(f"IMPORT COMPLETE")
    print(f"{'='*80}")
    print(f"Total employees in CSV: {updated_count}")
    print(f"  New employees: {new_count}")
    print(f"  Updated existing: {updated_count - new_count}")
    print(f"  With emails: {with_emails} ({with_emails/updated_count*100:.1f}%)")
    print(f"  Without emails: {without_emails} ({without_emails/updated_count*100:.1f}%)")
    print(f"\nEmployees marked as terminated: {terminated_count}")
    print(f"{'='*80}")

if __name__ == '__main__':
    print(f"{'='*80}")
    print(f"EMPLOYEE IMPORT - CORRECTED VERSION")
    print(f"{'='*80}")
    print(f"CSV File: {CSV_FILE}")
    print(f"DynamoDB Table: panda-employees")
    print(f"Region: us-east-2")
    print(f"{'='*80}\n")

    import_employees()
