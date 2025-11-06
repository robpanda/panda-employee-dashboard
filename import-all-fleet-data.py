#!/usr/bin/env python3
"""
Import ALL Fleet Data from Excel to DynamoDB
Handles all sheets with proper error handling
"""

import sys
sys.path.insert(0, '/tmp/fleet_venv/lib/python3.13/site-packages')

import pandas as pd
import boto3
from datetime import datetime
from decimal import Decimal
import re

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')

vehicles_table = dynamodb.Table('panda-fleet-vehicles')
accidents_table = dynamodb.Table('panda-fleet-accidents')
ezpass_table = dynamodb.Table('panda-fleet-ezpass')
sales_table = dynamodb.Table('panda-fleet-sales')

def clean_value(value):
    """Clean NaN and None values"""
    if pd.isna(value) or value == '' or str(value) == 'nan':
        return ''
    return str(value).strip()

def safe_decimal(value, default=0):
    """Safely convert to Decimal"""
    try:
        if pd.isna(value) or value == '' or str(value) == 'nan':
            return Decimal(str(default))
        return Decimal(str(float(value)))
    except:
        return Decimal(str(default))

def safe_int(value, default=0):
    """Safely convert to int"""
    try:
        if pd.isna(value) or value == '' or str(value) == 'nan':
            return default
        return int(float(value))
    except:
        return default

def parse_date(date_val):
    """Parse date to ISO format"""
    if pd.isna(date_val) or date_val == '' or str(date_val) == 'nan':
        return ''
    try:
        if isinstance(date_val, pd.Timestamp):
            return date_val.isoformat()
        return pd.to_datetime(date_val).isoformat()
    except:
        return ''

def import_assigned_vehicles(excel_file):
    """Import assigned vehicles - main fleet"""
    print("🚗 Importing Assigned Vehicles...")

    # Read with header on row 6 (0-indexed row 6)
    df = pd.read_excel(excel_file, sheet_name='Assigned', header=6)

    count = 0
    errors = 0

    for idx, row in df.iterrows():
        try:
            # Skip if no asset ID
            asset_id = clean_value(row.get('Asset ID', ''))
            if not asset_id or asset_id.lower() in ['asset id', 'nan', '']:
                continue

            # Extract data with fallbacks
            vehicle = {
                'vehicle_id': asset_id,
                'asset_name': asset_id,
                'year': clean_value(row.get('Year', '')),
                'make': clean_value(row.get('Make', '')),
                'model': clean_value(row.get('Model', '')),
                'vin': clean_value(row.get('VIN', '')),
                'license_plate': clean_value(row.get('License Plate#', '')),
                'status': 'assigned',
                'department': clean_value(row.get('Department', '')),
                'current_driver': clean_value(row.get('Current driver', '')),
                'driver_email': clean_value(row.get('Driver Email', '')) or 'fleet@pandaexteriors.com',
                'driver_phone': clean_value(row.get('Driver Phone Number', '')),
                'driver_manager': clean_value(row.get('Driver Manager', '')),
                'territory': clean_value(row.get('Territory', '')),
                'location': clean_value(row.get('Location', '')),
                'panda_phone': clean_value(row.get('Panda Phone Number', '')),
                'ez_pass_id': clean_value(row.get('EZ Pass', '')),
                'registration_expiration': '',
                'insurance_expiration': '',
                'emissions_due': '',
                'mileage': safe_int(row.get('Mileage', 0)),
                'unit_value': safe_decimal(row.get('Unit Value', 0)),
                'comments': clean_value(row.get('comments', '')),
                'gaf_presenter': False,
                'camera_installed': False,
                'vanity_ordered': False,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }

            vehicles_table.put_item(Item=vehicle)
            count += 1
            print(f"  ✓ {asset_id}")

        except Exception as e:
            errors += 1
            print(f"  ✗ Error on row {idx}: {str(e)}")
            continue

    print(f"✅ Imported {count} assigned vehicles ({errors} errors)\n")
    return count

def import_floaters_downed(excel_file):
    """Import floater and downed vehicles"""
    print("🔄 Importing Floaters & Downed Vehicles...")

    df = pd.read_excel(excel_file, sheet_name='FloatersDowned', header=1)

    count = 0
    errors = 0

    for idx, row in df.iterrows():
        try:
            vehicle_name = clean_value(row.get('Vehicle Name', ''))
            if not vehicle_name or vehicle_name.lower() in ['vehicle name', 'floaters', 'downed', 'nan', '']:
                continue

            # Determine status from location or comments
            location = clean_value(row.get('Location', '')).lower()
            comments = clean_value(row.get('Comments', '')).lower()

            if 'downed' in location or 'downed' in comments or 'repair' in comments:
                status = 'downed'
            else:
                status = 'floater'

            vehicle = {
                'vehicle_id': vehicle_name,
                'asset_name': vehicle_name,
                'year': clean_value(row.get('Year', '')),
                'make': clean_value(row.get('Make', '')),
                'model': clean_value(row.get('Model', '')),
                'vin': clean_value(row.get('VIN', '')),
                'license_plate': clean_value(row.get('License Plate#', '')),
                'status': status,
                'department': clean_value(row.get('Department', '')),
                'current_driver': clean_value(row.get('Current driver', '')),
                'driver_email': 'fleet@pandaexteriors.com',
                'driver_phone': '',
                'driver_manager': '',
                'territory': '',
                'location': clean_value(row.get('Location', '')),
                'panda_phone': clean_value(row.get('Panda Phone Number', '')),
                'ez_pass_id': '',
                'registration_expiration': '',
                'insurance_expiration': '',
                'emissions_due': '',
                'mileage': 0,
                'unit_value': Decimal('0'),
                'comments': clean_value(row.get('Comments', '')),
                'gaf_presenter': False,
                'camera_installed': False,
                'vanity_ordered': False,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }

            vehicles_table.put_item(Item=vehicle)
            count += 1
            print(f"  ✓ {vehicle_name} ({status})")

        except Exception as e:
            errors += 1
            print(f"  ✗ Error on row {idx}: {str(e)}")
            continue

    print(f"✅ Imported {count} floaters/downed vehicles ({errors} errors)\n")
    return count

def import_sold_vehicles(excel_file):
    """Import sold vehicles"""
    print("💰 Importing Sold Vehicles...")

    df = pd.read_excel(excel_file, sheet_name='Sold', header=0)

    count = 0
    errors = 0

    for idx, row in df.iterrows():
        try:
            vehicle_name = clean_value(row.get('Vehicle Name', ''))
            if not vehicle_name or vehicle_name.lower() in ['vehicle name', 'nan', '']:
                continue

            # Create sale record
            sale_id = f"SALE-{vehicle_name.replace(' ', '-')}-{datetime.now().strftime('%Y%m%d')}"

            sale = {
                'sale_id': sale_id,
                'vehicle_id': vehicle_name,
                'asset_name': vehicle_name,
                'year': clean_value(row.get('Year', '')),
                'make': clean_value(row.get('Make', '')),
                'model': clean_value(row.get('Model', '')),
                'vin': clean_value(row.get('VIN', '')),
                'license_plate': clean_value(row.get('License Plate#', '')),
                'buyer': clean_value(row.get('Current driver', '')),
                'sale_type': 'sold',
                'sale_date': datetime.now().isoformat(),
                'sale_price': safe_decimal(row.get('Sale Price', 0)),
                'insurance_canceled': False,
                'plate_swapped': False,
                'sold_to': '',
                'comments': clean_value(row.get('comments', '')),
                'created_at': datetime.now().isoformat()
            }

            sales_table.put_item(Item=sale)

            # Also add to vehicles table as sold
            vehicle = {
                'vehicle_id': vehicle_name,
                'asset_name': vehicle_name,
                'year': clean_value(row.get('Year', '')),
                'make': clean_value(row.get('Make', '')),
                'model': clean_value(row.get('Model', '')),
                'vin': clean_value(row.get('VIN', '')),
                'license_plate': clean_value(row.get('License Plate#', '')),
                'status': 'sold',
                'department': '',
                'current_driver': clean_value(row.get('Current driver', '')),
                'driver_email': 'fleet@pandaexteriors.com',
                'driver_phone': '',
                'driver_manager': '',
                'territory': '',
                'location': '',
                'panda_phone': clean_value(row.get('Panda Phone Number', '')),
                'ez_pass_id': '',
                'registration_expiration': '',
                'insurance_expiration': '',
                'emissions_due': '',
                'mileage': 0,
                'unit_value': Decimal('0'),
                'comments': clean_value(row.get('comments', '')),
                'gaf_presenter': False,
                'camera_installed': False,
                'vanity_ordered': False,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }

            vehicles_table.put_item(Item=vehicle)
            count += 1
            print(f"  ✓ {vehicle_name}")

        except Exception as e:
            errors += 1
            print(f"  ✗ Error on row {idx}: {str(e)}")
            continue

    print(f"✅ Imported {count} sold vehicles ({errors} errors)\n")
    return count

def import_ezpass(excel_file):
    """Import EZ Pass data"""
    print("🎫 Importing EZ Pass Records...")

    # Use header row 0 - correct header row for EZ Pass sheet
    df = pd.read_excel(excel_file, sheet_name='EZ Pass', header=0)

    count = 0
    errors = 0

    for idx, row in df.iterrows():
        try:
            # Note: Column name 'EZ Pass ' has a trailing space in the Excel file
            ezpass_id = clean_value(row.get('EZ Pass ', '') or row.get('EZ Pass', ''))
            if not ezpass_id or ezpass_id.lower() in ['ez pass', 'nan', '']:
                continue

            # Use correct column names from the sheet
            vehicle_id = clean_value(row.get('Asset ID', ''))
            # Fallback for empty vehicle_id to avoid GSI validation error
            if not vehicle_id:
                vehicle_id = 'UNASSIGNED'

            ezpass = {
                'ezpass_id': ezpass_id,
                'vehicle_id': vehicle_id,
                'asset_name': vehicle_id if vehicle_id != 'UNASSIGNED' else '',
                'driver': clean_value(row.get('Driver', '')),
                'driver_email': '',
                'plate_number': clean_value(row.get('Plate Number', '')),
                'status': 'canceled' if clean_value(row.get('Canceled', '')) else 'active',
                'in_bag_id': clean_value(row.get('In The Bag', '')),
                'canceled_id': clean_value(row.get('Canceled', '')),
                'territory': '',  # No territory column in this sheet
                'assigned_driver': '',  # No assigned column in this sheet
                'notes': '',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }

            ezpass_table.put_item(Item=ezpass)
            count += 1
            print(f"  ✓ {ezpass_id}")

        except Exception as e:
            errors += 1
            print(f"  ✗ Error on row {idx}: {str(e)}")
            continue

    print(f"✅ Imported {count} EZ Pass records ({errors} errors)\n")
    return count

def main():
    excel_file = '/Users/robwinters/Downloads/Fleet Dept Vehicle Sheet.xlsx'

    print("🚗 Starting Complete Fleet Data Import")
    print("=" * 60)
    print()

    total_vehicles = 0
    total_sales = 0
    total_ezpass = 0

    try:
        # Import all vehicles
        total_vehicles += import_assigned_vehicles(excel_file)
        total_vehicles += import_floaters_downed(excel_file)

        # Import sales
        total_sales = import_sold_vehicles(excel_file)

        # Import EZ Pass
        total_ezpass = import_ezpass(excel_file)

        print()
        print("=" * 60)
        print("✅ IMPORT COMPLETE!")
        print()
        print(f"📊 Summary:")
        print(f"   - Vehicles: {total_vehicles}")
        print(f"   - Sales: {total_sales}")
        print(f"   - EZ Pass: {total_ezpass}")
        print(f"   - Total Records: {total_vehicles + total_sales + total_ezpass}")
        print()
        print("🎉 All data imported to DynamoDB!")
        print()
        print("🌐 View at: https://pandaadmin.com/assets-vehicles.html")

    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())
