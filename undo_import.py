#!/usr/bin/env python3
"""
Undo Employee Import Script
Restores employee database to state before the last import
"""

import requests
import json
from datetime import datetime

API_BASE = 'https://w40mq6ab11.execute-api.us-east-2.amazonaws.com/prod'

def undo_import():
    """Undo the last employee import by removing today's additions and reactivating terminations"""
    
    print("🔄 Starting undo process...")
    
    try:
        # Get current employee data
        print("📥 Fetching current employee data...")
        response = requests.get(f'{API_BASE}/employees')
        response.raise_for_status()
        data = response.json()
        
        if 'employees' not in data:
            raise Exception('No employee data found')
        
        employees = data['employees']
        today = datetime.now().strftime('%Y-%m-%d')
        
        print(f"📊 Found {len(employees)} total employees")
        
        # Track changes
        removed_count = 0
        reactivated_count = 0
        restored_employees = []
        
        for emp in employees:
            # Remove employees added today (from import)
            if emp.get('Employment Date') == today:
                print(f"❌ Removing newly added employee: {emp.get('First Name', '')} {emp.get('Last Name', '')}")
                removed_count += 1
                continue
            
            # Reactivate employees terminated today
            if emp.get('Termination Date') == today:
                print(f"✅ Reactivating employee: {emp.get('First Name', '')} {emp.get('Last Name', '')}")
                emp.pop('Termination Date', None)
                emp['Terminated'] = 'No'
                reactivated_count += 1
            
            restored_employees.append(emp)
        
        # Save restored data
        print("💾 Saving restored employee data...")
        save_response = requests.post(
            f'{API_BASE}/employees',
            headers={'Content-Type': 'application/json'},
            json={'employees': restored_employees}
        )
        save_response.raise_for_status()
        
        print(f"✅ Undo completed successfully!")
        print(f"   • Removed {removed_count} newly added employees")
        print(f"   • Reactivated {reactivated_count} terminated employees")
        print(f"   • Total employees after undo: {len(restored_employees)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during undo: {str(e)}")
        return False

if __name__ == "__main__":
    success = undo_import()
    if success:
        print("\n🎉 Import has been successfully undone!")
        print("You can now view the restored data at:")
        print("https://panda-exteriors-map-bucket.s3.amazonaws.com/leads/employee_dashboard.html")
    else:
        print("\n💥 Undo failed. Please check the error messages above.")