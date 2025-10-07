import requests
import json

# Test employees endpoint to see if database connection works
API_URL = 'https://dfu3zr3dnrvgiiwa2yu77cz5fq0rqmth.lambda-url.us-east-2.on.aws'

def test_employees():
    print("Testing employees endpoint...")
    
    try:
        response = requests.get(f'{API_URL}/employees', timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            employees = data.get('employees', [])
            print(f"✅ Found {len(employees)} employees")
            
            # Look for drjwoo88@gmail.com
            drjwoo = None
            for emp in employees:
                if emp.get('Email') == 'drjwoo88@gmail.com':
                    drjwoo = emp
                    break
            
            if drjwoo:
                print(f"✅ Found drjwoo88@gmail.com:")
                print(f"   Name: {drjwoo.get('First Name')} {drjwoo.get('Last Name')}")
                print(f"   ID: {drjwoo.get('id')}")
                print(f"   Points Manager: {drjwoo.get('points_manager')}")
                print(f"   Password: {drjwoo.get('password')}")
            else:
                print("❌ drjwoo88@gmail.com not found in employees list")
        else:
            print(f"❌ Error: {response.text}")
        
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

if __name__ == "__main__":
    test_employees()