import requests
import json

def test_full_login_flow():
    base_url = "https://dfu3zr3dnrvgiiwa2yu77cz5fq0rqmth.lambda-url.us-east-2.on.aws"
    
    # Test login
    login_payload = {
        "email": "colin.yoster@gmail.com",
        "password": "Panda2025!"
    }
    
    print("🔍 Testing full login flow for Colin...")
    
    try:
        # Step 1: Test login
        print("\\n1️⃣ Testing login endpoint...")
        login_response = requests.post(f"{base_url}/employee-login", json=login_payload, timeout=30)
        
        print(f"Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            print("✅ Login successful!")
            print(f"Employee data: {json.dumps(login_data, indent=2)}")
            
            employee = login_data.get('employee', {})
            employee_id = employee.get('id') or employee.get('employee_id')
            
            if employee_id:
                # Step 2: Test employee data fetch
                print(f"\\n2️⃣ Testing employee data fetch for ID: {employee_id}...")
                employee_response = requests.get(f"{base_url}/employees?email={employee.get('email')}", timeout=30)
                
                print(f"Status: {employee_response.status_code}")
                if employee_response.status_code == 200:
                    emp_data = employee_response.json()
                    print("✅ Employee data fetch successful!")
                    print(f"Found {len(emp_data.get('employees', []))} employees")
                else:
                    print(f"❌ Employee data fetch failed: {employee_response.text}")
                
                # Step 3: Test referrals fetch
                print(f"\\n3️⃣ Testing referrals fetch...")
                referrals_response = requests.get(f"{base_url}/referrals/employee/{employee_id}", timeout=30)
                
                print(f"Status: {referrals_response.status_code}")
                if referrals_response.status_code == 200:
                    ref_data = referrals_response.json()
                    print("✅ Referrals fetch successful!")
                    print(f"Found {len(ref_data.get('referrals', []))} referrals")
                else:
                    print(f"❌ Referrals fetch failed: {referrals_response.text}")
            
        else:
            print(f"❌ Login failed!")
            try:
                error_data = login_response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Response: {login_response.text}")
        
        # Step 4: Test general endpoints
        print(f"\\n4️⃣ Testing general endpoints...")
        
        # Test employees endpoint
        employees_response = requests.get(f"{base_url}/employees", timeout=30)
        print(f"Employees endpoint: {employees_response.status_code}")
        
        # Test referrals endpoint
        referrals_response = requests.get(f"{base_url}/referrals", timeout=30)
        print(f"Referrals endpoint: {referrals_response.status_code}")
        
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_login_flow()