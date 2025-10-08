#!/usr/bin/env python3
import requests
import json

API_URL = 'https://dfu3zr3dnrvgiiwa2yu77cz5fq0rqmth.lambda-url.us-east-2.on.aws'

# List of points_admin users who need points permissions
points_admins = [
    'Edwardfwhelan5@gmail.com',
    'jkonstandinidis@gmail.com', 
    'amprovinzano@gmail.com',
    'yaliaksandra@yahoo.com',
    'Trev2024@gmail.com',
    'rpalmer1050@gmail.com',
    'vliebno@outlook.com',
    'jrmcginnis@me.com',
    'Babel462@gmail.com',
    'sandberg.todd.d@gmail.com',
    'scotttucker@panda-exteriors.com',
    'AndrewL2288@Hotmail.com',
    'tommyhallwig@pandaexteriors.com',
    'mattmarkey@pandaexteriors.com',
    'Jarpan@pandaexteriors.com',
    'joe.larose55@gmail.com',
    'cjcurry2@gmail.com',
    'drjwoo88@gmail.com',
    'andreasg418@gmail.com',
    'mackgk1@gmail.com',
    'cheynekilbourne@panda-exteriors.com',
    'suttongasper@gmail.com'
]

def update_admin_permissions():
    """Update all points_admin users to have points permissions"""
    for email in points_admins:
        try:
            response = requests.put(
                f'{API_URL}/admin-users/{email}',
                headers={'Content-Type': 'application/json'},
                json={
                    'role': 'points_admin',
                    'active': True,
                    'permissions': ['points']
                }
            )
            
            if response.ok:
                print(f"✅ Updated permissions for {email}")
            else:
                print(f"❌ Failed to update {email}: {response.text}")
                
        except Exception as e:
            print(f"❌ Error updating {email}: {str(e)}")

def setup_managers():
    """Set up admin users as managers in the employee database"""
    try:
        # Get all employees
        response = requests.get(f'{API_URL}/employees')
        data = response.json()
        employees = data.get('employees', data) if isinstance(data, dict) else data
        
        for email in points_admins:
            # Find employee by email
            employee = None
            for emp in employees:
                emp_email = (emp.get('Email') or emp.get('email') or '').lower()
                if emp_email == email.lower():
                    employee = emp
                    break
            
            if employee:
                emp_id = employee.get('id') or employee.get('employee_id')
                if emp_id:
                    # Update employee to be supervisor and points manager
                    update_response = requests.put(
                        f'{API_URL}/employees/{emp_id}',
                        headers={'Content-Type': 'application/json'},
                        json={
                            'is_supervisor': 'Yes',
                            'points_manager': 'Yes', 
                            'points_budget': 500
                        }
                    )
                    
                    if update_response.ok:
                        name = f"{employee.get('First Name', '')} {employee.get('Last Name', '')}".strip()
                        print(f"✅ Set up {name} ({email}) as manager")
                    else:
                        print(f"❌ Failed to update employee {email}: {update_response.text}")
                else:
                    print(f"⚠️  No employee ID found for {email}")
            else:
                print(f"⚠️  Employee not found for {email}")
                
    except Exception as e:
        print(f"❌ Error setting up managers: {str(e)}")

if __name__ == "__main__":
    print("Updating admin permissions...")
    update_admin_permissions()
    
    print("\nSetting up managers...")
    setup_managers()
    
    print("\nDone!")