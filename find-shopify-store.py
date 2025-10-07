#!/usr/bin/env python3

import requests

def find_shopify_store():
    """Try to find the correct Shopify store name"""
    
    access_token = "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"
    
    # Common store name patterns to try
    possible_stores = [
        "my-cred",
        "mycred", 
        "my-cred-store",
        "mycredstore",
        "panda-my-cred",
        "pandamycred",
        "my-cred-shopify",
        "mycredshopify"
    ]
    
    print("🔍 Searching for correct Shopify store name...")
    
    for store in possible_stores:
        # Test both shop.json and gift_cards endpoints
        endpoints = [
            f'https://{store}.myshopify.com/admin/api/2023-10/shop.json',
            f'https://{store}.myshopify.com/admin/api/2023-10/gift_cards.json'
        ]
        
        for url in endpoints:
            headers = {
                'X-Shopify-Access-Token': access_token,
                'Content-Type': 'application/json'
            }
            
            try:
                response = requests.get(url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    print(f"✅ Found working store: {store}.myshopify.com")
                    if 'shop.json' in url:
                        shop_data = response.json()
                        print(f"   Shop name: {shop_data.get('shop', {}).get('name', 'Unknown')}")
                        print(f"   Domain: {shop_data.get('shop', {}).get('domain', 'Unknown')}")
                    return store
                elif response.status_code == 401:
                    print(f"🔑 Store exists but access token invalid: {store}")
                elif response.status_code != 404:
                    print(f"⚠️ Store {store} returned: {response.status_code}")
                    
            except Exception as e:
                continue
    
    print("❌ Could not find the correct store name")
    print("💡 Please check:")
    print("   1. The actual Shopify store URL/name")
    print("   2. The access token permissions")
    print("   3. That the store exists and is active")
    
    return None

if __name__ == "__main__":
    find_shopify_store()