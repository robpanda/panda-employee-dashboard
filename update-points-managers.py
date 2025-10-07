#!/usr/bin/env python3

import boto3
import json
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
employees_table = dynamodb.Table('panda-employees')

def update_points_managers():
    """Update employees with leadership titles to be Points Managers"""
    
    # Leadership titles that qualify for Points Manager status
    leadership_titles = [
        'director', 'president', 'vice president', 'c-suite', 
        'ceo', 'cfo', 'coo', 'cto', 'vp', 'chief'
    ]
    
    try:
        # Scan all employees
        response = employees_table.scan()
        employees = response['Items']
        
        updated_count = 0
        
        for employee in employees:
            position = (employee.get('Position', '') or '').lower()
            current_points_manager = employee.get('points_manager', 'No')
            
            # Check if employee has leadership title
            is_leadership = any(title in position for title in leadership_titles)
            
            if is_leadership and current_points_manager != 'Yes':
                # Update employee to be Points Manager
                employee_id = employee.get('id', employee.get('employee_id'))
                first_name = employee.get('First Name', '')
                last_name = employee.get('Last Name', '')
                
                print(f"Updating {first_name} {last_name} ({position}) to Points Manager")
                
                # Update the employee record
                employee['points_manager'] = 'Yes'
                employee['points_budget'] = Decimal('500')  # Default quarterly budget
                
                # Save back to DynamoDB
                employees_table.put_item(Item=employee)
                updated_count += 1
        
        print(f"\nUpdated {updated_count} employees to Points Manager status")
        
        # List all Points Managers
        print("\nCurrent Points Managers:")
        for employee in employees:
            if employee.get('points_manager') == 'Yes':
                first_name = employee.get('First Name', '')
                last_name = employee.get('Last Name', '')
                position = employee.get('Position', 'Unknown Position')
                budget = employee.get('points_budget', 0)
                print(f"- {first_name} {last_name} ({position}) - Budget: {budget}")
                
    except Exception as e:
        print(f"Error updating Points Managers: {e}")

if __name__ == "__main__":
    update_points_managers()