import boto3

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
referrals_table = dynamodb.Table('panda-referrals')
employees_table = dynamodb.Table('panda-employees')

def check_jake_referrals():
    # First find Jake's employee ID
    response = employees_table.scan(
        FilterExpression='contains(#email, :email)',
        ExpressionAttributeNames={'#email': 'Email'},
        ExpressionAttributeValues={':email': 'jaaacob228@gmail.com'}
    )
    
    if not response['Items']:
        print("Jake not found in employee database")
        return
    
    jake = response['Items'][0]
    jake_id = jake.get('id', jake.get('employee_id'))
    jake_name = jake.get('Name', f"{jake.get('First Name', '')} {jake.get('Last Name', '')}").strip()
    
    print(f"Found Jake: {jake_name} (ID: {jake_id})")
    
    # Find referrals by Jake
    response = referrals_table.scan(
        FilterExpression='referred_by_id = :emp_id OR referred_by_name = :emp_name',
        ExpressionAttributeValues={
            ':emp_id': jake_id,
            ':emp_name': jake_name
        }
    )
    
    referrals = response['Items']
    print(f"Found {len(referrals)} referrals for Jake")
    
    # Group by month
    monthly_counts = {}
    for referral in referrals:
        created_at = referral.get('created_at', '')
        if created_at:
            month = created_at[:7]  # YYYY-MM format
            if month not in monthly_counts:
                monthly_counts[month] = 0
            monthly_counts[month] += 1
            print(f"Referral: {referral.get('name', 'Unknown')} - Date: {created_at} - Month: {month}")
    
    print("\nMonthly breakdown:")
    for month, count in sorted(monthly_counts.items()):
        print(f"{month}: {count} referrals")

if __name__ == "__main__":
    check_jake_referrals()