#!/bin/bash

DOMAIN="pandaadmin.com"
BUCKET="pandaadmin-com"

# Get hosted zone ID
ZONE_ID=$(aws route53 list-hosted-zones --query "HostedZones[?Name=='${DOMAIN}.'].Id" --output text | cut -d'/' -f3)

echo "🌐 Creating DNS records for $DOMAIN (Zone: $ZONE_ID)..."

# Create A record pointing to S3 bucket
cat > /tmp/dns-records.json << EOF
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
        },
        {
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "www.$DOMAIN",
                "Type": "CNAME",
                "TTL": 300,
                "ResourceRecords": [
                    {
                        "Value": "$DOMAIN"
                    }
                ]
            }
        }
    ]
}
EOF

# Apply DNS changes
aws route53 change-resource-record-sets \
    --hosted-zone-id $ZONE_ID \
    --change-batch file:///tmp/dns-records.json

echo "✅ DNS records created. Wait 5-10 minutes for propagation."