#!/usr/bin/env python3
"""
Import complete GTR data from CSV exports
- Advocates: 1,849 records
- Sales Reps: 103 records
- Sales Managers: 8 records
"""

import boto3
import csv
import time
from datetime import datetime
import re
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')

# DynamoDB tables
advocates_table = dynamodb.Table('panda-advocates')
reps_table = dynamodb.Table('panda-sales-reps')
managers_table = dynamodb.Table('panda-sales-managers')

def parse_date(date_str):
    """Parse date from MM/DD/YYYY format"""
    if not date_str or date_str.strip() == '':
        return None
    try:
        dt = datetime.strptime(date_str.strip(), '%m/%d/%Y')
        return int(dt.timestamp() * 1000)  # milliseconds
    except:
        return None

def parse_money(money_str):
    """Parse money string like '$225.00' to Decimal"""
    if not money_str or money_str.strip() == '':
        return Decimal('0.00')
    try:
        return Decimal(money_str.replace('$', '').replace(',', '').strip())
    except:
        return Decimal('0.00')

def generate_referral_code(name, user_id):
    """Generate a referral code from name"""
    if not name:
        return f"REF{user_id}"
    # Take first letters of name
    parts = name.split()
    code = ''.join([p[0].upper() for p in parts if p])[:3]
    return f"{code}{user_id[-4:]}"

def import_sales_managers(csv_path):
    """Import sales managers from CSV"""
    print("\n=== IMPORTING SALES MANAGERS ===")

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0

        for row in reader:
            name = row.get('Name', '').strip()
            if not name:
                continue

            # Generate manager ID from name
            manager_id = f"MGR{count + 1:03d}"

            item = {
                'managerId': manager_id,
                'name': name,
                'email': row.get('Email', '').strip(),
                'phone': row.get('Phone Number', '').strip(),
                'active': row.get('Status', '').strip().lower() == 'active',
                'createdAt': parse_date(row.get('Registered On', '')) or int(time.time() * 1000),
                'updatedAt': int(time.time() * 1000),
                'repsCount': int(row.get('Number of Salesrep', 0) or 0),
                'source': 'GTR_CSV_IMPORT'
            }

            try:
                managers_table.put_item(Item=item)
                count += 1
                print(f"  ✓ {name} ({manager_id})")
            except Exception as e:
                print(f"  ✗ Error importing {name}: {e}")

    print(f"\n✅ Imported {count} sales managers")
    return count

def import_sales_reps(csv_path):
    """Import sales reps from CSV"""
    print("\n=== IMPORTING SALES REPS ===")

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0

        for row in reader:
            name = row.get('Name', '').strip()
            if not name:
                continue

            # Generate rep ID from name
            rep_id = f"REP{count + 1:04d}"

            item = {
                'repId': rep_id,
                'name': name,
                'email': row.get('Email', '').strip(),
                'phone': row.get('Phone Number', '').strip(),
                'managerName': row.get('Sales Manager', '').strip(),
                'active': row.get('Status', '').strip().lower() == 'active',
                'createdAt': parse_date(row.get('Registered On', '')) or int(time.time() * 1000),
                'updatedAt': int(time.time() * 1000),
                'advocatesCount': int(row.get('Total Advocates', 0) or 0),
                'totalReferrals': int(row.get('Total Referrals', 0) or 0),
                'soldReferrals': int(row.get('Sold Referrals', 0) or 0),
                'source': 'GTR_CSV_IMPORT'
            }

            try:
                reps_table.put_item(Item=item)
                count += 1
                if count % 10 == 0:
                    print(f"  Imported {count} reps...")
            except Exception as e:
                print(f"  ✗ Error importing {name}: {e}")

    print(f"\n✅ Imported {count} sales reps")
    return count

def import_advocates(csv_path):
    """Import advocates from CSV"""
    print("\n=== IMPORTING ADVOCATES ===")

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0

        for row in reader:
            user_id = row.get('User ID', '').strip()
            name = row.get('Name', '').strip()

            if not user_id or not name:
                continue

            # Parse name
            name_parts = name.split(maxsplit=1)
            first_name = name_parts[0] if len(name_parts) > 0 else ''
            last_name = name_parts[1] if len(name_parts) > 1 else ''

            # Generate referral code
            referral_code = generate_referral_code(name, user_id)

            # Parse address
            address = {
                'street1': row.get('Street1', '').strip(),
                'street2': row.get('Street2', '').strip(),
                'city': row.get('City', '').strip(),
                'state': row.get('State', '').strip(),
                'zip': row.get('Zip', '').strip()
            }

            # Parse earnings
            total_paid = parse_money(row.get('Total Paid', '$0.00'))

            item = {
                'advocateId': user_id,
                'gtrAdvocateId': user_id,
                'firstName': first_name,
                'lastName': last_name,
                'email': row.get('Email ID', '').strip(),
                'phone': row.get('Phone', '').strip(),
                'referralCode': referral_code,
                'referralUrl': f'https://pandaadmin.com/refer/{referral_code}',
                'address': address,
                'active': row.get('Status', '').strip().lower() == 'active',
                'createdAt': parse_date(row.get('Registered On', '')) or int(time.time() * 1000),
                'updatedAt': int(time.time() * 1000),
                'totalReferrals': int(row.get('Total Referrals Submitted', 0) or 0),
                'totalEarnings': total_paid,
                'paidEarnings': total_paid,
                'pendingEarnings': Decimal('0.00'),
                'notes': row.get('Note', '').strip(),
                'repName': row.get('Associated Sales Reps', '').strip(),
                'source': 'GTR_CSV_IMPORT'
            }

            try:
                advocates_table.put_item(Item=item)
                count += 1
                if count % 50 == 0:
                    print(f"  Imported {count} advocates...")
            except Exception as e:
                print(f"  ✗ Error importing {name}: {e}")

    print(f"\n✅ Imported {count} advocates")
    return count

def main():
    print("=" * 60)
    print("GTR COMPLETE DATA IMPORT")
    print("=" * 60)

    # Import in order: managers -> reps -> advocates
    managers_count = import_sales_managers('/Users/robwinters/Downloads/exportData (5).csv')
    reps_count = import_sales_reps('/Users/robwinters/Downloads/exportData (4).csv')
    advocates_count = import_advocates('/Users/robwinters/Downloads/exportData (3).csv')

    print("\n" + "=" * 60)
    print("IMPORT COMPLETE")
    print("=" * 60)
    print(f"Sales Managers: {managers_count}")
    print(f"Sales Reps: {reps_count}")
    print(f"Advocates: {advocates_count}")
    print(f"Total Records: {managers_count + reps_count + advocates_count}")
    print("=" * 60)

if __name__ == '__main__':
    main()
