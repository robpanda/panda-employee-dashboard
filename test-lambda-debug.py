import requests
import json

# Test admin login with debug info
API_URL = 'https://dfu3zr3dnrvgiiwa2yu77cz5fq0rqmth.lambda-url.us-east-2.on.aws'

def test_debug():
    # Test with exact email from database
    login_data = {
        'email': 'drjwoo88@gmail.com',
        'password': 'Panda2025!'
    }
    
    print("Testing admin login...")
    print(f"Email: '{login_data['email']}'")
    print(f"Password: '{login_data['password']}'")
    
    try:
        response = requests.post(f'{API_URL}/admin-login', 
                               headers={'Content-Type': 'application/json'},
                               json=login_data,
                               timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response: {response.text}")
        
        # Also test employee login to see if that works
        print("\n--- Testing employee login ---")
        emp_response = requests.post(f'{API_URL}/employee-login', 
                                   headers={'Content-Type': 'application/json'},
                                   json=login_data,
                                   timeout=30)
        
        print(f"Employee Login Status: {emp_response.status_code}")
        print(f"Employee Login Response: {emp_response.text}")
        
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

if __name__ == "__main__":
    test_debug()