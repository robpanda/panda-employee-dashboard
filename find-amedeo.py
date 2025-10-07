import boto3

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def find_amedeo():
    try:
        response = table.scan()
        items = response['Items']
        
        print(f"Searching through {len(items)} records...")
        
        for item in items:
            # Check all fields for Amedeo
            for key, value in item.items():
                if isinstance(value, str) and 'amedeo' in value.lower():
                    print(f"Found Amedeo reference:")
                    print(f"  Field: {key}")
                    print(f"  Value: {value}")
                    print(f"  Full record:")
                    for k, v in item.items():
                        print(f"    {k}: {v}")
                    print("---")
                    return
                    
        print("No Amedeo record found")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    find_amedeo()