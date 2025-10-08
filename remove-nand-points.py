import boto3
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def remove_nand_points():
    try:
        # First, get current data for Nand Patel
        response = table.scan(
            FilterExpression='contains(#name, :name)',
            ExpressionAttributeNames={'#name': 'first_name'},
            ExpressionAttributeValues={':name': 'Nand'}
        )
        
        if not response['Items']:
            print("❌ Nand Patel not found")
            return
            
        employee = response['Items'][0]
        employee_id = employee['id']
        current_balance = employee.get('points_balance', 0)
        current_lifetime = employee.get('points_lifetime', 0)
        
        print(f"Found Nand Patel (ID: {employee_id})")
        print(f"Current balance: {current_balance}")
        print(f"Current lifetime: {current_lifetime}")
        
        # Remove 200 points
        new_balance = max(0, int(current_balance) - 200)
        new_lifetime = max(0, int(current_lifetime) - 200)
        
        # Update the employee record
        table.update_item(
            Key={'id': employee_id},
            UpdateExpression='SET points_balance = :balance, points_lifetime = :lifetime',
            ExpressionAttributeValues={
                ':balance': Decimal(str(new_balance)),
                ':lifetime': Decimal(str(new_lifetime))
            }
        )
        
        print(f"✅ Successfully removed 200 points from Nand Patel")
        print(f"   New balance: {new_balance}")
        print(f"   New lifetime: {new_lifetime}")
        
    except Exception as e:
        print(f"❌ Error removing points: {str(e)}")

if __name__ == "__main__":
    remove_nand_points()