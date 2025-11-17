#!/usr/bin/env python3
"""
Import employees from CSV file directly to DynamoDB
FIXED VERSION - November 2025
- Corrected 'Work Email' column mapping
- Fixed First Name mapping
- Fixed Hire Date mapping
- Improved Manager/Supervisor field handling
"""
import boto3
import csv
from datetime import datetime
from decimal import Decimal

# CSV file path - UPDATE THIS TO YOUR LATEST CSV FILE
CSV_FILE = '/Users/robwinters/Downloads/Active_Headcount__location_and_email_ (5) - Report.csv'

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

def parse_supervisor_name(supervisor_str):
    """
    Parse supervisor name from 'Last, First' format to 'First Last'
    Example: 'Daniel, Jason' -> 'Jason Daniel'
    """
    if not supervisor_str or supervisor_str.strip() == '':
        return ''

    supervisor_str = supervisor_str.strip()

    # Handle 'Last, First' format
    if ',' in supervisor_str:
        parts = supervisor_str.split(',')
        if len(parts) == 2:
            last_name = parts[0].strip()
            first_name = parts[1].strip()
            return f"{first_name} {last_name}"

    # If no comma, return as-is
    return supervisor_str

def import_employees():
    """Import employees from CSV to DynamoDB"""

    # Get all existing employee IDs
    existing_employee_ids = get_all_existing_employees()

    updated_count = 0
    new_count = 0
    with_emails = 0
    without_emails = 0
    csv_employee_ids = set()

    # Track issues
    missing_first_name = []
    missing_hire_date = []
    missing_supervisor = []

    print(f"\nImporting from: {CSV_FILE}\n")

    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Skip empty rows
            if not row.get('Employee Id') or not row.get('Last Name'):
                continue

            employee_id = row.get('Employee Id', '').strip()

            # FIXED: Correctly read First Name from CSV
            first_name = row.get('First Name', '').strip()
            last_name = row.get('Last Name', '').strip()

            # Track missing data
            if not first_name:
                missing_first_name.append(f"{employee_id} - {last_name}")

            # Track which employees are in the CSV
            csv_employee_ids.add(employee_id)

            # FIXED: Correctly read Work Email column (was 'Current Work Email')
            personal_email = row.get('Email', '').strip()
            work_email = row.get('Work Email', '').strip()

            # Determine if terminated based on Employee Status Code
            status_code = row.get('Employee Status Code', '').strip()
            terminated = 'Yes' if status_code != 'A' else 'No'

            # FIXED: Correctly read Hire Date
            hire_date = row.get('Hire Date', '').strip()
            if not hire_date:
                missing_hire_date.append(f"{employee_id} - {first_name} {last_name}")

            # FIXED: Parse Supervisor field from 'Last, First' to 'First Last'
            supervisor_raw = row.get('Supervisor', '').strip()
            supervisor = parse_supervisor_name(supervisor_raw)
            if not supervisor:
                missing_supervisor.append(f"{employee_id} - {first_name} {last_name}")

            # Create employee record with CORRECTED field mappings
            employee_data = {
                'employee_id': employee_id,
                'id': employee_id,

                # FIXED: First Name now correctly mapped
                'first_name': first_name,
                'last_name': last_name,
                'First Name': first_name,
                'Last Name': last_name,
                'name': f"{first_name} {last_name}",

                # FIXED: Work Email correctly mapped to 'Work Email' column
                'Email': personal_email,
                'email': personal_email.lower() if personal_email else '',
                'Work Email': work_email,
                'work_email': work_email.lower() if work_email else '',

                # Department and Position
                'Department': row.get('Department Description', '').strip(),
                'department': row.get('Department Description', '').strip(),
                'Position': row.get('Position Description', '').strip() or row.get('Job Title (PIT)', '').strip(),
                'office': row.get('Current Work Location Name', '').strip(),
                'Office Location': row.get('Current Work Location Name', '').strip(),

                # FIXED: Supervisor field now correctly parsed
                'supervisor': supervisor,
                'supervisor_raw': supervisor_raw,  # Keep original for debugging

                # Status fields
                'Terminated': terminated,
                'Employee Status Code': status_code,

                # FIXED: Hire Date correctly mapped
                'Employment Date': hire_date,
                'hire_date': hire_date,
                'Hire Date': hire_date,
                'Rehire Date': row.get('Rehire Date', '').strip(),

                # Employment details
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

            # Display progress
            if personal_email or work_email:
                with_emails += 1
                status_icon = "+" if is_new else "✓"
                term_status = " [TERMINATED]" if terminated == 'Yes' else ""
                supervisor_display = f" | Mgr: {supervisor}" if supervisor else ""
                hire_display = f" | Hired: {hire_date}" if hire_date else ""
                print(f"{status_icon} {employee_data['name']:30} Work: {work_email:40}{supervisor_display}{hire_display}{term_status}")
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
                    Key={'id': emp_id},
                    UpdateExpression='SET #term = :term, updated_at = :updated',
                    ExpressionAttributeNames={
                        '#term': 'Terminated'
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

    # Print summary
    print(f"\n{'='*80}")
    print(f"IMPORT COMPLETE")
    print(f"{'='*80}")
    print(f"Total employees in CSV: {updated_count}")
    print(f"  New employees: {new_count}")
    print(f"  Updated existing: {updated_count - new_count}")
    print(f"  With emails: {with_emails} ({with_emails/updated_count*100:.1f}%)")
    print(f"  Without emails: {without_emails} ({without_emails/updated_count*100:.1f}%)")
    print(f"\nEmployees marked as terminated: {terminated_count}")

    # Report data quality issues
    if missing_first_name or missing_hire_date or missing_supervisor:
        print(f"\n{'='*80}")
        print(f"DATA QUALITY ISSUES")
        print(f"{'='*80}")

        if missing_first_name:
            print(f"\n⚠️  Missing First Name ({len(missing_first_name)} employees):")
            for emp in missing_first_name[:10]:
                print(f"   - {emp}")
            if len(missing_first_name) > 10:
                print(f"   ... and {len(missing_first_name) - 10} more")

        if missing_hire_date:
            print(f"\n⚠️  Missing Hire Date ({len(missing_hire_date)} employees):")
            for emp in missing_hire_date[:10]:
                print(f"   - {emp}")
            if len(missing_hire_date) > 10:
                print(f"   ... and {len(missing_hire_date) - 10} more")

        if missing_supervisor:
            print(f"\n⚠️  Missing Supervisor ({len(missing_supervisor)} employees):")
            for emp in missing_supervisor[:10]:
                print(f"   - {emp}")
            if len(missing_supervisor) > 10:
                print(f"   ... and {len(missing_supervisor) - 10} more")

    print(f"\n{'='*80}")

if __name__ == '__main__':
    print(f"{'='*80}")
    print(f"EMPLOYEE IMPORT - FIXED VERSION (November 2025)")
    print(f"{'='*80}")
    print(f"CSV File: {CSV_FILE}")
    print(f"DynamoDB Table: panda-employees")
    print(f"Region: us-east-2")
    print(f"{'='*80}\n")

    print("FIXES APPLIED:")
    print("  ✓ First Name column mapping corrected")
    print("  ✓ Work Email column mapping corrected (was 'Current Work Email')")
    print("  ✓ Hire Date field mapping corrected")
    print("  ✓ Supervisor field parsing fixed ('Last, First' → 'First Last')")
    print(f"{'='*80}\n")

    import_employees()
