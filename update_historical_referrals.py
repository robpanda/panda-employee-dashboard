#!/usr/bin/env python3
import csv
import json
import boto3
from datetime import datetime
import uuid

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
referrals_table = dynamodb.Table('panda-referrals')
employees_table = dynamodb.Table('panda-employees')

def get_employee_id_by_name(name):
    """Find employee ID by name"""
    try:
        response = employees_table.scan()
        employees = response.get('Items', [])
        
        for employee in employees:
            if employee.get('name', '').lower() == name.lower():
                return employee.get('employee_id')
        return None
    except Exception as e:
        print(f"Error finding employee {name}: {e}")
        return None

def clear_historical_data():
    """Clear existing historical referral data"""
    try:
        response = referrals_table.scan()
        items = response.get('Items', [])
        
        deleted_count = 0
        for item in items:
            # Only delete items with "Historical data import" notes
            if item.get('notes') == 'Historical data import':
                referrals_table.delete_item(Key={'id': item['id']})
                deleted_count += 1
                
                if deleted_count % 10 == 0:
                    print(f"Deleted {deleted_count} historical records...")
        
        print(f"Cleared {deleted_count} historical referral records")
        return deleted_count
    except Exception as e:
        print(f"Error clearing historical data: {e}")
        return 0

def import_corrected_referrals():
    """Import corrected historical referrals from CSV"""
    imported_count = 0
    skipped_count = 0
    
    with open('corrected_historical_referrals.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            try:
                # Skip empty referral names
                if not row['referral_name'].strip():
                    skipped_count += 1
                    continue
                
                # Find referring employee ID
                referred_by_id = get_employee_id_by_name(row['referred_by_name'])
                if not referred_by_id:
                    print(f"Warning: Could not find employee ID for {row['referred_by_name']}")
                    referred_by_id = f"UNKNOWN_{row['referred_by_name'].replace(' ', '_')}"
                
                # Create referral record
                referral_id = str(uuid.uuid4())
                
                referral_data = {
                    'id': referral_id,
                    'name': row['referral_name'].strip(),
                    'email': f"{row['referral_name'].lower().replace(' ', '.')}@example.com",
                    'phone': '000-000-0000',
                    'department': row['department'],
                    'referred_by_id': referred_by_id,
                    'referred_by_name': row['referred_by_name'],
                    'status': row['status'],
                    'phone_screen_complete': row['phone_screen_complete'].lower() == 'true',
                    'created_at': row['created_at'],
                    'notes': 'Historical data import - October 2024'
                }
                
                # Insert into DynamoDB
                referrals_table.put_item(Item=referral_data)
                imported_count += 1
                
                if imported_count % 10 == 0:
                    print(f"Imported {imported_count} corrected referrals...")
                    
            except Exception as e:
                print(f"Error importing referral {row['referral_name']}: {e}")
                skipped_count += 1
                continue
    
    print(f"\nImport complete!")
    print(f"Successfully imported: {imported_count} referrals")
    print(f"Skipped: {skipped_count} referrals")

if __name__ == "__main__":
    print("Starting historical referral data update...")
    print("Step 1: Clearing existing historical data...")
    clear_historical_data()
    print("\nStep 2: Importing corrected data...")
    import_corrected_referrals()