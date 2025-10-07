#!/usr/bin/env python3

import boto3
from decimal import Decimal
from datetime import datetime

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
employees_table = dynamodb.Table('panda-employees')

def update_amedeo_points():
    """Update Amedeo citro's points to show 100 total received and 100 redeemed"""
    
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
        emp_id = employee.get('id', employee.get('employee_id'))
        
        print(f"Found Amedeo citro: {employee.get('First Name', '')} {employee.get('Last Name', '')}")
        
        # Update employee record with new point structure
        employee['points'] = Decimal('0')  # Available points (after redemption)
        employee['Panda Points'] = Decimal('0')  # Available points
        employee['total_points_received'] = Decimal('100')  # Total ever received
        employee['total_points_redeemed'] = Decimal('100')  # Total ever redeemed
        employee['updated_at'] = datetime.now().isoformat()
        
        # Save updated employee
        employees_table.put_item(Item=employee)
        
        print(f"Updated Amedeo's points:")
        print(f"- Available Points: 0")
        print(f"- Total Received: 100")
        print(f"- Total Redeemed: 100")
        
    except Exception as e:
        print(f"Error updating Amedeo's points: {e}")

if __name__ == "__main__":
    update_amedeo_points()