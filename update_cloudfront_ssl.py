#!/usr/bin/env python3

import boto3
import json

def update_cloudfront_ssl():
    """Update CloudFront distribution with validated SSL certificate"""
    
    # Read certificate ARN
    try:
        with open('certificate_arn.txt', 'r') as f:
            certificate_arn = f.read().strip()
    except FileNotFoundError:
        print("Error: certificate_arn.txt not found. Run request_ssl_certificate.py first.")
        return None
    
    # Initialize AWS clients
    acm = boto3.client('acm', region_name='us-east-1')
    cloudfront = boto3.client('cloudfront')
    
    print(f"Updating CloudFront with certificate: {certificate_arn}")
    
    try:
        # Check certificate status
        cert_details = acm.describe_certificate(CertificateArn=certificate_arn)
        cert_status = cert_details['Certificate']['Status']
        
        print(f"Certificate status: {cert_status}")
        
        if cert_status != 'ISSUED':
            print("Error: Certificate is not yet validated/issued.")
            print("Please wait for DNS validation to complete before running this script.")
            return None
        
        # Get existing CloudFront distribution
        distribution_id = 'E3SCE3WCVEG662'
        
        response = cloudfront.get_distribution_config(Id=distribution_id)
        distribution_config = response['DistributionConfig']
        etag = response['ETag']
        
        print(f"Updating distribution {distribution_id}...")
        
        # Update distribution with SSL certificate and custom domains
        distribution_config['Aliases'] = {
            'Quantity': 2,
            'Items': ['www.mypandapoints.com', 'mypandapoints.com']
        }
        
        distribution_config['ViewerCertificate'] = {
            'ACMCertificateArn': certificate_arn,
            'SSLSupportMethod': 'sni-only',
            'MinimumProtocolVersion': 'TLSv1.2_2021',
            'CertificateSource': 'acm'
        }
        
        # Redirect HTTP to HTTPS
        distribution_config['DefaultCacheBehavior']['ViewerProtocolPolicy'] = 'redirect-to-https'
        
        # Update distribution
        update_response = cloudfront.update_distribution(
            Id=distribution_id,
            DistributionConfig=distribution_config,
            IfMatch=etag
        )
        
        cloudfront_domain = update_response['Distribution']['DomainName']
        
        print("CloudFront distribution updated successfully!")
        print(f"CloudFront Domain: {cloudfront_domain}")
        
        print("\n" + "=" * 80)
        print("FINAL STEPS:")
        print("=" * 80)
        print("1. Add these CNAME records to your domain DNS:")
        print(f"   www.mypandapoints.com -> {cloudfront_domain}")
        print(f"   mypandapoints.com -> {cloudfront_domain}")
        print("2. Wait for CloudFront deployment (15-20 minutes)")
        print("3. Test https://www.mypandapoints.com")
        
        return {
            'distribution_id': distribution_id,
            'cloudfront_domain': cloudfront_domain,
            'certificate_arn': certificate_arn
        }
        
    except Exception as e:
        print(f"Error updating CloudFront: {str(e)}")
        return None

if __name__ == "__main__":
    result = update_cloudfront_ssl()
    if result:
        print(f"\nCloudFront SSL setup completed!")
    else:
        print("CloudFront SSL setup failed!")