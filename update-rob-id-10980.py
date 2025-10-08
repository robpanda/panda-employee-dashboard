import boto3
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def update_rob_department():
    try:
        # Update Rob Winters by ID
        table.update_item(
            Key={'id': '10980'},
            UpdateExpression='SET department = :dept, points_manager = :manager, quarterly_budget = :budget',
            ExpressionAttributeValues={
                ':dept': 'Digital Marketing',
                ':manager': 'Yes',
                ':budget': Decimal('500')
            }
        )
        
        print(f"✅ Updated Rob Winters (ID: 10980):")
        print(f"   Department: Digital Marketing")
        print(f"   Points Manager: Yes")
        print(f"   Quarterly Budget: 500 points")
        
    except Exception as e:
        print(f"❌ Error updating Rob's department: {str(e)}")

if __name__ == "__main__":
    update_rob_department()