import boto3
import uuid
from datetime import datetime

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')

# Create admin users table
def create_admin_users_table():
    try:
        table = dynamodb.create_table(
            TableName='panda-admin-users',
            KeySchema=[
                {
                    'AttributeName': 'email',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'email',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Wait for table to be created
        table.wait_until_exists()
        print("Admin users table created successfully")
        
        # Add initial admin users
        add_initial_admins()
        
    except Exception as e:
        if 'ResourceInUseException' in str(e):
            print("Table already exists, adding initial admins")
            add_initial_admins()
        else:
            print(f"Error creating table: {e}")

def add_initial_admins():
    table = dynamodb.Table('panda-admin-users')
    
    admins = [
        {
            'email': 'camiaran358@gmail.com',
            'name': 'Camila Arango',
            'password': 'Panda2025!',
            'role': 'referrals_admin',
            'permissions': ['referrals'],
            'active': True,
            'created_at': datetime.now().isoformat()
        },
        {
            'email': 'nick.gessler@gmail.com',
            'name': 'Nicholas Gessler',
            'password': 'Panda2025!',
            'role': 'referrals_admin',
            'permissions': ['referrals'],
            'active': True,
            'created_at': datetime.now().isoformat()
        }
    ]
    
    for admin in admins:
        try:
            table.put_item(Item=admin)
            print(f"Added admin: {admin['name']} ({admin['email']})")
        except Exception as e:
            print(f"Error adding admin {admin['email']}: {e}")

if __name__ == "__main__":
    create_admin_users_table()