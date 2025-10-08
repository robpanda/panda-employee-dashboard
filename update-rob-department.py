import boto3
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def update_rob_department():
    try:
        # Find Rob Winters by email
        response = table.scan(
            FilterExpression='email = :email',
            ExpressionAttributeValues={':email': 'rb.winters@me.com'}
        )
        
        if response['Items']:
            employee = response['Items'][0]
            
            # Update department and add manager privileges
            table.update_item(
                Key={'id': employee['id']},
                UpdateExpression='SET department = :dept, points_manager = :manager, quarterly_budget = :budget',
                ExpressionAttributeValues={
                    ':dept': 'Digital Marketing',
                    ':manager': 'Yes',
                    ':budget': Decimal('500')
                }
            )
            
            print(f"✅ Updated Rob Winters (rb.winters@me.com):")
            print(f"   Department: Digital Marketing")
            print(f"   Points Manager: Yes")
            print(f"   Quarterly Budget: 500 points")
        else:
            print("❌ Employee with email rb.winters@me.com not found")
        
    except Exception as e:
        print(f"❌ Error updating Rob's department: {str(e)}")

if __name__ == "__main__":
    update_rob_department()