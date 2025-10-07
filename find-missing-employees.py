import boto3

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

missing_names = ["Michael Stuart", "Rob Test", "Chris Ayala", "Jonathan Gonzalez"]

def find_similar_names():
    try:
        response = table.scan()
        items = response['Items']
        
        print("Looking for similar names...")
        
        for missing in missing_names:
            print(f"\nSearching for '{missing}':")
            missing_parts = missing.lower().split()
            
            matches = []
            for item in items:
                # Check different name combinations
                names_to_check = []
                
                if 'First Name' in item and 'Last Name' in item:
                    names_to_check.append(f"{item['First Name']} {item['Last Name']}")
                if 'first_name' in item and 'last_name' in item:
                    names_to_check.append(f"{item['first_name']} {item['last_name']}")
                if 'name' in item:
                    names_to_check.append(item['name'])
                
                for name in names_to_check:
                    if name:
                        name_lower = name.lower()
                        # Check if any part of the missing name is in this name
                        for part in missing_parts:
                            if part in name_lower:
                                matches.append(name)
                                break
            
            # Remove duplicates and show matches
            unique_matches = list(set(matches))
            if unique_matches:
                print(f"  Possible matches: {unique_matches}")
            else:
                print(f"  No matches found")
                
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    find_similar_names()