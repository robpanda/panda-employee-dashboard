#!/usr/bin/env python3
import boto3
from decimal import Decimal

def check_manager_assignments():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    table = dynamodb.Table('panda-employees')
    
    # Employee IDs to check
    employee_ids = ['10848', '10024', '10946']
    
    print("🔍 Checking manager assignments for specified employees...")
    
    for emp_id in employee_ids:
        try:
            response = table.get_item(Key={'id': emp_id})
            
            if 'Item' in response:
                employee = response['Item']
                first_name = employee.get('First Name', employee.get('first_name', 'Unknown'))
                last_name = employee.get('Last Name', employee.get('last_name', 'Unknown'))
                name = f"{first_name} {last_name}"
                supervisor = employee.get('supervisor', employee.get('manager', 'No supervisor assigned'))
                department = employee.get('Department', employee.get('department', 'Unknown'))
                
                print(f"\n📋 Employee ID: {emp_id}")
                print(f"   Name: {name}")
                print(f"   Department: {department}")
                print(f"   Current Supervisor: {supervisor}")
                
            else:
                print(f"\n❌ Employee ID {emp_id} not found in database")
                
        except Exception as e:
            print(f"❌ Error checking employee {emp_id}: {str(e)}")

def update_manager_assignment(emp_id, manager_name):
    """Update an employee's manager assignment"""
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    table = dynamodb.Table('panda-employees')
    
    try:
        response = table.update_item(
            Key={'id': emp_id},
            UpdateExpression='SET supervisor = :supervisor',
            ExpressionAttributeValues={':supervisor': manager_name},
            ReturnValues='UPDATED_NEW'
        )
        print(f"✅ Updated employee {emp_id} supervisor to: {manager_name}")
        return True
    except Exception as e:
        print(f"❌ Error updating employee {emp_id}: {str(e)}")
        return False

def list_all_managers():
    """List all employees who could be managers"""
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    table = dynamodb.Table('panda-employees')
    
    try:
        response = table.scan()
        employees = response['Items']
        
        # Find potential managers (those with supervisor status or management titles)
        managers = []
        for emp in employees:
            is_supervisor = emp.get('is_supervisor', 'No')
            points_manager = emp.get('points_manager', 'No')
            position = emp.get('Position', emp.get('position', '')).lower()
            
            if (is_supervisor == 'Yes' or points_manager == 'Yes' or 
                'manager' in position or 'director' in position or 
                'supervisor' in position or 'lead' in position):
                
                first_name = emp.get('First Name', emp.get('first_name', ''))
                last_name = emp.get('Last Name', emp.get('last_name', ''))
                name = f"{first_name} {last_name}".strip()
                department = emp.get('Department', emp.get('department', 'Unknown'))
                
                managers.append({
                    'id': emp.get('id', ''),
                    'name': name,
                    'department': department,
                    'position': emp.get('Position', emp.get('position', ''))
                })
        
        print(f"\n👥 Found {len(managers)} potential managers:")
        for mgr in sorted(managers, key=lambda x: x['name']):
            print(f"   {mgr['name']} - {mgr['department']} ({mgr['position']})")
            
        return managers
        
    except Exception as e:
        print(f"❌ Error listing managers: {str(e)}")
        return []

if __name__ == "__main__":
    print("🚀 Manager Assignment Checker")
    print("=" * 50)
    
    # Check current assignments
    check_manager_assignments()
    
    # List available managers
    list_all_managers()
    
    print("\n" + "=" * 50)
    print("To update manager assignments, use:")
    print("update_manager_assignment('employee_id', 'Manager Full Name')")