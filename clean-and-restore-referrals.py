import boto3
import uuid
from datetime import datetime

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-referrals')

def clean_and_restore():
    try:
        # First, delete ALL existing referrals
        print("Clearing existing referrals...")
        response = table.scan()
        items = response['Items']
        
        for item in items:
            table.delete_item(Key={'id': item['id']})
        
        print(f"Deleted {len(items)} existing referrals")
        
        # Now restore only the legitimate data from corrected_historical_referrals.csv
        print("Restoring legitimate referrals...")
        
        import csv
        with open('corrected_historical_referrals.csv', 'r') as file:
            reader = csv.DictReader(file)
            
            count = 0
            for row in reader:
                # Create referral entry with proper structure
                referral_data = {
                    'id': str(uuid.uuid4()),
                    'name': row['referral_name'],
                    'department': row['department'],
                    'status': row['status'].lower().replace(' ', '-'),  # Normalize status
                    'phone_screen': 'Complete' if row['phone_screen_complete'] == 'true' else 'Pending',
                    'phone_screen_complete': row['phone_screen_complete'] == 'true',
                    'date_referred': row['created_at'],
                    'referred_by': row['referred_by_name'],
                    'referred_by_name': row['referred_by_name'],
                    'created_at': row['created_at'],
                    'updated_at': datetime.now().isoformat()
                }
                
                # Insert into DynamoDB
                table.put_item(Item=referral_data)
                count += 1
                
                if count % 25 == 0:
                    print(f"Restored {count} referrals...")
            
            print(f"\n✅ Successfully restored {count} legitimate referrals")
            print("Database now contains only the original referral data")
            
    except Exception as e:
        print(f"❌ Error cleaning and restoring referrals: {str(e)}")

if __name__ == "__main__":
    clean_and_restore()