import boto3
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-referrals')

def clean_referrals():
    try:
        # Scan all referrals
        response = table.scan()
        items = response['Items']
        
        print(f"Found {len(items)} total referrals")
        
        # Find all Joshua Bell and Test Person entries
        joshua_entries = []
        test_entries = []
        other_entries = []
        
        for item in items:
            name = item.get('name', '').strip()
            if name == 'Joshua Bell':
                joshua_entries.append(item)
            elif name == 'Test Person':
                test_entries.append(item)
            else:
                other_entries.append(item)
        
        print(f"Joshua Bell entries: {len(joshua_entries)}")
        print(f"Test Person entries: {len(test_entries)}")
        print(f"Other entries: {len(other_entries)}")
        
        # Keep only the first Joshua Bell entry, delete the rest
        if joshua_entries:
            keep_entry = joshua_entries[0]
            print(f"\nKeeping Joshua Bell entry: {keep_entry.get('department', 'N/A')}")
            
            # Delete duplicate Joshua Bell entries
            for i, entry in enumerate(joshua_entries[1:], 1):
                table.delete_item(Key={'id': entry['id']})
                print(f"Deleted Joshua Bell duplicate {i}")
        
        # Delete all Test Person entries
        for i, entry in enumerate(test_entries, 1):
            table.delete_item(Key={'id': entry['id']})
            print(f"Deleted Test Person entry {i}")
        
        print(f"\n✅ Cleanup complete!")
        print(f"   Kept: 1 Joshua Bell entry")
        print(f"   Deleted: {len(joshua_entries) - 1} Joshua Bell duplicates")
        print(f"   Deleted: {len(test_entries)} Test Person entries")
        
    except Exception as e:
        print(f"❌ Error cleaning referrals: {str(e)}")

if __name__ == "__main__":
    clean_referrals()