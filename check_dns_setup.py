#!/usr/bin/env python3

import boto3

def check_dns_setup():
    """Check current DNS setup and provide required records"""
    
    # Read certificate ARN
    try:
        with open('certificate_arn.txt', 'r') as f:
            certificate_arn = f.read().strip()
    except FileNotFoundError:
        print("Error: certificate_arn.txt not found.")
        return
    
    # Check certificate status
    acm = boto3.client('acm', region_name='us-east-1')
    
    try:
        cert_details = acm.describe_certificate(CertificateArn=certificate_arn)
        cert_status = cert_details['Certificate']['Status']
        validation_options = cert_details['Certificate']['DomainValidationOptions']
        
        print("=" * 80)
        print("CURRENT CERTIFICATE STATUS")
        print("=" * 80)
        print(f"Status: {cert_status}")
        print(f"ARN: {certificate_arn}")
        
        print("\n" + "=" * 80)
        print("REQUIRED DNS RECORDS FOR YOUR DOMAIN")
        print("=" * 80)
        
        print("\n1. SSL CERTIFICATE VALIDATION RECORDS (CNAME):")
        print("-" * 50)
        for option in validation_options:
            if 'ResourceRecord' in option:
                record = option['ResourceRecord']
                # Remove the domain suffix for cleaner display
                name = record['Name'].replace('.mypandapoints.com.', '')
                print(f"Domain: {option['DomainName']}")
                print(f"Type: CNAME")
                print(f"Name: {name}")
                print(f"Value: {record['Value']}")
                print()
        
        print("2. DOMAIN POINTING RECORDS:")
        print("-" * 50)
        print("Type: CNAME")
        print("Name: www")
        print("Value: d1aormva1txfoz.cloudfront.net")
        print()
        print("Type: A (or CNAME if your DNS provider supports CNAME for root)")
        print("Name: @ (root domain)")
        print("Value: d1aormva1txfoz.cloudfront.net (or use CloudFront IP if A record required)")
        print()
        
        print("=" * 80)
        print("CURRENT ISSUES TO FIX:")
        print("=" * 80)
        print("1. Add the SSL validation CNAME records above")
        print("2. Change the A record @ from 13.32.0.4 to point to CloudFront")
        print("3. The 403 error suggests CloudFront can't reach your S3 bucket")
        
        if cert_status == 'ISSUED':
            print("\n✅ Certificate is validated and ready!")
            print("Run: python3 update_cloudfront_ssl.py")
        else:
            print(f"\n⏳ Certificate status: {cert_status}")
            print("Add the validation CNAME records and wait for validation")
            
    except Exception as e:
        print(f"Error checking certificate: {str(e)}")

if __name__ == "__main__":
    check_dns_setup()