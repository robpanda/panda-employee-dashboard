#!/usr/bin/env python3
import csv
import boto3
from boto3.dynamodb.conditions import Attr

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
referrals_table = dynamodb.Table('panda-referrals')

def update_referral_notes():
    """Update referral notes from CSV data"""
    updated_count = 0
    not_found_count = 0
    
    # Load notes mapping from CSV
    notes_mapping = {}
    with open('update_notes_from_data.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            notes_mapping[row['referral_name'].strip()] = row['notes'].strip()
    
    try:
        # Scan all referrals with historical import notes
        response = referrals_table.scan(
            FilterExpression=Attr('notes').contains('Historical data import')
        )
        
        referrals = response.get('Items', [])
        
        for referral in referrals:
            referral_name = referral.get('name', '').strip()
            
            if referral_name in notes_mapping:
                new_notes = notes_mapping[referral_name]
                
                # Update the referral with new notes
                referrals_table.update_item(
                    Key={'id': referral['id']},
                    UpdateExpression='SET notes = :notes',
                    ExpressionAttributeValues={':notes': new_notes}
                )
                
                updated_count += 1
                print(f"Updated notes for: {referral_name}")
                
                if updated_count % 10 == 0:
                    print(f"Updated {updated_count} referrals...")
            else:
                not_found_count += 1
                print(f"No notes found for: {referral_name}")
        
        print(f"\nUpdate complete!")
        print(f"Successfully updated: {updated_count} referrals")
        print(f"Not found in mapping: {not_found_count} referrals")
        
    except Exception as e:
        print(f"Error updating referral notes: {e}")

if __name__ == "__main__":
    print("Starting referral notes update...")
    update_referral_notes()