#!/usr/bin/env python3
import boto3

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
employees_table = dynamodb.Table('panda-employees')

def set_all_passwords():
    """Set all employee passwords to Panda2025!"""
    updated_count = 0
    
    try:
        response = employees_table.scan()
        employees = response.get('Items', [])
        
        for employee in employees:
            employee_id = employee.get('id', employee.get('employee_id', ''))
            if employee_id:
                employees_table.update_item(
                    Key={'id': employee_id},
                    UpdateExpression='SET password = :pwd',
                    ExpressionAttributeValues={':pwd': 'Panda2025!'}
                )
                updated_count += 1
                
                if updated_count % 10 == 0:
                    print(f"Updated {updated_count} employee passwords...")
        
        print(f"\nPassword update complete!")
        print(f"Successfully updated: {updated_count} employees")
        
    except Exception as e:
        print(f"Error updating passwords: {e}")

if __name__ == "__main__":
    print("Setting all employee passwords to 'Panda2025!'...")
    set_all_passwords()