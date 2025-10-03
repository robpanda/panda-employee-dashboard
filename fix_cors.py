#!/usr/bin/env python3
import re

def fix_cors_headers():
    with open('lambda_function.py', 'r') as f:
        content = f.read()
    
    # Replace incomplete CORS headers
    content = re.sub(
        r"'headers': {\s*'Content-Type': 'application/json',\s*\n\s*\n\s*'Access-Control-Allow-Headers': 'Content-Type,Authorization'\s*},",
        "'headers': {\n                'Content-Type': 'application/json',\n                'Access-Control-Allow-Origin': '*',\n                'Access-Control-Allow-Headers': 'Content-Type,Authorization'\n            },",
        content
    )
    
    # Add missing CORS headers to responses that only have Content-Type
    content = re.sub(
        r"'headers': {'Content-Type': 'application/json'},",
        "'headers': {\n                'Content-Type': 'application/json',\n                'Access-Control-Allow-Origin': '*',\n                'Access-Control-Allow-Headers': 'Content-Type,Authorization'\n            },",
        content
    )
    
    with open('lambda_function.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed CORS headers in lambda_function.py")

if __name__ == "__main__":
    fix_cors_headers()