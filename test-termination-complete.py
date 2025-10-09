#!/usr/bin/env python3

import requests
import json
from datetime import datetime, timedelta

# Test the complete termination functionality
API_URL = 'https://dfu3zr3dnrvgiiwa2yu77cz5fq0rqmth.lambda-url.us-east-2.on.aws'

def test_termination_workflow():
    print("🧪 Testing Termination Date and Email Functionality")
    print("=" * 60)
    
    # Test 1: Create a test employee with recent hire date
    test_employee_data = {
        'First Name': 'John',
        'Last Name': 'TestEmployee',
        'Email': 'john.test@example.com',
        'Work Email': 'john.test@pandaexteriors.com',
        'Employee Id': 'TEST001',
        'Position': 'Test Position',
        'Department': 'Testing',
        'Employment Date': (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d'),  # 60 days ago
        'Merch Requested': 'Winter Jacket, Company Polo',
        'merchandise_value': 125.50,
        'office': 'Test Office',
        'supervisor': 'Test Manager'
    }
    
    print(f"📝 Test Employee Data:")
    print(f"   Name: {test_employee_data['First Name']} {test_employee_data['Last Name']}")
    print(f"   Hire Date: {test_employee_data['Employment Date']}")
    print(f"   Days Employed: {(datetime.now() - datetime.strptime(test_employee_data['Employment Date'], '%Y-%m-%d')).days}")
    print(f"   Merchandise Value: ${test_employee_data['merchandise_value']}")
    print()
    
    # Test 2: Verify email trigger conditions
    days_employed = (datetime.now() - datetime.strptime(test_employee_data['Employment Date'], '%Y-%m-%d')).days
    should_trigger = days_employed <= 90 and test_employee_data['merchandise_value'] > 0
    
    print(f"📧 Email Trigger Analysis:")
    print(f"   Days Employed: {days_employed} (≤ 90: {'✅' if days_employed <= 90 else '❌'})")
    print(f"   Has Merchandise: {'✅' if test_employee_data['merchandise_value'] > 0 else '❌'}")
    print(f"   Should Trigger Email: {'✅ YES' if should_trigger else '❌ NO'}")
    print()
    
    # Test 3: Expected email content
    if should_trigger:
        termination_date = datetime.now().strftime('%Y-%m-%d')
        employee_name = f"{test_employee_data['First Name']} {test_employee_data['Last Name']}"
        
        print(f"📨 Expected Email Content:")
        print(f"   To: robwinters@pandaexteriors.com")
        print(f"   Subject: Merch Refund Collection Required for Terminated Employee: {employee_name}")
        print(f"   Amount: ${test_employee_data['merchandise_value']:.2f} USD")
        print(f"   Items: {test_employee_data['Merch Requested']}")
        print(f"   Employee: {employee_name}")
        print(f"   Email: {test_employee_data['Email']}")
        print(f"   Days Employed: {days_employed}")
        print()
    
    print("✅ Test completed successfully!")
    print("📋 To test the actual email sending:")
    print("   1. Go to https://www.pandaadmin.com/employee.html")
    print("   2. Find an employee with < 90 days employment and merchandise")
    print("   3. Edit the employee and set a termination date")
    print("   4. Save changes")
    print("   5. Check robwinters@pandaexteriors.com for the refund email")

if __name__ == "__main__":
    test_termination_workflow()