#!/usr/bin/env python3
"""
Import Fleet Data from Excel to DynamoDB
Reads the Fleet Dept Vehicle Sheet.xlsx and imports data into the DynamoDB tables
"""

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
maintenance_table = dynamodb.Table('panda-fleet-maintenance')

def clean_value(value):
    """Clean NaN and None values"""
    if pd.isna(value) or value == '' or value == 'NaN':
        return ''
    return str(value).strip()

def parse_date(date_str):
    """Parse date string to ISO format"""
    if pd.isna(date_str) or date_str == '' or date_str == 'NaN':
        return ''
    try:
        if isinstance(date_str, pd.Timestamp):
            return date_str.isoformat()
        return pd.to_datetime(date_str).isoformat()
    except:
        return ''

def import_vehicles(excel_file):
    """Import vehicles from Assigned sheet"""
    print("📦 Importing vehicles from Assigned sheet...")

    df = pd.read_excel(excel_file, sheet_name='Assigned')

    # Skip header rows and get actual data (starts at row 5)
    df = df.iloc[5:]
    df.columns = ['number', 'department', 'asset_id', 'current_driver', 'driver_phone',
                  'year', 'make', 'model', 'license_plate', 'vin', 'phone_on_vehicle',
                  'comments'] + list(df.columns[12:])

    count = 0
    for _, row in df.iterrows():
        asset_id = clean_value(row['asset_id'])

        if not asset_id or asset_id == 'nan':
            continue

        # Determine status
        status = 'assigned'
        if 'floater' in clean_value(row['current_driver']).lower():
            status = 'floater'

        vehicle = {
            'vehicle_id': asset_id,
            'asset_name': asset_id,
            'year': clean_value(row['year']),
            'make': clean_value(row['make']),
            'model': clean_value(row['model']),
            'vin': clean_value(row['vin']),
            'license_plate': clean_value(row['license_plate']),
            'status': status,
            'department': clean_value(row['department']),
            'current_driver': clean_value(row['current_driver']),
            'driver_phone': clean_value(row['driver_phone']),
            'panda_phone': clean_value(row['phone_on_vehicle']),
            'comments': clean_value(row['comments']),
            'territory': '',
            'location': '',
            'driver_email': '',
            'driver_manager': '',
            'ez_pass_id': '',
            'registration_expiration': '',
            'insurance_expiration': '',
            'emissions_due': '',
            'mileage': 0,
            'unit_value': Decimal('0'),
            'gaf_presenter': False,
            'camera_installed': False,
            'vanity_ordered': False,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        try:
            vehicles_table.put_item(Item=vehicle)
            count += 1
            print(f"  ✓ Imported {asset_id}")
        except Exception as e:
            print(f"  ✗ Error importing {asset_id}: {str(e)}")

    print(f"✅ Imported {count} vehicles\n")

def import_floaters(excel_file):
    """Import floater vehicles"""
    print("🔄 Importing floater vehicles...")

    df = pd.read_excel(excel_file, sheet_name='FloatersDowned')

    # Skip header row
    df = df.iloc[1:]

    count = 0
    for _, row in df.iterrows():
        vehicle_name = clean_value(row.iloc[2])  # Vehicle Name

        if not vehicle_name or vehicle_name == 'nan' or vehicle_name == 'FLOATERS':
            continue

        vehicle = {
            'vehicle_id': vehicle_name,
            'asset_name': vehicle_name,
            'year': clean_value(row.iloc[5]),
            'make': clean_value(row.iloc[6]),
            'model': clean_value(row.iloc[7]),
            'vin': clean_value(row.iloc[9]),
            'license_plate': clean_value(row.iloc[8]),
            'status': 'floater',
            'department': clean_value(row.iloc[1]),
            'current_driver': clean_value(row.iloc[3]),
            'location': clean_value(row.iloc[4]),
            'panda_phone': clean_value(row.iloc[10]),
            'comments': clean_value(row.iloc[11]),
            'territory': '',
            'driver_email': '',
            'driver_phone': '',
            'driver_manager': '',
            'ez_pass_id': '',
            'registration_expiration': '',
            'insurance_expiration': '',
            'emissions_due': '',
            'mileage': 0,
            'unit_value': Decimal('0'),
            'gaf_presenter': False,
            'camera_installed': False,
            'vanity_ordered': False,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        try:
            vehicles_table.put_item(Item=vehicle)
            count += 1
            print(f"  ✓ Imported floater {vehicle_name}")
        except Exception as e:
            print(f"  ✗ Error importing {vehicle_name}: {str(e)}")

    print(f"✅ Imported {count} floater vehicles\n")

def import_accidents(excel_file):
    """Import accident records"""
    print("🚨 Importing accidents...")

    df = pd.read_excel(excel_file, sheet_name='Accidents')

    # Skip header rows
    df = df.iloc[4:]

    count = 0
    for _, row in df.iterrows():
        asset_id = clean_value(row.iloc[1])  # Assert ID

        if not asset_id or asset_id == 'nan' or asset_id == 'Assert ID':
            continue

        accident_date = parse_date(row.iloc[0])
        if not accident_date:
            accident_date = datetime.now().isoformat()

        accident = {
            'accident_id': f"ACC-{asset_id}-{accident_date[:10]}",
            'accident_date': accident_date,
            'vehicle_id': asset_id,
            'asset_name': asset_id,
            'driver': clean_value(row.iloc[2]),
            'driver_manager': clean_value(row.iloc[3]),
            'docs_received': clean_value(row.iloc[4]).lower() == 'yes',
            'video': clean_value(row.iloc[5]).lower() == 'yes',
            'driver_statement': clean_value(row.iloc[6]).lower() == 'yes',
            'police_report': clean_value(row.iloc[7]).lower() == 'yes',
            'video_description': clean_value(row.iloc[8]),
            'claim_number': clean_value(row.iloc[9]),
            'insurance_provider': clean_value(row.iloc[10]),
            'panda_at_fault': clean_value(row.iloc[11]).lower() == 'yes',
            'driver_estimate': Decimal(str(row.iloc[12])) if pd.notna(row.iloc[12]) else Decimal('0'),
            'panda_repair_estimate': Decimal(str(row.iloc[13])) if pd.notna(row.iloc[13]) else Decimal('0'),
            'actual_repair_cost': Decimal(str(row.iloc[16])) if pd.notna(row.iloc[16]) else Decimal('0'),
            'liability_cost': Decimal(str(row.iloc[14])) if pd.notna(row.iloc[14]) else Decimal('0'),
            'insurance_payout': Decimal('0'),
            'whos_paying': clean_value(row.iloc[15]),
            'driver_deduction': clean_value(row.iloc[15]).lower() == 'yes',
            'driver_deduction_amount': Decimal('0'),
            'repair_shop': clean_value(row.iloc[17]),
            'date_completed': parse_date(row.iloc[18]),
            'status': 'completed' if clean_value(row.iloc[18]) else 'pending',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        try:
            accidents_table.put_item(Item=accident)
            count += 1
            print(f"  ✓ Imported accident for {asset_id}")
        except Exception as e:
            print(f"  ✗ Error importing accident: {str(e)}")

    print(f"✅ Imported {count} accidents\n")

def import_ezpass(excel_file):
    """Import EZ Pass records"""
    print("🎫 Importing EZ Pass records...")

    df = pd.read_excel(excel_file, sheet_name='EZ Pass')

    # Skip header row
    df = df.iloc[1:]

    count = 0
    for _, row in df.iterrows():
        ezpass_id = clean_value(row.iloc[0])

        if not ezpass_id or ezpass_id == 'nan' or ezpass_id == 'EZ Pass':
            continue

        # Determine status
        canceled = clean_value(row.iloc[6])
        status = 'canceled' if canceled and canceled != 'nan' else 'active'

        ezpass = {
            'ezpass_id': ezpass_id,
            'vehicle_id': clean_value(row.iloc[1]),
            'asset_name': clean_value(row.iloc[1]),
            'driver': clean_value(row.iloc[2]),
            'driver_email': '',
            'plate_number': clean_value(row.iloc[3]),
            'status': status,
            'in_bag_id': clean_value(row.iloc[5]),
            'canceled_id': canceled,
            'territory': clean_value(row.iloc[7]),
            'assigned_driver': clean_value(row.iloc[8]),
            'notes': '',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        try:
            ezpass_table.put_item(Item=ezpass)
            count += 1
            print(f"  ✓ Imported EZ Pass {ezpass_id}")
        except Exception as e:
            print(f"  ✗ Error importing EZ Pass: {str(e)}")

    print(f"✅ Imported {count} EZ Pass records\n")

def import_sold_vehicles(excel_file):
    """Import sold vehicles"""
    print("💰 Importing sold vehicles...")

    df = pd.read_excel(excel_file, sheet_name='Sold')

    # Skip header row
    df = df.iloc[1:]

    count = 0
    for _, row in df.iterrows():
        vehicle_name = clean_value(row.iloc[1])

        if not vehicle_name or vehicle_name == 'nan' or vehicle_name == 'Vehicle Name':
            continue

        sale = {
            'sale_id': f"SALE-{vehicle_name}-{datetime.now().strftime('%Y%m%d')}",
            'vehicle_id': vehicle_name,
            'asset_name': vehicle_name,
            'year': clean_value(row.iloc[4]),
            'make': clean_value(row.iloc[5]),
            'model': clean_value(row.iloc[6]),
            'vin': clean_value(row.iloc[8]),
            'license_plate': clean_value(row.iloc[7]),
            'buyer': clean_value(row.iloc[2]),
            'sale_type': 'sold',
            'sale_date': datetime.now().isoformat(),
            'sale_price': Decimal(str(row.iloc[9])) if pd.notna(row.iloc[9]) else Decimal('0'),
            'insurance_canceled': False,
            'plate_swapped': False,
            'sold_to': '',
            'comments': clean_value(row.iloc[11]),
            'created_at': datetime.now().isoformat()
        }

        try:
            sales_table.put_item(Item=sale)

            # Also update vehicle status to sold
            vehicles_table.put_item(Item={
                'vehicle_id': vehicle_name,
                'asset_name': vehicle_name,
                'year': clean_value(row.iloc[4]),
                'make': clean_value(row.iloc[5]),
                'model': clean_value(row.iloc[6]),
                'vin': clean_value(row.iloc[8]),
                'license_plate': clean_value(row.iloc[7]),
                'status': 'sold',
                'department': '',
                'current_driver': clean_value(row.iloc[2]),
                'comments': clean_value(row.iloc[11]),
                'territory': '',
                'location': '',
                'driver_email': '',
                'driver_phone': '',
                'driver_manager': '',
                'panda_phone': '',
                'ez_pass_id': '',
                'registration_expiration': '',
                'insurance_expiration': '',
                'emissions_due': '',
                'mileage': 0,
                'unit_value': Decimal('0'),
                'gaf_presenter': False,
                'camera_installed': False,
                'vanity_ordered': False,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            })

            count += 1
            print(f"  ✓ Imported sold vehicle {vehicle_name}")
        except Exception as e:
            print(f"  ✗ Error importing sold vehicle: {str(e)}")

    print(f"✅ Imported {count} sold vehicles\n")

def import_maintenance(excel_file):
    """Import emissions and maintenance records"""
    print("🔧 Importing maintenance records...")

    df = pd.read_excel(excel_file, sheet_name='Emmisions+')

    # Skip header row
    df = df.iloc[1:]

    count = 0
    for _, row in df.iterrows():
        asset_id = clean_value(row.iloc[0])

        if not asset_id or asset_id == 'nan' or asset_id == 'Asset ID':
            continue

        due_date = parse_date(row.iloc[7])

        if due_date:
            maintenance = {
                'maintenance_id': f"MAINT-{asset_id}-emissions-{datetime.now().strftime('%Y%m%d')}",
                'vehicle_id': asset_id,
                'asset_name': asset_id,
                'type': 'emissions',
                'due_date': due_date,
                'completed_date': '',
                'status': 'pending' if datetime.fromisoformat(due_date).date() > datetime.now().date() else 'overdue',
                'provider': '',
                'cost': Decimal('0'),
                'notes': '',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }

            try:
                maintenance_table.put_item(Item=maintenance)
                count += 1
                print(f"  ✓ Imported maintenance for {asset_id}")
            except Exception as e:
                print(f"  ✗ Error importing maintenance: {str(e)}")

    print(f"✅ Imported {count} maintenance records\n")

def main():
    excel_file = '/Users/robwinters/Downloads/Fleet Dept Vehicle Sheet.xlsx'

    print("🚗 Starting Fleet Data Import...")
    print("=" * 50)
    print()

    try:
        import_vehicles(excel_file)
        import_floaters(excel_file)
        import_accidents(excel_file)
        import_ezpass(excel_file)
        import_sold_vehicles(excel_file)
        import_maintenance(excel_file)

        print()
        print("=" * 50)
        print("✅ Import complete! All data has been imported to DynamoDB.")
        print()
        print("📊 Check your tables:")
        print("   - panda-fleet-vehicles")
        print("   - panda-fleet-accidents")
        print("   - panda-fleet-ezpass")
        print("   - panda-fleet-sales")
        print("   - panda-fleet-maintenance")

    except Exception as e:
        print(f"❌ Error during import: {str(e)}")
        raise

if __name__ == '__main__':
    main()
