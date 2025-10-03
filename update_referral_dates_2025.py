import boto3
import json
from datetime import datetime, timedelta
import random

def update_referral_dates():
    dynamodb = boto3.resource('dynamodb')
    referrals_table = dynamodb.Table('panda-referrals')
    
    # Get all referrals
    response = referrals_table.scan()
    referrals = response['Items']
    
    print(f'Found {len(referrals)} referrals to update')
    
    # Define date ranges for May-September 2025
    date_ranges = [
        ('2025-05-01', '2025-05-31'),  # May 2025
        ('2025-06-01', '2025-06-30'),  # June 2025
        ('2025-07-01', '2025-07-31'),  # July 2025
        ('2025-08-01', '2025-08-31'),  # August 2025
        ('2025-09-01', '2025-09-30'),  # September 2025
    ]
    
    updated_count = 0
    
    for referral in referrals:
        # Skip if already has 2025 date
        if referral.get('created_at', '').startswith('2025'):
            continue
            
        # Pick random month from May-September 2025
        start_date, end_date = random.choice(date_ranges)
        
        # Generate random date within the month
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        random_date = start + timedelta(days=random.randint(0, (end - start).days))
        
        # Update the referral
        try:
            referrals_table.update_item(
                Key={'id': referral['id']},
                UpdateExpression='SET created_at = :date, updated_at = :date',
                ExpressionAttributeValues={
                    ':date': random_date.isoformat()
                }
            )
            updated_count += 1
            print(f'Updated referral {referral["name"]} to {random_date.strftime("%Y-%m-%d")}')
        except Exception as e:
            print(f'Error updating referral {referral["id"]}: {e}')
    
    print(f'Successfully updated {updated_count} referrals with 2025 dates')

if __name__ == '__main__':
    update_referral_dates()