#!/bin/bash

DOMAIN="pandaadmin.com"
BUCKET="pandaadmin"

echo "☁️ Setting up CloudFront distribution for SSL..."

# Get certificate ARN
CERT_ARN=$(aws acm list-certificates --region us-east-1 --query "CertificateSummaryList[?DomainName=='$DOMAIN'].CertificateArn" --output text)

if [ -z "$CERT_ARN" ]; then
    echo "❌ No validated certificate found. Run ./scripts/setup-ssl.sh first"
    exit 1
fi

# Create CloudFront distribution
cat > /tmp/cloudfront-config.json << EOF
{
    "CallerReference": "$(date +%s)",
    "Comment": "SSL distribution for $DOMAIN",
    "DefaultRootObject": "index.html",
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "S3-$BUCKET",
                "DomainName": "pandaadmin.s3-website-us-east-1.amazonaws.com",
                "CustomOriginConfig": {
                    "HTTPPort": 80,
                    "HTTPSPort": 443,
                    "OriginProtocolPolicy": "http-only"
                }
            }
        ]
    },
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3-$BUCKET",
        "ViewerProtocolPolicy": "redirect-to-https",
        "TrustedSigners": {
            "Enabled": false,
            "Quantity": 0
        },
        "ForwardedValues": {
            "QueryString": false,
            "Cookies": {
                "Forward": "none"
            }
        },
        "MinTTL": 0
    },
    "Enabled": true,
    "Aliases": {
        "Quantity": 1,
        "Items": ["$DOMAIN"]
    },
    "ViewerCertificate": {
        "ACMCertificateArn": "$CERT_ARN",
        "SSLSupportMethod": "sni-only",
        "MinimumProtocolVersion": "TLSv1.2_2021"
    }
}
EOF

DISTRIBUTION_ID=$(aws cloudfront create-distribution \
    --distribution-config file:///tmp/cloudfront-config.json \
    --query 'Distribution.Id' \
    --output text)

CLOUDFRONT_DOMAIN=$(aws cloudfront get-distribution \
    --id $DISTRIBUTION_ID \
    --query 'Distribution.DomainName' \
    --output text)

echo "✅ CloudFront distribution created: $DISTRIBUTION_ID"
echo "🌐 CloudFront domain: $CLOUDFRONT_DOMAIN"
echo ""
echo "📋 Final step: Update Route 53 A record to point to CloudFront"
echo "   Run: ./scripts/update-dns-to-cloudfront.sh $CLOUDFRONT_DOMAIN"