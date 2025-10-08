#!/usr/bin/env python3
import boto3
import os
import mimetypes

def deploy_to_staging(site_type='admin'):
    """Deploy files to staging environment"""
    s3 = boto3.client('s3', region_name='us-east-2')
    
    if site_type == 'admin':
        bucket_name = 'staging.pandaadmin.com'
        local_path = '/Users/robwinters/Documents/GitHub/panda-employee-dashboard'
        files_to_deploy = [
            'index.html', 'admin.html', 'employee.html', 'points.html', 
            'referrals.html', 'login.html', 'style.css'
        ]
    else:  # portal
        bucket_name = 'staging.mypandapoints.com'
        local_path = '/Users/robwinters/Documents/GitHub/mypandapoints'
        files_to_deploy = [
            'dashboard.html', 'profile.html', 'login.html', 'referrals.html',
            'points-portal.html', 'style.css'
        ]
    
    print(f"🚀 Deploying to staging: {bucket_name}")
    
    for file_name in files_to_deploy:
        file_path = os.path.join(local_path, file_name)
        
        if os.path.exists(file_path):
            try:
                # Determine content type
                content_type, _ = mimetypes.guess_type(file_name)
                if content_type is None:
                    content_type = 'text/html' if file_name.endswith('.html') else 'text/plain'
                
                # Upload file
                with open(file_path, 'rb') as f:
                    s3.put_object(
                        Bucket=bucket_name,
                        Key=file_name,
                        Body=f.read(),
                        ContentType=content_type,
                        CacheControl='no-cache, no-store, must-revalidate'
                    )
                
                print(f"✅ Uploaded: {file_name}")
                
            except Exception as e:
                print(f"❌ Error uploading {file_name}: {str(e)}")
        else:
            print(f"⚠️  File not found: {file_path}")

def promote_to_production(site_type='admin'):
    """Promote staging to production"""
    s3 = boto3.client('s3', region_name='us-east-2')
    
    if site_type == 'admin':
        staging_bucket = 'staging.pandaadmin.com'
        prod_bucket = 'www.pandaadmin.com'
    else:  # portal
        staging_bucket = 'staging.mypandapoints.com'
        prod_bucket = 'panda-portal-frontend-us-east-2'
    
    print(f"🚀 Promoting {staging_bucket} to {prod_bucket}")
    
    try:
        # List all objects in staging
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=staging_bucket)
        
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    copy_source = {'Bucket': staging_bucket, 'Key': obj['Key']}
                    s3.copy_object(
                        CopySource=copy_source,
                        Bucket=prod_bucket,
                        Key=obj['Key']
                    )
        
        print(f"✅ Successfully promoted to production: {prod_bucket}")
        
    except Exception as e:
        print(f"❌ Error promoting to production: {str(e)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python deploy-to-staging.py [deploy|promote] [admin|portal]")
        sys.exit(1)
    
    action = sys.argv[1]
    site_type = sys.argv[2] if len(sys.argv) > 2 else 'admin'
    
    if action == 'deploy':
        deploy_to_staging(site_type)
    elif action == 'promote':
        promote_to_production(site_type)
    else:
        print("Invalid action. Use 'deploy' or 'promote'")