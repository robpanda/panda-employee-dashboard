import boto3
from decimal import Decimal
import uuid

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def add_drjwoo_admin():
    try:
        # Generate unique ID
        employee_id = str(uuid.uuid4())[:8]
        
        # Add drjwoo88@gmail.com as points manager admin
        response = table.put_item(
            Item={
                'id': employee_id,
                'email': 'drjwoo88@gmail.com',
                'first_name': 'Dr.',
                'last_name': 'Woo',
                'title': 'Manager',
                'points_manager': 'Yes',
                'points_budget': Decimal('500'),
                'password': 'Panda2025!',
                'points_balance': Decimal('0'),
                'total_points_received': Decimal('0'),
                'total_points_redeemed': Decimal('0'),
                'Panda Points': Decimal('0')
            }
        )
        
        print(f"✅ Successfully added drjwoo88@gmail.com as points manager admin")
        print(f"   ID: {employee_id}")
        print(f"   Password: Panda2025!")
        print(f"   Points Budget: 500")
        
    except Exception as e:
        print(f"❌ Error adding admin: {str(e)}")

if __name__ == "__main__":
    add_drjwoo_admin()