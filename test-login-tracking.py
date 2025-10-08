import boto3
import json
from datetime import datetime, timedelta
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('panda-employees')

def test_login_tracking():
    """Test the login tracking functionality"""
    try:
        # Get a sample employee to test with
        response = table.scan(Limit=5)
        employees = response.get('Items', [])
        
        if not employees:
            print("❌ No employees found to test with")
            return
            
        test_employee = employees[0]
        emp_id = test_employee.get('id')
        emp_name = f"{test_employee.get('first_name', '')} {test_employee.get('last_name', '')}".strip()
        
        print(f"🧪 Testing login tracking for: {emp_name} (ID: {emp_id})")
        
        # Check current login history
        login_history = test_employee.get('login_history', [])
        print(f"📊 Current login history entries: {len(login_history)}")
        
        if login_history:
            print("📋 Recent login entries:")
            for i, login in enumerate(login_history[-3:]):  # Show last 3 entries
                timestamp = login.get('timestamp', 'Unknown')
                status = login.get('status', 'Unknown')
                source = login.get('source', 'Unknown')
                print(f"   {i+1}. {timestamp} - {status} - {source}")
        else:
            print("⚠️  No login history found")
            
        # Check last_login field
        last_login = test_employee.get('last_login')
        if last_login:
            print(f"🕐 Last login timestamp: {last_login}")
        else:
            print("⚠️  No last_login timestamp found")
            
        # Test adding a new login entry
        print("\n🔄 Testing login tracking update...")
        
        new_login_entry = {
            'timestamp': datetime.now().isoformat(),
            'status': 'Success',
            'source': 'Test Script',
            'ip_address': '127.0.0.1'
        }
        
        # Update login history
        updated_history = login_history + [new_login_entry]
        # Keep only last 60 days of entries (for testing, we'll keep last 50 entries)
        if len(updated_history) > 50:
            updated_history = updated_history[-50:]
            
        # Update the employee record
        table.update_item(
            Key={'id': emp_id},
            UpdateExpression='SET login_history = :history, last_login = :last_login',
            ExpressionAttributeValues={
                ':history': updated_history,
                ':last_login': new_login_entry['timestamp']
            }
        )
        
        print("✅ Successfully added test login entry")
        
        # Verify the update
        response = table.get_item(Key={'id': emp_id})
        updated_employee = response.get('Item', {})
        updated_login_history = updated_employee.get('login_history', [])
        
        print(f"📊 Updated login history entries: {len(updated_login_history)}")
        print(f"🕐 Updated last login: {updated_employee.get('last_login')}")
        
        # Test login history retrieval (simulate API call)
        print("\n🔍 Testing login history retrieval...")
        
        # Filter to last 60 days
        sixty_days_ago = datetime.now() - timedelta(days=60)
        recent_logins = []
        
        for login in updated_login_history:
            try:
                login_date = datetime.fromisoformat(login['timestamp'].replace('Z', '+00:00'))
                if login_date >= sixty_days_ago:
                    recent_logins.append(login)
            except:
                # Keep entries with invalid timestamps for now
                recent_logins.append(login)
                
        print(f"📅 Login entries in last 60 days: {len(recent_logins)}")
        
        if recent_logins:
            print("📋 Recent login entries (last 3):")
            for i, login in enumerate(recent_logins[-3:]):
                timestamp = login.get('timestamp', 'Unknown')
                status = login.get('status', 'Unknown')
                source = login.get('source', 'Unknown')
                print(f"   {i+1}. {timestamp} - {status} - {source}")
                
        print("\n✅ Login tracking test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing login tracking: {str(e)}")

if __name__ == "__main__":
    test_login_tracking()