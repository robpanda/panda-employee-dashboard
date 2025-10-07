#!/usr/bin/env python3

import boto3
import json

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
employees_table = dynamodb.Table('panda-employees')

def check_employee_emails():
    print("Checking employee emails in database...")
    
    try:
        response = employees_table.scan()
        employees = response['Items']
        
        print(f"Found {len(employees)} employees in database")
        print("\nFirst 10 employee emails:")
        
        for i, emp in enumerate(employees[:10]):
            email = emp.get('Email') or emp.get('email') or 'NO EMAIL'
            name = f"{emp.get('First Name', '')} {emp.get('Last Name', '')}".strip()
            if not name:
                name = emp.get('name', 'NO NAME')
            
            print(f"{i+1}. {name} - {email}")
            
        # Check for specific emails from CSV
        csv_emails = [
            'mikestuart@pandaexteriors.com',
            'jimmycoggin@pandaexteriors.com', 
            'kevinflores@pandaexteriors.com'
        ]
        
        print(f"\nChecking for CSV emails in database:")
        for csv_email in csv_emails:
            found = False
            for emp in employees:
                db_email = (emp.get('Email') or emp.get('email') or '').lower()
                if db_email == csv_email.lower():
                    name = f"{emp.get('First Name', '')} {emp.get('Last Name', '')}".strip()
                    print(f"✅ Found: {csv_email} -> {name}")
                    found = True
                    break
            if not found:
                print(f"❌ Not found: {csv_email}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_employee_emails()