import boto3
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
points_history_table = dynamodb.Table('panda-points-history')
employees_table = dynamodb.Table('panda-employees')

def clear_nand_points_history():
    try:
        # Find all points history records for Nand Patel
        response = points_history_table.scan(
            FilterExpression='contains(employee_name, :name)',
            ExpressionAttributeValues={':name': 'Nand Patel'}
        )
        
        deleted_count = 0
        for item in response['Items']:
            points_history_table.delete_item(
                Key={'id': item['id']}
            )
            deleted_count += 1
            print(f"Deleted record: {item['date']} - {item['points']} pts - {item['reason']}")
        
        # Reset Jason Wooten's remaining points to 500
        employees_table.update_item(
            Key={'id': '10024'},  # Jason Wooten's ID
            UpdateExpression='SET points_remaining = :remaining',
            ExpressionAttributeValues={':remaining': Decimal('500')}
        )
        
        print(f"✅ Cleared {deleted_count} points history records for Nand Patel")
        print("✅ Restored Jason Wooten's remaining points to 500")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    clear_nand_points_history()