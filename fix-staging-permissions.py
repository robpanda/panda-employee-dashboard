#!/usr/bin/env python3
import boto3
import json

def fix_staging_permissions():
    s3 = boto3.client('s3', region_name='us-east-2')
    
    buckets = ['staging.pandaadmin.com', 'staging.mypandapoints.com']
    
    for bucket_name in buckets:
        try:
            # Set bucket policy for public read access
            bucket_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicReadGetObject",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{bucket_name}/*"
                    }
                ]
            }
            
            s3.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(bucket_policy)
            )
            
            print(f"✅ Fixed permissions for {bucket_name}")
            
        except Exception as e:
            print(f"❌ Error fixing {bucket_name}: {str(e)}")

if __name__ == "__main__":
    fix_staging_permissions()