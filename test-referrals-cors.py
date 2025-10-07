import requests
import json

# Test referrals endpoint CORS
API_URL = 'https://dfu3zr3dnrvgiiwa2yu77cz5fq0rqmth.lambda-url.us-east-2.on.aws'

def test_referrals_cors():
    print("Testing referrals endpoint CORS...")
    
    # Test GET request
    try:
        response = requests.get(f'{API_URL}/referrals/employee/10370', timeout=30)
        
        print(f"GET Status Code: {response.status_code}")
        print(f"CORS Headers: {response.headers.get('Access-Control-Allow-Origin', 'NOT FOUND')}")
        print(f"Response: {response.text[:200]}...")
        
    except Exception as e:
        print(f"❌ GET Request failed: {str(e)}")
    
    # Test POST request
    try:
        test_referral = {
            'name': 'Test Person',
            'email': 'test@example.com',
            'phone': '555-1234',
            'department': 'Sales',
            'referred_by_id': '10370',
            'referred_by_name': 'Test Employee'
        }
        
        response = requests.post(f'{API_URL}/referrals', 
                               headers={'Content-Type': 'application/json'},
                               json=test_referral,
                               timeout=30)
        
        print(f"\nPOST Status Code: {response.status_code}")
        print(f"CORS Headers: {response.headers.get('Access-Control-Allow-Origin', 'NOT FOUND')}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ POST Request failed: {str(e)}")

if __name__ == "__main__":
    test_referrals_cors()