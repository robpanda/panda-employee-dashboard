import boto3
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
points_history_table = dynamodb.Table('panda-points-history')
employees_table = dynamodb.Table('panda-employees')

def fix_jason_points_history():
    """Fix points history records to properly attribute to Jason Wooten"""
    try:
        # Get Jason Wooten's employee ID
        response = employees_table.scan(
            FilterExpression='contains(#name, :name)',
            ExpressionAttributeNames={'#name': 'first_name'},
            ExpressionAttributeValues={':name': 'Jason'}
        )
        
        jason_id = None
        for emp in response['Items']:
            full_name = f"{emp.get('first_name', '')} {emp.get('last_name', '')}".strip()
            if 'Jason' in full_name and 'Wooten' in full_name:
                jason_id = emp.get('id')
                print(f"Found Jason Wooten with ID: {jason_id}")
                break
        
        if not jason_id:
            print("❌ Jason Wooten not found")
            return
            
        # Get all points history records
        response = points_history_table.scan()
        history_records = response['Items']
        
        # Find records that should be attributed to Jason Wooten
        jason_records = []
        for record in history_records:
            awarded_by_name = record.get('awarded_by_name', '')
            if 'Jason Wooten' in awarded_by_name:
                jason_records.append(record)
                
        print(f"Found {len(jason_records)} records attributed to Jason Wooten")
        
        # Update records to have correct awarded_by field
        for record in jason_records:
            if record.get('awarded_by') != jason_id:
                points_history_table.update_item(
                    Key={'id': record['id']},
                    UpdateExpression='SET awarded_by = :awarded_by',
                    ExpressionAttributeValues={
                        ':awarded_by': jason_id
                    }
                )
                print(f"✅ Updated record {record['id']} - {record.get('employee_name')} - {record.get('points')} pts")
        
        print(f"\n✅ Successfully updated Jason Wooten's points history records")
        
    except Exception as e:
        print(f"❌ Error fixing points history: {str(e)}")

if __name__ == "__main__":
    fix_jason_points_history()