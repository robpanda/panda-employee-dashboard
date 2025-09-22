#!/bin/bash

DOMAIN="pandaadmin.com"
BUCKET="pandaadmin"

echo "🔒 Setting up SSL for $DOMAIN..."

# 1. Request SSL certificate
echo "Requesting SSL certificate..."
CERT_ARN=$(aws acm request-certificate \
    --domain-name $DOMAIN \
    --subject-alternative-names www.$DOMAIN \
    --validation-method DNS \
    --region us-east-1 \
    --query 'CertificateArn' \
    --output text)

echo "Certificate ARN: $CERT_ARN"

# 2. Get validation records
echo "Getting DNS validation records..."
aws acm describe-certificate \
    --certificate-arn $CERT_ARN \
    --region us-east-1 \
    --query 'Certificate.DomainValidationOptions[*].[DomainName,ResourceRecord.Name,ResourceRecord.Value]' \
    --output table

echo ""
echo "📋 Next steps:"
echo "1. Add the CNAME validation records shown above to Route 53"
echo "2. Wait for certificate validation (5-30 minutes)"
echo "3. Run ./scripts/setup-cloudfront.sh to create CloudFront distribution"
echo ""
echo "💡 To add validation records automatically, run:"
echo "   ./scripts/validate-certificate.sh $CERT_ARN"