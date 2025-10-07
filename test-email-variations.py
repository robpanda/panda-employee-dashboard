import requests
import json

# Test different email variations
API_URL = 'https://dfu3zr3dnrvgiiwa2yu77cz5fq0rqmth.lambda-url.us-east-2.on.aws'

def test_variations():
    variations = [
        'drjwoo88@gmail.com',
        'DRJWOO88@GMAIL.COM',
        ' drjwoo88@gmail.com ',
        'drjwoo88@gmail.com\n',
        'drjwoo88@gmail.com\r'
    ]
    
    for email in variations:
        print(f"Testing email: '{email}' (length: {len(email)})")
        
        login_data = {
            'email': email,
            'password': 'Panda2025!'
        }
        
        try:
            response = requests.post(f'{API_URL}/admin-login', 
                                   headers={'Content-Type': 'application/json'},
                                   json=login_data,
                                   timeout=10)
            
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"  ✅ SUCCESS!")
                    admin = data.get('admin', {})
                    print(f"     Name: {admin.get('name')}")
                    print(f"     Role: {admin.get('role')}")
                    break
                else:
                    print(f"  ❌ Failed: {data.get('error')}")
            else:
                print(f"  ❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
        
        print()

if __name__ == "__main__":
    test_variations()