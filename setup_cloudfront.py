#!/usr/bin/env python3
import boto3
import json
import time

def create_cloudfront_distribution():
    cloudfront = boto3.client('cloudfront')
    
    # CloudFront distribution configuration
    distribution_config = {
        'CallerReference': f'mypandapoints-{int(time.time())}',
        'Aliases': {
            'Quantity': 2,
            'Items': ['mypandapoints.com', 'www.mypandapoints.com']
        },
        'DefaultRootObject': 'index.html',
        'Comment': 'CloudFront distribution for mypandapoints.com',
        'Enabled': True,
        'Origins': {
            'Quantity': 1,
            'Items': [
                {
                    'Id': 'S3-mypandapoints',
                    'DomainName': 'mypandapoints.s3-website.us-east-2.amazonaws.com',
                    'CustomOriginConfig': {
                        'HTTPPort': 80,
                        'HTTPSPort': 443,
                        'OriginProtocolPolicy': 'http-only'
                    }
                }
            ]
        },
        'DefaultCacheBehavior': {
            'TargetOriginId': 'S3-mypandapoints',
            'ViewerProtocolPolicy': 'redirect-to-https',
            'MinTTL': 0,
            'ForwardedValues': {
                'QueryString': False,
                'Cookies': {'Forward': 'none'}
            },
            'TrustedSigners': {
                'Enabled': False,
                'Quantity': 0
            }
        },
        'PriceClass': 'PriceClass_100'
    }
    
    try:
        response = cloudfront.create_distribution(DistributionConfig=distribution_config)
        distribution = response['Distribution']
        
        print(f"✅ CloudFront distribution created successfully!")
        print(f"Distribution ID: {distribution['Id']}")
        print(f"Domain Name: {distribution['DomainName']}")
        print(f"Status: {distribution['Status']}")
        
        print(f"\n📋 DNS Records to add in GoDaddy:")
        print(f"1. Delete existing A record for @")
        print(f"2. Add CNAME record:")
        print(f"   Type: CNAME")
        print(f"   Name: @")
        print(f"   Data: {distribution['DomainName']}")
        print(f"   TTL: 600 seconds")
        print(f"\n3. Update www CNAME record:")
        print(f"   Type: CNAME")
        print(f"   Name: www")
        print(f"   Data: {distribution['DomainName']}")
        print(f"   TTL: 600 seconds")
        
        print(f"\n⏳ Distribution is deploying... This takes 15-20 minutes.")
        print(f"You can check status at: https://console.aws.amazon.com/cloudfront/")
        
        return distribution['DomainName']
        
    except Exception as e:
        print(f"❌ Error creating CloudFront distribution: {e}")
        return None

if __name__ == "__main__":
    create_cloudfront_distribution()