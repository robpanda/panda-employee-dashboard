# Manual Setup for Shopify Secrets

Since the deployment user doesn't have Secrets Manager permissions, please manually create the secret:

## 1. Create Secret in AWS Secrets Manager

1. Go to AWS Secrets Manager in the AWS Console
2. Click "Store a new secret"
3. Select "Other type of secret"
4. Add the following key-value pairs:
   - `store`: `my-cred`
   - `access_token`: `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`
   - `api_key`: `275ce2d95912e3201520211ff4ad0e62`
   - `api_secret`: `560b36b828895cd3600dacb17e380207`
5. Name the secret: `shopify/my-cred`
6. Add description: "Shopify API credentials for My Cred store - Panda Points redemption"

## 2. Update Lambda Role Permissions

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

## 3. Deploy Lambda Function

Run: `python3 deploy-shopify-redemption.py`

The Lambda function is already updated to use Secrets Manager.