import boto3
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def fix_all_manager_budgets():
    try:
        # Get all managers
        response = table.scan(
            FilterExpression='points_manager = :pm',
            ExpressionAttributeValues={':pm': 'Yes'}
        )
        
        managers = response['Items']
        updated_count = 0
        
        for manager in managers:
            if 'quarterly_budget' not in manager or manager.get('quarterly_budget') != 500:
                # Update quarterly budget to 500
                table.update_item(
                    Key={'id': manager['id']},
                    UpdateExpression='SET quarterly_budget = :budget',
                    ExpressionAttributeValues={
                        ':budget': Decimal('500')
                    }
                )
                
                name = f"{manager.get('First Name', '')} {manager.get('Last Name', '')}"
                print(f"Updated {name}: 500 points quarterly budget")
                updated_count += 1
        
        print(f"\n✅ Updated {updated_count} managers with 500 points quarterly budget")
        print(f"Total managers: {len(managers)}")
        
    except Exception as e:
        print(f"❌ Error fixing manager budgets: {str(e)}")

if __name__ == "__main__":
    fix_all_manager_budgets()