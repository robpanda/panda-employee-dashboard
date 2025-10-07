import requests
import json

# Test super admin login
API_URL = 'https://dfu3zr3dnrvgiiwa2yu77cz5fq0rqmth.lambda-url.us-east-2.on.aws'

def test_super_admin():
    login_data = {
        'email': 'admin',
        'password': 'admin123'
    }
    
    print("Testing super admin login...")
    
    try:
        response = requests.post(f'{API_URL}/admin-login', 
                               headers={'Content-Type': 'application/json'},
                               json=login_data,
                               timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Super admin login works!")
            else:
                print("❌ Super admin login failed")
        
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

if __name__ == "__main__":
    test_super_admin()