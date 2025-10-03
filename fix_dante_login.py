#!/usr/bin/env python3
import boto3

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
employees_table = dynamodb.Table('panda-employees')

def fix_dante_login():
    """Fix Dante's login by removing duplicate and ensuring correct record"""
    
    try:
        # Delete the duplicate record with empty name
        employees_table.delete_item(Key={'id': '4c3bd40d-9caf-4f3c-8409-a0e88a963532'})
        print("Deleted duplicate record")
        
        # Update the correct record
        employees_table.update_item(
            Key={'id': '10730'},
            UpdateExpression='SET #fn = :fn, password = :pwd',
            ExpressionAttributeNames={'#fn': 'First Name'},
            ExpressionAttributeValues={
                ':fn': 'Dante',
                ':pwd': 'Panda2025!'
            }
        )
        print("Updated Dante's record with correct name and password")
        
    except Exception as e:
        print(f"Error fixing Dante's login: {e}")

if __name__ == "__main__":
    print("Fixing Dante's login...")
    fix_dante_login()