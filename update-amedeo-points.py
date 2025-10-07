#!/usr/bin/env python3

import boto3
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
employees_table = dynamodb.Table('panda-employees')

def update_amedeo_points():
    print("Updating Amedeo citro's points...")
    
    try:
        # Find Amedeo by name
        response = employees_table.scan()
        employees = response['Items']
        
        for emp in employees:
            first_name = emp.get('First Name', '') or emp.get('first_name', '')
            last_name = emp.get('Last Name', '') or emp.get('last_name', '')
            full_name = f"{first_name} {last_name}".strip().lower()
            
            if 'amedeo' in full_name and 'citro' in full_name:
                print(f"Found Amedeo: {first_name} {last_name}")
                
                # Update his points
                employees_table.put_item(Item={
                    **emp,
                    'points': Decimal('0'),  # Available points = 0
                    'Panda Points': Decimal('0'),  # Available points = 0
                    'redeemed_points': Decimal('100'),  # Redeemed points = 100
                    'total_points_earned': Decimal('100'),  # Total earned = 100
                    'updated_at': '2025-01-15T12:00:00Z'
                })
                
                print("✅ Updated Amedeo citro:")
                print("   Available points: 0")
                print("   Redeemed points: 100")
                print("   Total earned: 100")
                return
        
        print("❌ Amedeo citro not found")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    update_amedeo_points()