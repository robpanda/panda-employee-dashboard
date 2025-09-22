#!/bin/bash

DOMAIN="pandaadmin.com"
BUCKET="pandaadmin"

# Get hosted zone ID
ZONE_ID=$(aws route53 list-hosted-zones --query "HostedZones[?Name=='${DOMAIN}.'].Id" --output text | cut -d'/' -f3)

echo "🌐 Setting up S3 website hosting and DNS for $DOMAIN..."

# Configure S3 bucket for website hosting
echo "Configuring S3 bucket for website hosting..."
aws s3 website s3://$BUCKET --index-document index.html --error-document error.html

# Make bucket public
aws s3api put-bucket-policy --bucket $BUCKET --policy '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::pandaadmin-com/*"
    }
  ]
}'

# Create A record pointing to S3 website endpoint
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
        }
    ]
}
EOF

# Apply DNS changes
aws route53 change-resource-record-sets \
    --hosted-zone-id $ZONE_ID \
    --change-batch file:///tmp/dns-records.json

echo "✅ S3 website hosting configured and DNS A record created."
echo "🌐 Your site will be available at: http://$DOMAIN"
echo "⏱️  Wait 5-10 minutes for DNS propagation."