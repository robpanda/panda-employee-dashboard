import boto3

def add_cloudfront_aliases():
    cloudfront = boto3.client('cloudfront')
    
    distribution_id = 'E3SCE3WCVEG662'
    response = cloudfront.get_distribution_config(Id=distribution_id)
    
    config = response['DistributionConfig']
    etag = response['ETag']
    
    # Add domain aliases and SSL certificate
    config['Aliases'] = {
        'Quantity': 2,
        'Items': ['mypandapoints.com', 'www.mypandapoints.com']
    }
    
    # Add SSL certificate
    config['ViewerCertificate'] = {
        'ACMCertificateArn': 'arn:aws:acm:us-east-1:679128292059:certificate/d65782ab-1abe-4725-8031-3e78cf69f576',
        'SSLSupportMethod': 'sni-only',
        'MinimumProtocolVersion': 'TLSv1.2_2021'
    }
    
    # Update distribution
    cloudfront.update_distribution(
        Id=distribution_id,
        DistributionConfig=config,
        IfMatch=etag
    )
    
    print(f'Added domain aliases to CloudFront distribution {distribution_id}')

if __name__ == '__main__':
    add_cloudfront_aliases()