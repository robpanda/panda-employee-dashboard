import boto3
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

# Corrected names for missing employees
missing_employees = [
    {"name": "Mike Stuart", "points": 200, "redeemed": 0},  # was "Michael Stuart"
    {"name": "Christopher Ayala Lovo", "points": 50, "redeemed": 0},  # was "Chris Ayala"
    {"name": "Jonathan Gonzalez Velasquez", "points": 50, "redeemed": 0}  # was "Jonathan Gonzalez"
    # Note: "Rob Test" might be "Rob Winters" but that's likely the admin, skipping
]

def find_employee_by_name(name):
    """Find employee by matching first and last name"""
    try:
        response = table.scan()
        items = response['Items']
        
        name_lower = name.lower()
        
        for item in items:
            # Try different name field combinations
            full_name = None
            
            if 'First Name' in item and 'Last Name' in item:
                full_name = f"{item['First Name']} {item['Last Name']}".lower()
            elif 'first_name' in item and 'last_name' in item:
                full_name = f"{item['first_name']} {item['last_name']}".lower()
            elif 'name' in item:
                full_name = item['name'].lower()
                
            if full_name and full_name == name_lower:
                return item
                
        return None
    except Exception as e:
        print(f"Error finding employee {name}: {str(e)}")
        return None

def update_employee_points(employee_id, points, redeemed):
    """Update employee points"""
    try:
        balance = points - redeemed
        
        response = table.update_item(
            Key={'id': employee_id},
            UpdateExpression='SET points_lifetime = :lifetime, points_redeemed = :redeemed, points_balance = :balance, #pp = :pp, total_points_received = :received, total_points_redeemed = :redeemed_total, redeemed_points = :redeemed_old',
            ExpressionAttributeNames={
                '#pp': 'Panda Points'
            },
            ExpressionAttributeValues={
                ':lifetime': Decimal(str(points)),
                ':redeemed': Decimal(str(redeemed)), 
                ':balance': Decimal(str(balance)),
                ':pp': Decimal(str(balance)),
                ':received': Decimal(str(points)),
                ':redeemed_total': Decimal(str(redeemed)),
                ':redeemed_old': Decimal(str(redeemed))
            },
            ReturnValues='UPDATED_NEW'
        )
        return True
    except Exception as e:
        print(f"Error updating points: {str(e)}")
        return False

def update_missing_employees():
    """Update points for the missing employees with corrected names"""
    print("Updating missing employees with corrected names...")
    
    for data in missing_employees:
        name = data["name"]
        points = data["points"]
        redeemed = data["redeemed"]
        
        print(f"\nProcessing {name}...")
        
        # Find employee
        employee = find_employee_by_name(name)
        
        if employee:
            employee_id = employee.get('id')
            if employee_id:
                if update_employee_points(employee_id, points, redeemed):
                    balance = points - redeemed
                    print(f"✅ Updated {name}: {points} total, {redeemed} redeemed, {balance} balance")
                else:
                    print(f"❌ Failed to update {name}")
            else:
                print(f"❌ No ID found for {name}")
        else:
            print(f"❌ Employee not found: {name}")

if __name__ == "__main__":
    update_missing_employees()