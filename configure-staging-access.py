#!/usr/bin/env python3
import boto3

def configure_staging_buckets():
    s3 = boto3.client('s3', region_name='us-east-2')
    
    buckets = ['staging.pandaadmin.com', 'staging.mypandapoints.com']
    
    for bucket_name in buckets:
        try:
            # Remove block public access settings
            s3.delete_public_access_block(Bucket=bucket_name)
            print(f"✅ Removed public access block for {bucket_name}")
            
            # Configure bucket for static website hosting
            s3.put_bucket_website(
                Bucket=bucket_name,
                WebsiteConfiguration={
                    'IndexDocument': {'Suffix': 'index.html'},
                    'ErrorDocument': {'Key': 'error.html'}
                }
            )
            print(f"✅ Configured website hosting for {bucket_name}")
            
        except Exception as e:
            print(f"❌ Error configuring {bucket_name}: {str(e)}")

if __name__ == "__main__":
    configure_staging_buckets()