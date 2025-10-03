import boto3

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def fix_missing_names():
    # Scan all employees
    response = table.scan()
    items = response['Items']
    
    updated_count = 0
    
    for item in items:
        # Check if Name is missing or None
        if not item.get('Name') or item.get('Name') is None:
            first_name = item.get('First Name', '')
            last_name = item.get('Last Name', '')
            
            if first_name or last_name:
                full_name = f"{first_name} {last_name}".strip()
                
                # Update the item with the constructed name
                table.update_item(
                    Key={'id': item['id']},
                    UpdateExpression='SET #name = :name',
                    ExpressionAttributeNames={'#name': 'Name'},
                    ExpressionAttributeValues={':name': full_name}
                )
                
                updated_count += 1
                print(f"Updated {item.get('Email', 'Unknown')}: {full_name}")
    
    print(f"Total employees updated: {updated_count}")

if __name__ == "__main__":
    fix_missing_names()