# Shopify Gift Card Redemption Setup

## Overview
The mypandapoints.com portal now supports gift card redemption through the My Cred Shopify store.

## AWS Secrets Manager Setup Required

### 1. Create Secret
Create a secret in AWS Secrets Manager with the name: `shopify/my-cred`

The secret should contain the following JSON structure:
```json
{
    "store": "my-cred",
    "access_token": "[SHOPIFY_ACCESS_TOKEN]",
    "api_key": "[SHOPIFY_API_KEY]", 
    "api_secret": "[SHOPIFY_API_SECRET]"
}
```

### 2. Lambda Permissions
Add the following policy to the Lambda execution role `panda-lambda-role`:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue"
            ],
            "Resource": "arn:aws:secretsmanager:us-east-2:*:secret:shopify/my-cred*"
        }
    ]
}
```

## Features
- 1 point = $1 gift card value
- Gift cards expire after 1 year
- Automatic points deduction
- Transaction history tracking
- Secure credential management

## Usage
1. Employee visits mypandapoints.com
2. Enters their Employee ID
3. Views current points balance
4. Enters points amount to redeem
5. Receives gift card code for My Cred store