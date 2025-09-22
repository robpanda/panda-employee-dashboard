#!/bin/bash

# Setup Route 53 for pandaadmin.com
DOMAIN="pandaadmin.com"
BUCKET="pandaadmin-com"

echo "🌐 Setting up Route 53 for $DOMAIN..."

# Create hosted zone
echo "Creating hosted zone..."
ZONE_ID=$(aws route53 create-hosted-zone \
    --name $DOMAIN \
    --caller-reference $(date +%s) \
    --query 'HostedZone.Id' \
    --output text | cut -d'/' -f3)

echo "Zone ID: $ZONE_ID"

# Get nameservers
echo "Nameservers to update in GoDaddy:"
aws route53 get-hosted-zone --id $ZONE_ID \
    --query 'DelegationSet.NameServers' \
    --output table

# Create S3 bucket
echo "Creating S3 bucket..."
aws s3 mb s3://$BUCKET --region us-east-1

# Request SSL certificate
echo "Requesting SSL certificate..."
CERT_ARN=$(aws acm request-certificate \
    --domain-name $DOMAIN \
    --subject-alternative-names www.$DOMAIN \
    --validation-method DNS \
    --region us-east-1 \
    --query 'CertificateArn' \
    --output text)

echo "Certificate ARN: $CERT_ARN"
echo "✅ Setup initiated. Update nameservers in GoDaddy, then validate certificate."