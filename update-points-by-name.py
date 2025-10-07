#!/usr/bin/env python3

import csv
import boto3
import json
from decimal import Decimal
import re

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
employees_table = dynamodb.Table('panda-employees')

def normalize_name(name):
    """Normalize name for comparison"""
    return re.sub(r'[^a-zA-Z\s]', '', name.lower().strip())

def update_employee_points():
    csv_file = '/Users/robwinters/Downloads/user_export_2025-10-06-02-15-30 - Sheet1.csv'
    
    # First, get all employees from database
    print("Loading employees from database...")
    response = employees_table.scan()
    employees = response['Items']
    print(f"Loaded {len(employees)} employees from database")
    
    updated_count = 0
    not_found_count = 0
    
    print("\nStarting points update from CSV...")
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            csv_email = row['Email'].strip()
            csv_name = row['Name'].strip()
            points = int(row['Points']) if row['Points'] else 0
            
            print(f"Processing: {csv_name} - {points} points")
            
            # Try to find employee by name matching
            found_employee = None
            
            # Normalize CSV name for comparison
            csv_name_norm = normalize_name(csv_name)
            
            for emp in employees:
                # Try different name combinations
                first_name = emp.get('First Name', '') or emp.get('first_name', '')
                last_name = emp.get('Last Name', '') or emp.get('last_name', '')
                full_name = f"{first_name} {last_name}".strip()
                
                # Also try the 'name' field if it exists
                name_field = emp.get('name', '')
                
                # Normalize database names
                full_name_norm = normalize_name(full_name)
                name_field_norm = normalize_name(name_field)
                
                # Check for matches
                if (csv_name_norm == full_name_norm or 
                    csv_name_norm == name_field_norm or
                    csv_name_norm in full_name_norm or
                    full_name_norm in csv_name_norm):
                    
                    found_employee = emp
                    print(f"  ✅ Matched with: {full_name} (DB: {emp.get('Email', 'no email')})")
                    break
            
            if found_employee:
                try:
                    # Update points
                    employees_table.put_item(Item={
                        **found_employee,
                        'points': Decimal(str(points)),
                        'Panda Points': Decimal(str(points)),
                        'updated_at': '2025-01-15T12:00:00Z'
                    })
                    
                    print(f"  ✅ Updated points: {points}")
                    updated_count += 1
                    
                except Exception as e:
                    print(f"  ❌ Error updating: {e}")
                    not_found_count += 1
            else:
                print(f"  ❌ No match found for: {csv_name}")
                not_found_count += 1
    
    print(f"\n📊 Summary:")
    print(f"✅ Updated: {updated_count} employees")
    print(f"❌ Not found: {not_found_count} employees")
    print(f"📝 Total processed: {updated_count + not_found_count} records")

if __name__ == "__main__":
    update_employee_points()