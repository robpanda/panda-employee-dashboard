import requests
import json

# Test admin login for drjwoo88@gmail.com
API_URL = 'https://dfu3zr3dnrvgiiwa2yu77cz5fq0rqmth.lambda-url.us-east-2.on.aws'

def test_admin_login():
    login_data = {
        'email': 'drjwoo88@gmail.com',
        'password': 'Panda2025!'
    }
    
    try:
        response = requests.post(f'{API_URL}/admin-login', 
                               headers={'Content-Type': 'application/json'},
                               json=login_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                admin = data.get('admin', {})
                print(f"✅ Login successful!")
                print(f"   Name: {admin.get('name')}")
                print(f"   Role: {admin.get('role')}")
                print(f"   Permissions: {admin.get('permissions')}")
                print(f"   Restricted Access: {admin.get('restricted_access', False)}")
                print(f"   Points Budget: {admin.get('points_budget', 0)}")
            else:
                print(f"❌ Login failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

if __name__ == "__main__":
    test_admin_login()