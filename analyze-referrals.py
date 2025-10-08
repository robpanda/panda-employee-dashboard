import boto3
from collections import Counter

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-referrals')

def analyze_referrals():
    try:
        # Scan all referrals
        response = table.scan()
        items = response['Items']
        
        print(f"Total referrals in database: {len(items)}")
        
        # Check for duplicates by name
        names = [item.get('name', 'N/A') for item in items]
        name_counts = Counter(names)
        duplicates = {name: count for name, count in name_counts.items() if count > 1}
        
        if duplicates:
            print(f"\nDuplicate names found:")
            for name, count in duplicates.items():
                print(f"  {name}: {count} entries")
        
        # Check referrers
        referrers = [item.get('referred_by', 'N/A') for item in items]
        referrer_counts = Counter(referrers)
        
        print(f"\nTop 10 referrers:")
        for referrer, count in referrer_counts.most_common(10):
            print(f"  {referrer}: {count} referrals")
        
        # Check status distribution
        statuses = [item.get('status', 'N/A') for item in items]
        status_counts = Counter(statuses)
        
        print(f"\nStatus distribution:")
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
        
        # Show sample entries
        print(f"\nFirst 10 referrals:")
        for i, item in enumerate(items[:10]):
            print(f"{i+1}. {item.get('name', 'N/A')} - {item.get('status', 'N/A')} - By: {item.get('referred_by', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error analyzing referrals: {str(e)}")

if __name__ == "__main__":
    analyze_referrals()