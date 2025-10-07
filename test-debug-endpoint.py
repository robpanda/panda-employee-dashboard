import requests
import json

# Test debug endpoint to see Lambda function version
API_URL = 'https://dfu3zr3dnrvgiiwa2yu77cz5fq0rqmth.lambda-url.us-east-2.on.aws'

def test_debug():
    print("Testing debug endpoint...")
    
    try:
        response = requests.get(f'{API_URL}/debug', timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

if __name__ == "__main__":
    test_debug()