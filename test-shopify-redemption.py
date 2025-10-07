#!/usr/bin/env python3

import requests
import json

def test_gift_card_redemption():
    """Test the gift card redemption functionality"""
    
    API_URL = 'https://dfu3zr3dnrvgiiwa2yu77cz5fq0rqmth.lambda-url.us-east-2.on.aws'
    
    # Test data - using a test employee ID
    test_data = {
        'employee_id': 'TEST001',
        'points': 25  # Test with $25 gift card
    }
    
    print("🧪 Testing Shopify gift card redemption...")
    print(f"📊 Test data: {test_data}")
    
    try:
        response = requests.post(
            f'{API_URL}/gift-cards',
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=30
        )
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Gift card redemption successful!")
            print(f"🎁 Gift card code: {result.get('gift_card_code', 'N/A')}")
            print(f"💰 Value: ${result.get('value', 'N/A')}")
            print(f"🏦 New balance: {result.get('new_balance', 'N/A')} points")
            return True
        else:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            print(f"❌ Redemption failed: {error_data}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_points_lookup():
    """Test points lookup functionality"""
    
    API_URL = 'https://dfu3zr3dnrvgiiwa2yu77cz5fq0rqmth.lambda-url.us-east-2.on.aws'
    
    print("\n🔍 Testing points lookup...")
    
    try:
        response = requests.get(f'{API_URL}/points/TEST001', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Points lookup successful!")
            print(f"👤 Employee: {data.get('name', 'N/A')}")
            print(f"⭐ Points: {data.get('points', 0)}")
            print(f"🏢 Department: {data.get('department', 'N/A')}")
            return True
        else:
            print(f"❌ Points lookup failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Points lookup failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Shopify redemption setup...")
    
    # Test points lookup first
    points_success = test_points_lookup()
    
    if points_success:
        # Test gift card redemption
        redemption_success = test_gift_card_redemption()
        
        if redemption_success:
            print("\n✅ All tests passed! Shopify redemption is working correctly.")
        else:
            print("\n⚠️ Points lookup works, but gift card redemption needs attention.")
    else:
        print("\n⚠️ Points lookup failed - check employee data first.")
    
    print("\n📝 Next steps:")
    print("1. Visit https://mypandapoints.com")
    print("2. Enter a valid Employee ID")
    print("3. Test the redemption functionality")