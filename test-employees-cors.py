import requests

# Test employees endpoint CORS
API_URL = 'https://dfu3zr3dnrvgiiwa2yu77cz5fq0rqmth.lambda-url.us-east-2.on.aws'

def test_employees_cors():
    print("Testing employees endpoint CORS...")
    
    try:
        response = requests.get(f'{API_URL}/employees', timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"CORS Headers: {response.headers.get('Access-Control-Allow-Origin', 'NOT FOUND')}")
        print(f"All Headers: {dict(response.headers)}")
        
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

if __name__ == "__main__":
    test_employees_cors()