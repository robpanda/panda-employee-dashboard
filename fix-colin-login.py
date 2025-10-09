import boto3
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def fix_colin_login():
    try:
        # Search for Colin Yost
        response = table.scan()
        employees = response['Items']
        
        colin = None
        for emp in employees:
            first_name = (emp.get('First Name', '') or emp.get('first_name', '')).strip().lower()
            last_name = (emp.get('Last Name', '') or emp.get('last_name', '')).strip().lower()
            email = (emp.get('Email', '') or emp.get('email', '')).strip().lower()
            
            if ('colin' in first_name and 'yost' in last_name) or email == 'colin.yoster@gmail.com':
                colin = emp
                break
        
        if not colin:
            print("❌ Colin Yost not found in database")
            return
        
        print(f"✅ Found Colin Yost:")
        print(f"   ID: {colin.get('id')}")
        print(f"   Name: {colin.get('First Name')} {colin.get('Last Name')}")
        print(f"   Email: {colin.get('Email')}")
        print(f"   Password: {colin.get('password', 'NOT SET')}")
        print(f"   Terminated: {colin.get('Terminated', 'No')}")
        
        # Fix any issues
        updates_needed = {}
        
        # Ensure email is correct
        if colin.get('Email') != 'colin.yoster@gmail.com':
            updates_needed['Email'] = 'colin.yoster@gmail.com'
            updates_needed['email'] = 'colin.yoster@gmail.com'
        
        # Ensure password is set
        if not colin.get('password'):
            updates_needed['password'] = 'Panda2025!'
        
        # Ensure not terminated
        if colin.get('Terminated') == 'Yes':
            updates_needed['Terminated'] = 'No'
        
        # Ensure has points field
        if 'points' not in colin:
            updates_needed['points'] = Decimal('0')
        if 'Panda Points' not in colin:
            updates_needed['Panda Points'] = Decimal('0')
        
        if updates_needed:
            print(f"\n🔧 Applying fixes:")
            for key, value in updates_needed.items():
                print(f"   {key}: {value}")
            
            # Build update expression
            update_expr = "SET "
            expr_values = {}
            expr_names = {}
            
            for i, (key, value) in enumerate(updates_needed.items()):
                if i > 0:
                    update_expr += ", "
                
                if key == 'Panda Points':
                    attr_name = f"#pp"
                    expr_names[attr_name] = key
                    update_expr += f"{attr_name} = :val{i}"
                else:
                    update_expr += f"{key} = :val{i}"
                
                expr_values[f":val{i}"] = value
            
            # Update the record
            update_params = {
                'Key': {'id': colin['id']},
                'UpdateExpression': update_expr,
                'ExpressionAttributeValues': expr_values
            }
            
            if expr_names:
                update_params['ExpressionAttributeNames'] = expr_names
            
            table.update_item(**update_params)
            
            print("✅ Colin's account has been fixed!")
        else:
            print("✅ Colin's account looks good - no fixes needed")
        
        # Test login credentials
        print(f"\n🔐 Login credentials:")
        print(f"   Email: colin.yoster@gmail.com")
        print(f"   Password: Panda2025!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    fix_colin_login()