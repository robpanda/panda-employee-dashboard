import boto3

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-referrals')

def check_referrals():
    try:
        # Scan all referrals
        response = table.scan()
        items = response['Items']
        
        print(f"Total referrals in database: {len(items)}")
        
        if items:
            print("\nFirst 5 referrals:")
            for i, item in enumerate(items[:5]):
                print(f"{i+1}. {item.get('name', 'N/A')} - {item.get('status', 'N/A')} - Referred by: {item.get('referred_by', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error checking referrals: {str(e)}")

if __name__ == "__main__":
    check_referrals()