#!/usr/bin/env python3
import re

def fix_all_cors():
    with open('lambda_function.py', 'r') as f:
        content = f.read()
    
    # Remove all existing CORS headers first
    content = re.sub(r"'Access-Control-Allow-Origin': '\*',?\s*", "", content)
    content = re.sub(r"'Access-Control-Allow-Headers': '[^']*',?\s*", "", content)
    content = re.sub(r"'Access-Control-Allow-Methods': '[^']*',?\s*", "", content)
    
    # Clean up empty lines in headers
    content = re.sub(r"'headers': {\s*'Content-Type': 'application/json',\s*\n\s*\n\s*}", 
                     "'headers': {'Content-Type': 'application/json'}", content)
    
    # Add consistent CORS headers to all responses
    content = re.sub(
        r"'headers': {\s*'Content-Type': 'application/json'\s*}",
        "'headers': {\n                'Content-Type': 'application/json',\n                'Access-Control-Allow-Origin': '*',\n                'Access-Control-Allow-Headers': 'Content-Type,Authorization'\n            }",
        content
    )
    
    with open('lambda_function.py', 'w') as f:
        f.write(content)
    
    print("✅ Completely fixed all CORS headers")

if __name__ == "__main__":
    fix_all_cors()