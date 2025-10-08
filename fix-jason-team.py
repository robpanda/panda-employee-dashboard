import boto3
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def fix_jason_team():
    """Fix supervisor assignments for Jason Wooten's team"""
    try:
        # Employee IDs that should be under Jason Wooten
        team_members = ['10946', '10024', '10848']  # Antoine, Jason San Martin-Torres, Nand
        
        for emp_id in team_members:
            # Update supervisor to "Jason Wooten"
            response = table.update_item(
                Key={'id': emp_id},
                UpdateExpression='SET supervisor = :supervisor',
                ExpressionAttributeValues={
                    ':supervisor': 'Jason Wooten'
                },
                ReturnValues='UPDATED_NEW'
            )
            
            print(f"✅ Updated employee {emp_id} supervisor to Jason Wooten")
            
        print(f"\n✅ Successfully updated {len(team_members)} employees to report to Jason Wooten")
        
    except Exception as e:
        print(f"❌ Error updating team assignments: {str(e)}")

if __name__ == "__main__":
    fix_jason_team()