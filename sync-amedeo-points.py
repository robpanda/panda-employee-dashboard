import boto3
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def update_amedeo_points():
    try:
        # Update Amedeo's points using id as key
        response = table.update_item(
            Key={'id': '10678'},
            UpdateExpression='SET points_lifetime = :lifetime, points_redeemed = :redeemed, points_balance = :balance, #pp = :pp, total_points_received = :received, total_points_redeemed = :redeemed_total, redeemed_points = :redeemed_old',
            ExpressionAttributeNames={
                '#pp': 'Panda Points'
            },
            ExpressionAttributeValues={
                ':lifetime': Decimal('100'),
                ':redeemed': Decimal('100'), 
                ':balance': Decimal('0'),
                ':pp': Decimal('0'),
                ':received': Decimal('100'),
                ':redeemed_total': Decimal('100'),
                ':redeemed_old': Decimal('100')
            },
            ReturnValues='UPDATED_NEW'
        )
        
        print("✅ Successfully updated Amedeo's points:")
        print(f"   Lifetime Total: 100")
        print(f"   Redeemed: 100") 
        print(f"   Current Balance: 0")
        
    except Exception as e:
        print(f"❌ Error updating points: {str(e)}")

if __name__ == "__main__":
    update_amedeo_points()