#!/usr/bin/env python3

import requests

def test_shopify_store_url():
    """Test different Shopify store URL formats"""
    
    access_token = "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"
    
    # Test different store URL formats
    store_formats = [
        "my-cred",
        "mycred", 
        "my-cred-shopify-redemption"
    ]
    
    for store in store_formats:
        url = f'https://{store}.myshopify.com/admin/api/2023-10/shop.json'
        headers = {
            'X-Shopify-Access-Token': access_token,
            'Content-Type': 'application/json'
        }
        
        print(f"🧪 Testing store URL: {store}.myshopify.com")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                shop_data = response.json()
                print(f"   ✅ Success! Shop name: {shop_data.get('shop', {}).get('name', 'Unknown')}")
                return store
            else:
                print(f"   ❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    print("🔍 Testing Shopify store URL formats...")
    correct_store = test_shopify_store_url()
    
    if correct_store:
        print(f"\n✅ Correct store URL found: {correct_store}.myshopify.com")
    else:
        print("\n❌ No working store URL found. Please verify the store name and access token.")