#!/usr/bin/env python3

import csv
import boto3
import json
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
employees_table = dynamodb.Table('panda-employees')

def update_employee_points():
    csv_file = '/Users/robwinters/Downloads/user_export_2025-10-06-02-15-30 - Sheet1.csv'
    
    updated_count = 0
    not_found_count = 0
    
    print("Starting points update from CSV...")
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            email = row['Email'].strip().lower()
            name = row['Name'].strip()
            points = int(row['Points']) if row['Points'] else 0
            
            print(f"Processing: {name} ({email}) - {points} points")
            
            try:
                # Find employee by email
                response = employees_table.scan(
                    FilterExpression='#email = :email',
                    ExpressionAttributeNames={'#email': 'Email'},
                    ExpressionAttributeValues={':email': email}
                )
                
                if response['Items']:
                    employee = response['Items'][0]
                    emp_id = employee.get('id') or employee.get('employee_id') or employee.get('Employee Id')
                    
                    # Update points
                    employees_table.put_item(Item={
                        **employee,
                        'points': Decimal(str(points)),
                        'Panda Points': Decimal(str(points)),
                        'updated_at': '2025-01-15T12:00:00Z'
                    })
                    
                    print(f"✅ Updated {name}: {points} points")
                    updated_count += 1
                    
                else:
                    print(f"❌ Employee not found: {name} ({email})")
                    not_found_count += 1
                    
            except Exception as e:
                print(f"❌ Error updating {name}: {e}")
                not_found_count += 1
    
    print(f"\n📊 Summary:")
    print(f"✅ Updated: {updated_count} employees")
    print(f"❌ Not found: {not_found_count} employees")
    print(f"📝 Total processed: {updated_count + not_found_count} records")

if __name__ == "__main__":
    update_employee_points()