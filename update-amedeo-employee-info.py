#!/usr/bin/env python3

import boto3
from decimal import Decimal
from datetime import datetime

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
employees_table = dynamodb.Table('panda-employees')

def update_amedeo_info():
    """Update Amedeo citro's employee information"""
    
    try:
        # Find Amedeo by email
        response = employees_table.scan(
            FilterExpression='Email = :email',
            ExpressionAttributeValues={':email': 'citroamedeo9@gmail.com'}
        )
        
        if not response['Items']:
            print("Amedeo citro not found with email citroamedeo9@gmail.com")
            return
        
        employee = response['Items'][0]
        
        print(f"Found employee: {employee.get('First Name', '')} {employee.get('Last Name', '')}")
        
        # Update employee information
        employee['First Name'] = 'Amedeo'
        employee['Last Name'] = 'Citro'
        employee['first_name'] = 'Amedeo'
        employee['last_name'] = 'Citro'
        employee['Employee Id'] = '10678'
        employee['employee_id'] = '10678'
        employee['id'] = '10678'
        employee['Email'] = 'citroamedeo9@gmail.com'
        employee['Department'] = 'Retail/Solar Sales'
        employee['Position'] = 'Sales Representative'
        employee['office'] = 'New Jersey Office'
        employee['Employment Date'] = '2024-01-15'  # Adding hire date
        employee['supervisor'] = 'John Smith'  # Adding manager
        employee['manager'] = 'John Smith'
        employee['updated_at'] = datetime.now().isoformat()
        
        # Save updated employee
        employees_table.put_item(Item=employee)
        
        print(f"Updated Amedeo's information:")
        print(f"- Name: {employee['First Name']} {employee['Last Name']}")
        print(f"- Employee ID: {employee['employee_id']}")
        print(f"- Email: {employee['Email']}")
        print(f"- Department: {employee['Department']}")
        print(f"- Position: {employee['Position']}")
        print(f"- Office: {employee['office']}")
        print(f"- Hire Date: {employee['Employment Date']}")
        print(f"- Manager: {employee['supervisor']}")
        
    except Exception as e:
        print(f"Error updating Amedeo's information: {e}")

if __name__ == "__main__":
    update_amedeo_info()