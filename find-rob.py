import boto3

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def find_rob():
    try:
        # Search for Rob Winters by name
        response = table.scan()
        employees = response['Items']
        
        for emp in employees:
            first_name = emp.get('First Name', '').lower()
            last_name = emp.get('Last Name', '').lower()
            
            if 'rob' in first_name and 'winter' in last_name:
                print(f"Found: {emp.get('First Name')} {emp.get('Last Name')}")
                print(f"Email: {emp.get('email', 'N/A')}")
                print(f"ID: {emp.get('id')}")
                print(f"Department: {emp.get('department', 'N/A')}")
                return emp['id']
        
        print("Rob Winters not found")
        return None
        
    except Exception as e:
        print(f"❌ Error finding Rob: {str(e)}")

if __name__ == "__main__":
    find_rob()