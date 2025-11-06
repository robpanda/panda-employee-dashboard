#!/bin/bash

# Add a test vehicle to the fleet

echo "Adding test vehicles to fleet..."

# Add Vehicle 1
aws dynamodb put-item \
    --table-name panda-fleet-vehicles \
    --item '{
        "vehicle_id": {"S": "Panda-001"},
        "asset_name": {"S": "Panda 1"},
        "year": {"S": "2024"},
        "make": {"S": "Ford"},
        "model": {"S": "F-150"},
        "vin": {"S": "1FTFW1E84NFC12345"},
        "license_plate": {"S": "PANDA01"},
        "status": {"S": "assigned"},
        "department": {"S": "Production"},
        "current_driver": {"S": "John Doe"},
        "driver_email": {"S": "john@pandaexteriors.com"},
        "driver_phone": {"S": "(240) 123-4567"},
        "territory": {"S": "MD"},
        "mileage": {"N": "15000"},
        "unit_value": {"N": "45000"},
        "created_at": {"S": "2024-11-06T15:00:00Z"},
        "updated_at": {"S": "2024-11-06T15:00:00Z"}
    }' \
    --region us-east-2

echo "✅ Added Panda 1"

# Add Vehicle 2 (Floater)
aws dynamodb put-item \
    --table-name panda-fleet-vehicles \
    --item '{
        "vehicle_id": {"S": "Panda-002"},
        "asset_name": {"S": "Panda 2"},
        "year": {"S": "2023"},
        "make": {"S": "Chevrolet"},
        "model": {"S": "Silverado"},
        "vin": {"S": "1GCPYBEK1NZ123456"},
        "license_plate": {"S": "PANDA02"},
        "status": {"S": "floater"},
        "department": {"S": "Production"},
        "current_driver": {"S": ""},
        "driver_email": {"S": "fleet@pandaexteriors.com"},
        "driver_phone": {"S": ""},
        "territory": {"S": "VA"},
        "mileage": {"N": "8500"},
        "unit_value": {"N": "42000"},
        "created_at": {"S": "2024-11-06T15:00:00Z"},
        "updated_at": {"S": "2024-11-06T15:00:00Z"}
    }' \
    --region us-east-2

echo "✅ Added Panda 2 (Floater)"

# Add Vehicle 3 (Downed)
aws dynamodb put-item \
    --table-name panda-fleet-vehicles \
    --item '{
        "vehicle_id": {"S": "Panda-003"},
        "asset_name": {"S": "Panda 3"},
        "year": {"S": "2022"},
        "make": {"S": "RAM"},
        "model": {"S": "1500"},
        "vin": {"S": "1C6SRFFT2NN123456"},
        "license_plate": {"S": "PANDA03"},
        "status": {"S": "downed"},
        "department": {"S": "Production"},
        "current_driver": {"S": ""},
        "driver_email": {"S": "fleet@pandaexteriors.com"},
        "driver_phone": {"S": ""},
        "territory": {"S": "MD"},
        "mileage": {"N": "45000"},
        "unit_value": {"N": "38000"},
        "created_at": {"S": "2024-11-06T15:00:00Z"},
        "updated_at": {"S": "2024-11-06T15:00:00Z"}
    }' \
    --region us-east-2

echo "✅ Added Panda 3 (Downed)"

echo ""
echo "🎉 Test vehicles added successfully!"
echo "   - Panda 1 (Assigned)"
echo "   - Panda 2 (Floater)"
echo "   - Panda 3 (Downed)"
echo ""
echo "Access at: https://pandaadmin.com/assets.html"
echo "Click the 'Vehicles' tab to see them!"
