#!/usr/bin/env python3

import boto3
import json
from datetime import datetime, timedelta

# Test the termination email functionality
def test_termination_email():
    # Create a test employee with recent hire date and merchandise
    test_employee = {
        'id': 'test-123',
        'First Name': 'Test',
        'Last Name': 'Employee',
        'Email': 'test@example.com',
        'Employment Date': (datetime.now() - timedelta(days=45)).strftime('%Y-%m-%d'),  # 45 days ago
        'Merch Requested': 'Winter Jacket, Company T-Shirt',
        'merchandise_value': 90.00
    }
    
    termination_date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"Test Employee: {test_employee['First Name']} {test_employee['Last Name']}")
    print(f"Hire Date: {test_employee['Employment Date']}")
    print(f"Termination Date: {termination_date}")
    print(f"Days Employed: {(datetime.now() - datetime.strptime(test_employee['Employment Date'], '%Y-%m-%d')).days}")
    print(f"Merchandise Value: ${test_employee['merchandise_value']}")
    print(f"Should trigger email: {'Yes' if (datetime.now() - datetime.strptime(test_employee['Employment Date'], '%Y-%m-%d')).days <= 90 else 'No'}")

if __name__ == "__main__":
    test_termination_email()