#!/usr/bin/env python3

import boto3

def fix_cloudfront_origin():
    """Fix CloudFront origin settings for S3 bucket access"""
    
    cloudfront = boto3.client('cloudfront')
    s3 = boto3.client('s3')
    
    distribution_id = 'E3SCE3WCVEG662'
    bucket_name = 'mypandapoints'
    
    try:
        # Get current distribution config
        response = cloudfront.get_distribution_config(Id=distribution_id)
        distribution_config = response['DistributionConfig']
        etag = response['ETag']
        
        print("Current CloudFront configuration:")
        print(f"Origin Domain: {distribution_config['Origins']['Items'][0]['DomainName']}")
        
        # Update origin to use S3 website endpoint instead of S3 bucket endpoint
        s3_website_domain = f"{bucket_name}.s3-website.us-east-2.amazonaws.com"
        
        distribution_config['Origins']['Items'][0]['DomainName'] = s3_website_domain
        distribution_config['Origins']['Items'][0]['CustomOriginConfig'] = {
            'HTTPPort': 80,
            'HTTPSPort': 443,
            'OriginProtocolPolicy': 'http-only',
            'OriginSslProtocols': {
                'Quantity': 1,
                'Items': ['TLSv1.2']
            }
        }
        
        # Remove S3OriginConfig if it exists
        if 'S3OriginConfig' in distribution_config['Origins']['Items'][0]:
            del distribution_config['Origins']['Items'][0]['S3OriginConfig']
        
        # Set default root object
        distribution_config['DefaultRootObject'] = 'index.html'
        
        # Update distribution
        update_response = cloudfront.update_distribution(
            Id=distribution_id,
            DistributionConfig=distribution_config,
            IfMatch=etag
        )
        
        print(f"✅ CloudFront origin updated to: {s3_website_domain}")
        print("⏳ Deployment in progress (15-20 minutes)")
        
        return True
        
    except Exception as e:
        print(f"Error fixing CloudFront origin: {str(e)}")
        return False

if __name__ == "__main__":
    if fix_cloudfront_origin():
        print("\nCloudFront origin fixed! Wait for deployment to complete.")
    else:
        print("Failed to fix CloudFront origin.")