#!/bin/bash

BUCKET="pandaadmin.com"

echo "🔓 Enabling public access for S3 bucket..."

# Remove public access block
aws s3api delete-public-access-block --bucket $BUCKET

# Set bucket policy for public read
aws s3api put-bucket-policy --bucket $BUCKET --policy '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::pandaadmin.com/*"
    }
  ]
}'

echo "✅ Bucket is now publicly accessible"