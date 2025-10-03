#!/usr/bin/env python3

import boto3
import json
import time

def setup_ssl_certificate():
    """Request SSL certificate and update CloudFront distribution for HTTPS"""
    
    # Initialize AWS clients
    acm = boto3.client('acm', region_name='us-east-1')  # ACM certificates for CloudFront must be in us-east-1
    cloudfront = boto3.client('cloudfront')
    
    print("Setting up SSL certificate for www.mypandapoints.com...")
    
    try:
        # Step 1: Request SSL certificate
        print("\n1. Requesting SSL certificate...")
        cert_response = acm.request_certificate(
            DomainName='www.mypandapoints.com',
            SubjectAlternativeNames=['mypandapoints.com'],
            ValidationMethod='DNS'
        )
        
        certificate_arn = cert_response['CertificateArn']
        print(f"Certificate ARN: {certificate_arn}")
        
        # Step 2: Get DNS validation records
        print("\n2. Getting DNS validation records...")
        time.sleep(5)  # Wait for certificate to be processed
        
        cert_details = acm.describe_certificate(CertificateArn=certificate_arn)
        validation_options = cert_details['Certificate']['DomainValidationOptions']
        
        print("\nDNS Validation Records (add these to your domain DNS):")
        print("=" * 60)
        for option in validation_options:
            if 'ResourceRecord' in option:
                record = option['ResourceRecord']
                print(f"Domain: {option['DomainName']}")
                print(f"Record Type: {record['Type']}")
                print(f"Record Name: {record['Name']}")
                print(f"Record Value: {record['Value']}")
                print("-" * 40)
        
        # Step 3: Update CloudFront distribution
        print("\n3. Updating CloudFront distribution...")
        
        # Get existing distribution
        distribution_id = 'E3SCE3WCVEG662'  # Your existing distribution
        
        # Get current distribution config
        response = cloudfront.get_distribution_config(Id=distribution_id)
        distribution_config = response['DistributionConfig']
        etag = response['ETag']
        
        # Update distribution with SSL certificate and custom domain
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
        
        # Update viewer protocol policy to redirect HTTP to HTTPS
        distribution_config['DefaultCacheBehavior']['ViewerProtocolPolicy'] = 'redirect-to-https'
        
        # Update distribution
        update_response = cloudfront.update_distribution(
            Id=distribution_id,
            DistributionConfig=distribution_config,
            IfMatch=etag
        )
        
        print(f"Distribution updated successfully!")
        print(f"Distribution Domain: {update_response['Distribution']['DomainName']}")
        
        print("\n" + "=" * 60)
        print("NEXT STEPS:")
        print("=" * 60)
        print("1. Add the DNS validation records shown above to your domain DNS")
        print("2. Wait for certificate validation (can take up to 30 minutes)")
        print("3. Add CNAME records to point your domain to CloudFront:")
        print(f"   www.mypandapoints.com -> {update_response['Distribution']['DomainName']}")
        print(f"   mypandapoints.com -> {update_response['Distribution']['DomainName']}")
        print("4. Wait for CloudFront deployment (15-20 minutes)")
        print("5. Test https://www.mypandapoints.com")
        
        return {
            'certificate_arn': certificate_arn,
            'distribution_id': distribution_id,
            'cloudfront_domain': update_response['Distribution']['DomainName']
        }
        
    except Exception as e:
        print(f"Error setting up SSL: {str(e)}")
        return None

if __name__ == "__main__":
    result = setup_ssl_certificate()
    if result:
        print(f"\nSSL setup initiated successfully!")
        print(f"Certificate ARN: {result['certificate_arn']}")
        print(f"CloudFront Domain: {result['cloudfront_domain']}")
    else:
        print("SSL setup failed!")