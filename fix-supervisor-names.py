#!/usr/bin/env python3
import requests
import json

API_URL = 'https://dfu3zr3dnrvgiiwa2yu77cz5fq0rqmth.lambda-url.us-east-2.on.aws'

def fix_supervisor_names():
    """Fix supervisor names from 'Last, First' to 'First Last' format"""
    try:
        # Get all employees
        response = requests.get(f'{API_URL}/employees')
        data = response.json()
        employees = data.get('employees', data) if isinstance(data, dict) else data
        
        # Create mapping of "Last, First" to "First Last"
        name_mapping = {}
        for emp in employees:
            first = emp.get('First Name', '')
            last = emp.get('Last Name', '')
            if first and last:
                old_format = f"{last}, {first}"
                new_format = f"{first} {last}"
                name_mapping[old_format] = new_format
        
        # Update employees with supervisor names in old format
        updates_made = 0
        for emp in employees:
            supervisor = emp.get('supervisor', '')
            if supervisor and supervisor in name_mapping:
                emp_id = emp.get('id') or emp.get('employee_id')
                new_supervisor = name_mapping[supervisor]
                
                if emp_id:
                    update_response = requests.put(
                        f'{API_URL}/employees/{emp_id}',
                        headers={'Content-Type': 'application/json'},
                        json={'supervisor': new_supervisor}
                    )
                    
                    if update_response.ok:
                        emp_name = f"{emp.get('First Name', '')} {emp.get('Last Name', '')}".strip()
                        print(f"✅ Updated {emp_name}: {supervisor} → {new_supervisor}")
                        updates_made += 1
                    else:
                        print(f"❌ Failed to update {emp_id}: {update_response.text}")
        
        print(f"\n✅ Updated {updates_made} supervisor assignments")
        
    except Exception as e:
        print(f"❌ Error fixing supervisor names: {str(e)}")

if __name__ == "__main__":
    print("Fixing supervisor name formats...")
    fix_supervisor_names()
    print("Done!")