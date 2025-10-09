import boto3
import json
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def debug_colin_record():
    try:
        # Search for Colin by email exactly as the login would
        response = table.scan()
        employees = response['Items']
        
        print(f"🔍 Searching through {len(employees)} employees...")
        
        target_email = 'colin.yoster@gmail.com'
        matches = []
        
        for emp in employees:
            email = (emp.get('Email', '') or emp.get('email', '')).strip().lower()
            if email == target_email.lower():
                matches.append(emp)
        
        print(f"\n📧 Email matches for '{target_email}':")
        print(f"Found {len(matches)} matches")
        
        if matches:
            colin = matches[0]
            print(f"\n📋 Colin's complete record:")
            
            # Convert Decimal to string for display
            def convert_decimals(obj):
                if isinstance(obj, Decimal):
                    return str(obj)
                elif isinstance(obj, dict):
                    return {k: convert_decimals(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_decimals(v) for v in obj]
                return obj
            
            clean_record = convert_decimals(colin)
            print(json.dumps(clean_record, indent=2, default=str))
            
            # Check specific fields that might cause issues
            print(f"\n🔧 Key fields check:")
            print(f"   ID: {colin.get('id')} (type: {type(colin.get('id'))})")
            print(f"   Email: '{colin.get('Email')}' (type: {type(colin.get('Email'))})")
            print(f"   Password: '{colin.get('password')}' (type: {type(colin.get('password'))})")
            print(f"   Terminated: '{colin.get('Terminated')}' (type: {type(colin.get('Terminated'))})")
            print(f"   First Name: '{colin.get('First Name')}' (type: {type(colin.get('First Name'))})")
            print(f"   Last Name: '{colin.get('Last Name')}' (type: {type(colin.get('Last Name'))})")
            
            # Check for any None values that might cause issues
            none_fields = []
            for key, value in colin.items():
                if value is None:
                    none_fields.append(key)
            
            if none_fields:
                print(f"\n⚠️  Fields with None values: {none_fields}")
            else:
                print(f"\n✅ No None values found")
                
        else:
            print(f"❌ No employee found with email: {target_email}")
            
            # Search for similar emails
            print(f"\n🔍 Searching for similar emails...")
            similar = []
            for emp in employees:
                email = (emp.get('Email', '') or emp.get('email', '')).strip().lower()
                if 'colin' in email or 'yost' in email:
                    similar.append((email, emp.get('First Name', ''), emp.get('Last Name', '')))
            
            if similar:
                print(f"Found similar emails:")
                for email, first, last in similar:
                    print(f"   {email} - {first} {last}")
            else:
                print(f"No similar emails found")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_colin_record()