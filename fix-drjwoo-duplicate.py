import boto3

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def fix_drjwoo_duplicate():
    try:
        # Delete the duplicate entry I created (ID: 20d0e2a5)
        print("Deleting duplicate entry...")
        table.delete_item(Key={'id': '20d0e2a5'})
        print("✅ Deleted duplicate entry with ID: 20d0e2a5")
        
        # Verify the existing Jason Wooten entry has correct settings
        response = table.get_item(Key={'id': '10022'})
        if 'Item' in response:
            employee = response['Item']
            print(f"✅ Found existing employee: {employee.get('First Name')} {employee.get('Last Name')}")
            print(f"   Email: {employee.get('Email')}")
            print(f"   Points Manager: {employee.get('points_manager')}")
            print(f"   Password: {employee.get('password')}")
            print(f"   Points Budget: {employee.get('points_budget')}")
        else:
            print("❌ Could not find existing employee with ID 10022")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    fix_drjwoo_duplicate()