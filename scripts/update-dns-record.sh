#!/bin/bash

DOMAIN="pandaadmin.com"
BUCKET="pandaadmin"

# Get hosted zone ID
ZONE_ID=$(aws route53 list-hosted-zones --query "HostedZones[?Name=='${DOMAIN}.'].Id" --output text | cut -d'/' -f3)

echo "🔄 Updating DNS A record to point to $BUCKET bucket..."

# Delete existing A record
cat > /tmp/delete-record.json << EOF
{
    "Changes": [
        {
            "Action": "DELETE",
            "ResourceRecordSet": {
                "Name": "$DOMAIN",
                "Type": "A",
                "AliasTarget": {
                    "DNSName": "s3-website-us-east-1.amazonaws.com",
                    "EvaluateTargetHealth": false,
                    "HostedZoneId": "Z3AQBSTGFYJSTF"
                }
            }
        }
    ]
}
EOF

# Create new A record pointing to correct bucket
cat > /tmp/create-record.json << EOF
{
    "Changes": [
        {
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "$DOMAIN",
                "Type": "A",
                "AliasTarget": {
                    "DNSName": "s3-website-us-east-1.amazonaws.com",
                    "EvaluateTargetHealth": false,
                    "HostedZoneId": "Z3AQBSTGFYJSTF"
                }
            }
        }
    ]
}
EOF

# Apply changes
aws route53 change-resource-record-sets --hosted-zone-id $ZONE_ID --change-batch file:///tmp/delete-record.json
aws route53 change-resource-record-sets --hosted-zone-id $ZONE_ID --change-batch file:///tmp/create-record.json

echo "✅ DNS record updated. Wait 5-10 minutes for propagation."