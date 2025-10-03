#!/usr/bin/env python3

import boto3
import json
import time

def request_ssl_certificate():
    """Request SSL certificate and show DNS validation records"""
    
    # Initialize AWS client (must be us-east-1 for CloudFront certificates)
    acm = boto3.client('acm', region_name='us-east-1')
    
    print("Requesting SSL certificate for www.mypandapoints.com...")
    
    try:
        # Request SSL certificate
        cert_response = acm.request_certificate(
            DomainName='www.mypandapoints.com',
            SubjectAlternativeNames=['mypandapoints.com'],
            ValidationMethod='DNS'
        )
        
        certificate_arn = cert_response['CertificateArn']
        print(f"Certificate ARN: {certificate_arn}")
        
        # Wait a moment for certificate to be processed
        print("\nWaiting for certificate details...")
        time.sleep(10)
        
        # Get DNS validation records
        cert_details = acm.describe_certificate(CertificateArn=certificate_arn)
        validation_options = cert_details['Certificate']['DomainValidationOptions']
        
        print("\n" + "=" * 80)
        print("DNS VALIDATION RECORDS - ADD THESE TO YOUR DOMAIN DNS:")
        print("=" * 80)
        
        for option in validation_options:
            if 'ResourceRecord' in option:
                record = option['ResourceRecord']
                print(f"\nDomain: {option['DomainName']}")
                print(f"Record Type: {record['Type']}")
                print(f"Record Name: {record['Name']}")
                print(f"Record Value: {record['Value']}")
                print("-" * 60)
        
        print("\n" + "=" * 80)
        print("NEXT STEPS:")
        print("=" * 80)
        print("1. Add the CNAME records above to your domain's DNS settings")
        print("2. Wait for DNS propagation and certificate validation (5-30 minutes)")
        print("3. Run update_cloudfront_ssl.py to update CloudFront with the certificate")
        print("4. Add domain CNAME records pointing to CloudFront")
        print("5. Test https://www.mypandapoints.com")
        
        # Save certificate ARN for later use
        with open('certificate_arn.txt', 'w') as f:
            f.write(certificate_arn)
        print(f"\nCertificate ARN saved to certificate_arn.txt")
        
        return certificate_arn
        
    except Exception as e:
        print(f"Error requesting certificate: {str(e)}")
        return None

if __name__ == "__main__":
    cert_arn = request_ssl_certificate()
    if cert_arn:
        print(f"\nCertificate requested successfully!")
        print(f"ARN: {cert_arn}")
    else:
        print("Certificate request failed!")