import boto3
import csv
import uuid
from datetime import datetime

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-referrals')

def restore_referrals():
    try:
        # Read the corrected historical referrals CSV
        with open('corrected_historical_referrals.csv', 'r') as file:
            reader = csv.DictReader(file)
            
            count = 0
            for row in reader:
                # Create referral entry
                referral_data = {
                    'id': str(uuid.uuid4()),
                    'name': row['referral_name'],
                    'department': row['department'],
                    'status': row['status'].title(),  # Capitalize first letter
                    'phone_screen': 'Complete' if row['phone_screen_complete'] == 'true' else 'Pending',
                    'date_referred': row['created_at'],
                    'referred_by': row['referred_by_name'],
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                # Insert into DynamoDB
                table.put_item(Item=referral_data)
                count += 1
                
                if count % 10 == 0:
                    print(f"Restored {count} referrals...")
            
            print(f"\n✅ Successfully restored {count} referrals from historical data")
            
    except Exception as e:
        print(f"❌ Error restoring referrals: {str(e)}")

if __name__ == "__main__":
    restore_referrals()