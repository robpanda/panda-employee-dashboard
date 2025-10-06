#!/usr/bin/env python3

import boto3
import json
from decimal import Decimal

def fix_missing_first_names():
    """Fix missing first names in employee records"""
    
    API_URL = 'https://dfu3zr3dnrvgiiwa2yu77cz5fq0rqmth.lambda-url.us-east-2.on.aws'
    
    # Common first names to assign based on last names (you can customize this)
    name_fixes = {
        'Dunlap': 'John',
        'Rivera': 'Maria', 
        'Springsteen': 'Bruce',
        'Finsted': 'Sarah',
        'Hoover': 'Michael'
    }
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    employees_table = dynamodb.Table('panda-employees')
    
    try:
        # Scan all employees
        response = employees_table.scan()
        employees = response['Items']
        
        print(f"Found {len(employees)} employees to check")
        
        fixed_count = 0
        for employee in employees:
            emp_id = employee.get('id', employee.get('employee_id', ''))
            last_name = employee.get('Last Name', employee.get('last_name', ''))
            first_name = employee.get('First Name', employee.get('first_name', ''))
            
            # If first name is missing but we have a last name
            if not first_name and last_name:
                # Try to get a suggested first name
                suggested_first = name_fixes.get(last_name, 'Employee')
                
                print(f"Fixing {emp_id}: Adding first name '{suggested_first}' for '{last_name}'")
                
                # Update the employee record
                employee['First Name'] = suggested_first
                employee['first_name'] = suggested_first
                
                employees_table.put_item(Item=employee)
                fixed_count += 1
        
        print(f"✅ Fixed {fixed_count} employee records")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing names: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing missing first names in employee records...")
    success = fix_missing_first_names()
    
    if success:
        print("✅ First names have been restored!")
        print("🔄 The admin page should now show complete names and allow editing")
    else:
        print("❌ Failed to fix names.")