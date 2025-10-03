#!/usr/bin/env python3
import boto3
import json
import time

def create_simple_cloudfront():
    cloudfront = boto3.client('cloudfront')
    
    distribution_config = {
        'CallerReference': f'mypandapoints-simple-{int(time.time())}',
        'DefaultRootObject': 'index.html',
        'Comment': 'Simple CloudFront for mypandapoints S3',
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
        
        print(f"✅ CloudFront distribution created!")
        print(f"Distribution ID: {distribution['Id']}")
        print(f"CloudFront Domain: {distribution['DomainName']}")
        
        print(f"\n📋 Update your GoDaddy DNS:")
        print(f"1. Change A record:")
        print(f"   Type: A")
        print(f"   Name: @")
        print(f"   Data: [Get IP from: dig {distribution['DomainName']}]")
        
        print(f"\n2. Change www CNAME:")
        print(f"   Type: CNAME")
        print(f"   Name: www")
        print(f"   Data: {distribution['DomainName']}")
        
        return distribution['DomainName']
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    create_simple_cloudfront()