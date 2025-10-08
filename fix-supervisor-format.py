#!/usr/bin/env python3
import boto3

def fix_supervisor_format():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    table = dynamodb.Table('panda-employees')
    
    # The employees that need to be updated
    employee_ids = ['10848', '10024', '10946']
    
    # Update supervisor from "Wooten, Jason" to "Jason Wooten"
    correct_supervisor = "Jason Wooten"
    
    print(f"🔧 Updating supervisor format to: {correct_supervisor}")
    
    for emp_id in employee_ids:
        try:
            response = table.update_item(
                Key={'id': emp_id},
                UpdateExpression='SET supervisor = :supervisor',
                ExpressionAttributeValues={':supervisor': correct_supervisor},
                ReturnValues='UPDATED_NEW'
            )
            
            # Get employee name for confirmation
            emp_response = table.get_item(Key={'id': emp_id})
            if 'Item' in emp_response:
                employee = emp_response['Item']
                first_name = employee.get('First Name', employee.get('first_name', 'Unknown'))
                last_name = employee.get('Last Name', employee.get('last_name', 'Unknown'))
                name = f"{first_name} {last_name}"
                print(f"✅ Updated {name} (ID: {emp_id}) supervisor to: {correct_supervisor}")
            else:
                print(f"✅ Updated employee ID: {emp_id} supervisor to: {correct_supervisor}")
                
        except Exception as e:
            print(f"❌ Error updating employee {emp_id}: {str(e)}")

if __name__ == "__main__":
    fix_supervisor_format()
    print("\n🎉 Supervisor format updates complete!")
    print("These employees should now appear under Jason Wooten's team in the points management system.")