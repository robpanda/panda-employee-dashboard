import boto3

# Test the exact scan logic used in Lambda function
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
employees_table = dynamodb.Table('panda-employees')

def test_scan_logic():
    email = 'drjwoo88@gmail.com'
    password = 'Panda2025!'
    
    print(f"Testing scan logic for: {email}")
    
    try:
        # This is the exact logic from the Lambda function
        response = employees_table.scan()
        manager_employee = None
        
        print(f"Scanned {len(response['Items'])} employees")
        
        for item in response['Items']:
            item_email = item.get('Email', '').strip().lower()
            print(f"Checking: '{item_email}' vs '{email.lower()}'")
            if item_email == email.lower():
                manager_employee = item
                print(f"✅ Found match!")
                break
        
        if manager_employee:
            print(f"Found employee: {manager_employee.get('First Name')} {manager_employee.get('Last Name')}")
            print(f"Points Manager: {manager_employee.get('points_manager')}")
            
            if manager_employee.get('points_manager') == 'Yes':\n                print(\"✅ Is points manager\")\n                stored_password = manager_employee.get('password', 'Panda2025!')\n                print(f\"Stored password: '{stored_password}'\")\n                print(f\"Input password: '{password}'\")\n                print(f\"Password match: {password == stored_password}\")\n            else:\n                print(\"❌ Not a points manager\")\n        else:\n            print(\"❌ No employee found with that email\")\n            \n    except Exception as e:\n        print(f\"❌ Error: {str(e)}\")\n\nif __name__ == \"__main__\":\n    test_scan_logic()