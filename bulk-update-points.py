import boto3
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

# Points data
points_data = [
    {"name": "Michael Stuart", "points": 200, "redeemed": 0},
    {"name": "Jimmy Coggin", "points": 200, "redeemed": 0},
    {"name": "Kevin Flores", "points": 100, "redeemed": 0},
    {"name": "Amedeo citro", "points": 100, "redeemed": 100},
    {"name": "Brad Repka", "points": 100, "redeemed": 0},
    {"name": "Ryan Dunlap", "points": 100, "redeemed": 0},
    {"name": "Marc Robinson", "points": 50, "redeemed": 0},
    {"name": "Samuel Smith", "points": 50, "redeemed": 0},
    {"name": "Bryon Holmes", "points": 50, "redeemed": 0},
    {"name": "Rob Test", "points": 50, "redeemed": 0},
    {"name": "Chris Ayala", "points": 50, "redeemed": 0},
    {"name": "Jonathan Gonzalez", "points": 50, "redeemed": 0},
    {"name": "Idris sesay", "points": 50, "redeemed": 0},
    {"name": "Dalton Dawson", "points": 50, "redeemed": 0},
    {"name": "Austin Boyle", "points": 50, "redeemed": 0}
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

def bulk_update_points():
    """Update points for all employees in the list"""
    print("Starting bulk points update...")
    
    updated_count = 0
    not_found_count = 0
    
    for data in points_data:
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
                    updated_count += 1
                else:
                    print(f"❌ Failed to update {name}")
            else:
                print(f"❌ No ID found for {name}")
        else:
            print(f"❌ Employee not found: {name}")
            not_found_count += 1
    
    print(f"\n📊 Summary:")
    print(f"   Updated: {updated_count}")
    print(f"   Not found: {not_found_count}")
    print(f"   Total processed: {len(points_data)}")

if __name__ == "__main__":
    bulk_update_points()