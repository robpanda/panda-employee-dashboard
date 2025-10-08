import boto3

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def check_manager_budgets():
    try:
        # Scan for employees with points_manager = Yes
        response = table.scan(
            FilterExpression='points_manager = :pm',
            ExpressionAttributeValues={':pm': 'Yes'}
        )
        
        managers = response['Items']
        print(f"Found {len(managers)} managers with points_manager = Yes:")
        
        for manager in managers:
            name = f"{manager.get('First Name', '')} {manager.get('Last Name', '')}"
            dept = manager.get('Department', 'N/A')
            budget = manager.get('quarterly_budget', 'Not set')
            print(f"  {name} - {dept} - Budget: {budget}")
        
        # Also check Rob Winters specifically
        rob_response = table.scan(
            FilterExpression='id = :id',
            ExpressionAttributeValues={':id': '10980'}
        )
        
        if rob_response['Items']:
            rob = rob_response['Items'][0]
            print(f"\nRob Winters (ID: 10980):")
            print(f"  Department: {rob.get('Department', 'N/A')}")
            print(f"  Points Manager: {rob.get('points_manager', 'N/A')}")
            print(f"  Quarterly Budget: {rob.get('quarterly_budget', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error checking manager budgets: {str(e)}")

if __name__ == "__main__":
    check_manager_budgets()