#!/bin/bash

# Test the CRM API endpoints

API_URL="https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/prod"

echo "Testing CRM API endpoints..."

# Test contacts endpoint
echo "1. Testing GET /contacts"
curl -X GET "$API_URL/contacts" | jq '.'

echo -e "\n2. Testing POST /contacts (single)"
curl -X POST "$API_URL/contacts" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "create",
    "contact": {
      "name": "Test User",
      "email": "test@example.com",
      "phone": "555-0123",
      "status": "active",
      "lists": ["leads"]
    }
  }' | jq '.'

echo -e "\n3. Testing GET /collections"
curl -X GET "$API_URL/collections" | jq '.'

echo -e "\n4. Testing GET /collections?action=counts"
curl -X GET "$API_URL/collections?action=counts" | jq '.'

echo -e "\n5. Testing POST /collections"
curl -X POST "$API_URL/collections" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "create",
    "collection": {
      "name": "Test Collection",
      "email": "test@example.com",
      "phone": "555-0123",
      "amount": 1500.00,
      "installDate": "2024-01-15",
      "stage": "31-60"
    }
  }' | jq '.'

echo -e "\n6. Testing GET /config"
curl -X GET "$API_URL/config" | jq '.'

echo -e "\nAPI testing complete!"