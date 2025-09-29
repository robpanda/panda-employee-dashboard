import requests
import json

# Test the new Lambda function
API_URL = 'https://dfu3zr3dnrvgiiwa2yu77cz5fq0rqmth.lambda-url.us-east-2.on.aws'

print("Testing Lambda function...")

# Test import from Google Sheets
print("\n1. Testing Google Sheets import...")
try:
    response = requests.post(f'{API_URL}/import')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test getting employees
print("\n2. Testing get employees...")
try:
    response = requests.get(f'{API_URL}/employees')
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found {len(data)} employees")
    if data:
        print(f"First employee: {data[0].get('name', 'No name')}")
except Exception as e:
    print(f"Error: {e}")