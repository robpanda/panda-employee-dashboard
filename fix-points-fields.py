#!/usr/bin/env python3
"""
Fix employee points fields by synchronizing 'points' with 'Panda Points'
Ensures the 'points' field reflects the correct current balance
"""

import boto3
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
employees_table = dynamodb.Table('panda-employees')

def fix_points_fields():
    """Synchronize points fields for all employees"""

    # Scan all employees
    response = employees_table.scan()
    employees = response['Items']

    # Continue scanning if there are more items
    while 'LastEvaluatedKey' in response:
        response = employees_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        employees.extend(response['Items'])

    fixed_count = 0

    for employee in employees:
        emp_id = employee.get('id', 'Unknown')
        panda_points = float(employee.get('Panda Points', 0) or 0)
        points = float(employee.get('points', 0) or 0)
        redeemed_points = float(employee.get('redeemed_points', 0) or 0)
        points_lifetime = float(employee.get('points_lifetime', 0) or 0)

        # Determine the correct current balance
        # If 'Panda Points' is higher than 'points', use 'Panda Points'
        if panda_points > points:
            correct_balance = panda_points
            needs_fix = True
        else:
            correct_balance = points
            needs_fix = False

        # Calculate correct lifetime (should be current + redeemed)
        expected_lifetime = correct_balance + redeemed_points

        # Fix lifetime if it's incorrect
        if points_lifetime < expected_lifetime:
            correct_lifetime = expected_lifetime
            needs_fix = True
        else:
            correct_lifetime = points_lifetime

        # Update if needed
        if needs_fix and (panda_points > 0 or points > 0 or redeemed_points > 0):
            print(f"Fixing employee {emp_id}:")
            print(f"  Old: points={points}, Panda Points={panda_points}, lifetime={points_lifetime}")
            print(f"  New: points={correct_balance}, lifetime={correct_lifetime}")

            try:
                employees_table.update_item(
                    Key={'id': emp_id},
                    UpdateExpression='SET points = :pts, points_lifetime = :lifetime',
                    ExpressionAttributeValues={
                        ':pts': Decimal(str(correct_balance)),
                        ':lifetime': Decimal(str(correct_lifetime))
                    }
                )
                fixed_count += 1
            except Exception as e:
                print(f"  ERROR updating employee {emp_id}: {e}")

    print(f"\n✅ Fixed {fixed_count} employee records")

if __name__ == '__main__':
    fix_points_fields()
