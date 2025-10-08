#!/usr/bin/env python3
import boto3
import json

def create_staging_environments():
    s3 = boto3.client('s3', region_name='us-east-2')
    cloudfront = boto3.client('cloudfront', region_name='us-east-2')
    
    # Staging bucket configurations
    staging_buckets = [
        {
            'name': 'staging.pandaadmin.com',
            'description': 'Staging environment for pandaadmin.com'
        },
        {
            'name': 'staging.mypandapoints.com', 
            'description': 'Staging environment for mypandapoints.com'
        }
    ]
    
    for bucket_config in staging_buckets:
        bucket_name = bucket_config['name']
        
        try:
            # Create S3 bucket
            print(f"Creating S3 bucket: {bucket_name}")
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': 'us-east-2'}
            )
            
            # Configure bucket for static website hosting
            s3.put_bucket_website(
                Bucket=bucket_name,
                WebsiteConfiguration={
                    'IndexDocument': {'Suffix': 'index.html'},
                    'ErrorDocument': {'Key': 'error.html'}
                }
            )
            
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
            
            print(f"✅ Created staging bucket: {bucket_name}")
            
        except Exception as e:
            print(f"❌ Error creating {bucket_name}: {str(e)}")

def copy_production_to_staging():
    s3 = boto3.client('s3', region_name='us-east-2')
    
    # Copy production files to staging
    copy_configs = [
        {
            'source': 'www.pandaadmin.com',
            'dest': 'staging.pandaadmin.com'
        },
        {
            'source': 'panda-portal-frontend-us-east-2',
            'dest': 'staging.mypandapoints.com'
        }
    ]
    
    for config in copy_configs:
        try:
            print(f"Copying {config['source']} to {config['dest']}")
            
            # List all objects in source bucket
            paginator = s3.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=config['source'])
            
            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        copy_source = {'Bucket': config['source'], 'Key': obj['Key']}
                        s3.copy_object(
                            CopySource=copy_source,
                            Bucket=config['dest'],
                            Key=obj['Key']
                        )
            
            print(f"✅ Copied all files from {config['source']} to {config['dest']}")
            
        except Exception as e:
            print(f"❌ Error copying {config['source']}: {str(e)}")

if __name__ == "__main__":
    print("🚀 Setting up staging environments...")
    create_staging_environments()
    copy_production_to_staging()
    print("✅ Staging environments setup complete!")
    print("\nStaging URLs:")
    print("- Admin Staging: http://staging.pandaadmin.com.s3-website.us-east-2.amazonaws.com")
    print("- Portal Staging: http://staging.mypandapoints.com.s3-website.us-east-2.amazonaws.com")