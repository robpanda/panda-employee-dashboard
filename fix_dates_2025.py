import boto3
import json

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-referrals')

def fix_dates():
    # Scan all items
    response = table.scan()
    items = response['Items']
    
    # Continue scanning if there are more items
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response['Items'])
    
    updated_count = 0
    
    for item in items:
        updated = False
        
        # Check and update date field
        if 'date' in item and '2024' in item['date']:
            item['date'] = item['date'].replace('2024', '2025')
            updated = True
        
        # Check and update created_at field
        if 'created_at' in item and '2024' in item['created_at']:
            item['created_at'] = item['created_at'].replace('2024', '2025')
            updated = True
        
        # Check and update any other date fields
        if 'submitted_date' in item and '2024' in item['submitted_date']:
            item['submitted_date'] = item['submitted_date'].replace('2024', '2025')
            updated = True
            
        if updated:
            # Update the item in DynamoDB
            table.put_item(Item=item)
            updated_count += 1
            print(f"Updated referral ID: {item.get('id', 'Unknown')} - {item.get('candidate_name', 'Unknown')}")
    
    print(f"Total referrals updated: {updated_count}")

if __name__ == "__main__":
    fix_dates()