#!/bin/bash

CERT_ARN=$1
DOMAIN="pandaadmin.com"

if [ -z "$CERT_ARN" ]; then
    echo "Usage: $0 <certificate-arn>"
    exit 1
fi

echo "🔍 Adding DNS validation records for certificate..."

# Get hosted zone ID
ZONE_ID=$(aws route53 list-hosted-zones --query "HostedZones[?Name=='${DOMAIN}.'].Id" --output text | cut -d'/' -f3)

# Get validation records and create Route 53 records
aws acm describe-certificate \
    --certificate-arn $CERT_ARN \
    --region us-east-1 \
    --query 'Certificate.DomainValidationOptions[0].ResourceRecord' \
    --output json > /tmp/validation.json

VALIDATION_NAME=$(cat /tmp/validation.json | jq -r '.Name')
VALIDATION_VALUE=$(cat /tmp/validation.json | jq -r '.Value')

# Create validation record
cat > /tmp/validation-record.json << EOF
{
    "Changes": [
        {
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "$VALIDATION_NAME",
                "Type": "CNAME",
                "TTL": 300,
                "ResourceRecords": [
                    {
                        "Value": "$VALIDATION_VALUE"
                    }
                ]
            }
        }
    ]
}
EOF

aws route53 change-resource-record-sets \
    --hosted-zone-id $ZONE_ID \
    --change-batch file:///tmp/validation-record.json

echo "✅ Validation record added. Certificate will be validated automatically."
echo "⏱️  Wait 5-30 minutes, then run: ./scripts/setup-cloudfront.sh"