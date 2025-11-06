#!/usr/bin/env python3
"""
Import GTR (Get The Referral) data into DynamoDB tables
"""

import requests
import boto3
import json
import time
from datetime import datetime
from decimal import Decimal

# Configuration
GTR_API_TOKEN = "67b5ee88-3768-4272-8ec0-adce1711e683"
GTR_BASE_URL = "https://restapi.getthereferral.com/v2"
REGION = "us-east-2"

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name=REGION)

# Tables
advocates_table = dynamodb.Table('panda-advocates')
sales_reps_table = dynamodb.Table('panda-sales-reps')
leads_table = dynamodb.Table('panda-referral-leads')
payouts_table = dynamodb.Table('panda-referral-payouts')

headers = {
    'Authorization': f'Bearer {GTR_API_TOKEN}'
}

def fetch_all_paginated(endpoint):
    """Fetch all pages from GTR API"""
    all_items = []
    page = 1
    per_page = 100

    while True:
        print(f"Fetching {endpoint} page {page}...")
        url = f"{GTR_BASE_URL}/{endpoint}?page={page}&per_page={per_page}"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            items = data.get(endpoint, [])
            if not items:
                break

            all_items.extend(items)

            # Check if there are more pages
            meta = data.get('meta', {})
            current_page = meta.get('current_page', page)
            last_page = meta.get('last_page', page)

            print(f"  Got {len(items)} items (page {current_page}/{last_page})")

            if current_page >= last_page:
                break

            page += 1
            time.sleep(0.5)  # Rate limiting

        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break

    return all_items

def generate_referral_code():
    """Generate a unique 6-character referral code"""
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

def import_advocates():
    """Import advocates from GTR"""
    print("\n=== Importing Advocates ===")
    advocates = fetch_all_paginated('advocates')

    print(f"\nImporting {len(advocates)} advocates...")

    # Track unique sales reps
    sales_reps = {}

    for adv in advocates:
        attrs = adv.get('attributes', {})

        # Track sales rep
        rep_id = str(attrs.get('sales_rep_id', 'unknown'))
        if rep_id and rep_id != 'unknown' and rep_id not in sales_reps:
            sales_reps[rep_id] = {
                'repId': rep_id,
                'gtrRepId': rep_id,
                'name': 'Sales Rep ' + rep_id,  # We'll update this manually
                'email': f'rep{rep_id}@pandaexteriors.com',
                'phone': '',
                'createdAt': int(time.time() * 1000),
                'updatedAt': int(time.time() * 1000),
                'active': True
            }

        # Import advocate
        advocate_id = str(attrs.get('advocate_id'))
        referral_code = attrs.get('mlm_code') or generate_referral_code()

        advocate_item = {
            'advocateId': advocate_id,
            'gtrAdvocateId': advocate_id,
            'repId': rep_id,
            'email': attrs.get('email', ''),
            'firstName': attrs.get('firstname', ''),
            'lastName': attrs.get('lastname', ''),
            'phone': attrs.get('phone') or '',
            'address': {
                'street1': attrs.get('street1') or '',
                'street2': attrs.get('street2') or '',
                'city': attrs.get('city') or '',
                'state': attrs.get('state') or '',
                'zip': attrs.get('zip') or ''
            },
            'referralCode': referral_code,
            'referralUrl': f"https://pandaadmin.com/refer/{referral_code}",
            'totalEarnings': Decimal('0'),
            'pendingEarnings': Decimal('0'),
            'paidEarnings': Decimal('0'),
            'totalLeads': 0,
            'totalConversions': 0,
            'createdAt': int(datetime.fromisoformat(attrs.get('added_on').replace('Z', '+00:00')).timestamp() * 1000) if attrs.get('added_on') else int(time.time() * 1000),
            'updatedAt': int(datetime.fromisoformat(attrs.get('updated_at').replace('Z', '+00:00')).timestamp() * 1000) if attrs.get('updated_at') else int(time.time() * 1000),
            'active': True,
            'emailVerified': bool(attrs.get('email_verified')),
            'lastLoggedIn': attrs.get('last_logged_in_at') or '',
            'source': 'GTR_IMPORT'
        }

        try:
            advocates_table.put_item(Item=advocate_item)
            print(f"  ✓ Imported advocate: {attrs.get('firstname')} {attrs.get('lastname')} ({advocate_id})")
        except Exception as e:
            print(f"  ✗ Error importing advocate {advocate_id}: {e}")

    # Import sales reps
    print(f"\nImporting {len(sales_reps)} sales reps...")
    for rep_id, rep_data in sales_reps.items():
        try:
            sales_reps_table.put_item(Item=rep_data)
            print(f"  ✓ Imported sales rep: {rep_id}")
        except Exception as e:
            print(f"  ✗ Error importing rep {rep_id}: {e}")

    return len(advocates), len(sales_reps)

def get_status_name(status_code):
    """Map GTR status codes to readable names"""
    status_map = {
        1: 'new',
        2: 'contacted',
        3: 'qualified',
        4: 'working',
        5: 'sold',
        6: 'lost'
    }
    return status_map.get(int(status_code), 'new')

def calculate_payout_amount(status):
    """Calculate payout based on lead status"""
    payout_tiers = {
        'new': Decimal('25.00'),  # Signup bonus
        'qualified': Decimal('50.00'),  # Good lead bonus
        'sold': Decimal('150.00')  # Deal closed bonus
    }
    return payout_tiers.get(status, Decimal('0'))

def import_leads():
    """Import leads from GTR"""
    print("\n=== Importing Leads ===")
    leads = fetch_all_paginated('leads')

    print(f"\nImporting {len(leads)} leads...")

    payout_count = 0

    for lead in leads:
        attrs = lead.get('attributes', {})

        lead_id = str(attrs.get('lead_id'))
        advocate_id = str(attrs.get('advocate_id'))
        rep_id = str(attrs.get('salesrep_id'))
        status_code = attrs.get('status', 1)
        status = get_status_name(status_code)

        # Import lead
        lead_item = {
            'leadId': lead_id,
            'gtrLeadId': lead_id,
            'advocateId': advocate_id,
            'repId': rep_id,
            'status': status,
            'email': attrs.get('email', ''),
            'firstName': attrs.get('firstname', ''),
            'lastName': attrs.get('lastname', ''),
            'phone': attrs.get('phone', ''),
            'address': {
                'street1': attrs.get('street1') or '',
                'street2': attrs.get('street2') or '',
                'city': attrs.get('city') or '',
                'state': attrs.get('state') or '',
                'zip': attrs.get('zip') or '',
                'country': attrs.get('country') or ''
            },
            'product': attrs.get('product', {}).get('name', 'Roofing Referral'),
            'createdAt': int(datetime.fromisoformat(attrs.get('added_on').replace('Z', '+00:00')).timestamp() * 1000) if attrs.get('added_on') else int(time.time() * 1000),
            'updatedAt': int(datetime.fromisoformat(attrs.get('updated_at').replace('Z', '+00:00')).timestamp() * 1000) if attrs.get('updated_at') else int(time.time() * 1000),
            'source': 'GTR_IMPORT',
            'notes': []
        }

        try:
            leads_table.put_item(Item=lead_item)
            print(f"  ✓ Imported lead: {attrs.get('firstname')} {attrs.get('lastname')} ({lead_id}) - {status}")

            # Create payout records for qualified leads
            if status in ['new', 'qualified', 'sold']:
                payout_amount = calculate_payout_amount(status)
                payout_status = 'paid' if status == 'sold' else 'pending'

                payout_id = f"{lead_id}_{status}"
                payout_item = {
                    'payoutId': payout_id,
                    'leadId': lead_id,
                    'advocateId': advocate_id,
                    'amount': payout_amount,
                    'type': status,
                    'status': payout_status,
                    'createdAt': lead_item['createdAt'],
                    'updatedAt': lead_item['updatedAt'],
                    'notes': f'GTR import - {status} status'
                }

                try:
                    payouts_table.put_item(Item=payout_item)
                    payout_count += 1
                except Exception as e:
                    print(f"    ✗ Error creating payout: {e}")

        except Exception as e:
            print(f"  ✗ Error importing lead {lead_id}: {e}")

    return len(leads), payout_count

def main():
    print("="*60)
    print("GTR Data Import Tool")
    print("="*60)

    # Import advocates and reps
    advocate_count, rep_count = import_advocates()

    # Import leads
    lead_count, payout_count = import_leads()

    # Summary
    print("\n" + "="*60)
    print("IMPORT COMPLETE")
    print("="*60)
    print(f"Sales Reps imported:  {rep_count}")
    print(f"Advocates imported:   {advocate_count}")
    print(f"Leads imported:       {lead_count}")
    print(f"Payouts created:      {payout_count}")
    print("="*60)

if __name__ == "__main__":
    main()
