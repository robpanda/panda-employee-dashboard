# Route 53 + SSL Setup for pandaadmin.com

## Step 1: Transfer DNS to Route 53

### 1.1 Create Hosted Zone
```bash
aws route53 create-hosted-zone \
    --name pandaadmin.com \
    --caller-reference $(date +%s)
```

### 1.2 Get Name Servers
```bash
aws route53 get-hosted-zone --id /hostedzone/YOUR_ZONE_ID
```

### 1.3 Update GoDaddy DNS
1. Login to GoDaddy
2. Go to DNS Management for pandaadmin.com
3. Change nameservers to the 4 AWS nameservers from step 1.2

## Step 2: Create S3 Bucket for Website

### 2.1 Create Bucket
```bash
aws s3 mb s3://pandaadmin-com --region us-east-1
```

### 2.2 Configure Website Hosting
```bash
aws s3 website s3://pandaadmin-com \
    --index-document index.html \
    --error-document error.html
```

### 2.3 Set Bucket Policy
```bash
cat > bucket-policy.json << EOF
{
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
}
EOF

aws s3api put-bucket-policy \
    --bucket pandaadmin-com \
    --policy file://bucket-policy.json
```

## Step 3: Request SSL Certificate

### 3.1 Request Certificate
```bash
aws acm request-certificate \
    --domain-name pandaadmin.com \
    --subject-alternative-names www.pandaadmin.com \
    --validation-method DNS \
    --region us-east-1
```

### 3.2 Get Certificate Details
```bash
aws acm describe-certificate --certificate-arn YOUR_CERT_ARN
```

### 3.3 Add DNS Validation Records
```bash
# Use the CNAME records from step 3.2 to create Route 53 records
aws route53 change-resource-record-sets \
    --hosted-zone-id YOUR_ZONE_ID \
    --change-batch file://cert-validation.json
```

## Step 4: Create Application Load Balancer

### 4.1 Create ALB
```bash
aws elbv2 create-load-balancer \
    --name pandaadmin-alb \
    --subnets subnet-12345 subnet-67890 \
    --security-groups sg-12345 \
    --scheme internet-facing \
    --type application
```

### 4.2 Create Target Group
```bash
aws elbv2 create-target-group \
    --name pandaadmin-targets \
    --protocol HTTP \
    --port 80 \
    --vpc-id vpc-12345 \
    --target-type ip
```

### 4.3 Create HTTPS Listener
```bash
aws elbv2 create-listener \
    --load-balancer-arn YOUR_ALB_ARN \
    --protocol HTTPS \
    --port 443 \
    --certificates CertificateArn=YOUR_CERT_ARN \
    --default-actions Type=redirect,RedirectConfig='{Protocol=HTTPS,Port=443,Host=pandaadmin-com.s3-website-us-east-1.amazonaws.com,StatusCode=HTTP_301}'
```

## Step 5: Create Route 53 Records

### 5.1 Create A Record for Root Domain
```bash
cat > a-record.json << EOF
{
    "Changes": [
        {
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "pandaadmin.com",
                "Type": "A",
                "AliasTarget": {
                    "DNSName": "YOUR_ALB_DNS_NAME",
                    "EvaluateTargetHealth": false,
                    "HostedZoneId": "YOUR_ALB_ZONE_ID"
                }
            }
        }
    ]
}
EOF

aws route53 change-resource-record-sets \
    --hosted-zone-id YOUR_ZONE_ID \
    --change-batch file://a-record.json
```

### 5.2 Create CNAME for www
```bash
cat > www-record.json << EOF
{
    "Changes": [
        {
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "www.pandaadmin.com",
                "Type": "CNAME",
                "TTL": 300,
                "ResourceRecords": [
                    {
                        "Value": "pandaadmin.com"
                    }
                ]
            }
        }
    ]
}
EOF

aws route53 change-resource-record-sets \
    --hosted-zone-id YOUR_ZONE_ID \
    --change-batch file://www-record.json
```

## Step 6: Deploy Website

### 6.1 Deploy Files
```bash
cd /Users/robwinters/Documents/GitHub/panda-employee-dashboard

# Deploy to S3
aws s3 sync public/ s3://pandaadmin-com/
aws s3 sync src/ s3://pandaadmin-com/src/

# Set correct content types
aws s3 cp public/index.html s3://pandaadmin-com/index.html --content-type "text/html"
aws s3 cp src/pages/dashboard.html s3://pandaadmin-com/dashboard.html --content-type "text/html"
aws s3 cp src/pages/leads.html s3://pandaadmin-com/leads.html --content-type "text/html"
```

## Step 7: Test Setup

### 7.1 Test URLs
- https://pandaadmin.com
- https://www.pandaadmin.com
- https://pandaadmin.com/dashboard.html
- https://pandaadmin.com/leads.html

### 7.2 Verify SSL
```bash
curl -I https://pandaadmin.com
```

## Simplified Alternative: S3 + Route 53 Only

If ALB is too complex, use direct S3 website hosting:

```bash
# Create ALIAS record pointing directly to S3
cat > s3-alias.json << EOF
{
    "Changes": [
        {
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "pandaadmin.com",
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
```

**Note**: S3 website hosting doesn't support SSL directly. Use ALB method above for HTTPS.