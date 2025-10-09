import requests
import json

def test_colin_login():
    url = "https://dfu3zr3dnrvgiiwa2yu77cz5fq0rqmth.lambda-url.us-east-2.on.aws/employee-login"
    
    payload = {
        "email": "colin.yoster@gmail.com",
        "password": "Panda2025!"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("🔍 Testing Colin's login...")
        print(f"URL: {url}")
        print(f"Email: {payload['email']}")
        print(f"Password: {payload['password']}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"\n📡 Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"Response Body: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
        else:
            print("❌ Login failed!")
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

if __name__ == "__main__":
    test_colin_login()