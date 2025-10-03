import boto3
import json

def update_cloudfront_origin():
    cloudfront = boto3.client('cloudfront')
    
    # Get current distribution config
    distribution_id = 'E3SCE3WCVEG662'
    response = cloudfront.get_distribution_config(Id=distribution_id)
    
    config = response['DistributionConfig']
    etag = response['ETag']
    
    # Update origin to point to correct S3 bucket
    old_origin_id = config['Origins']['Items'][0]['Id']
    new_origin_id = 'S3-panda-portal-frontend-us-east-2'
    
    config['Origins']['Items'][0]['DomainName'] = 'panda-portal-frontend-us-east-2.s3-website.us-east-2.amazonaws.com'
    config['Origins']['Items'][0]['Id'] = new_origin_id
    
    # Update default cache behavior to reference new origin
    config['DefaultCacheBehavior']['TargetOriginId'] = new_origin_id
    
    # Update any additional cache behaviors
    if 'CacheBehaviors' in config and config['CacheBehaviors']['Quantity'] > 0:
        for behavior in config['CacheBehaviors']['Items']:
            if behavior['TargetOriginId'] == old_origin_id:
                behavior['TargetOriginId'] = new_origin_id
    
    # Update distribution
    cloudfront.update_distribution(
        Id=distribution_id,
        DistributionConfig=config,
        IfMatch=etag
    )
    
    print(f'CloudFront distribution {distribution_id} updated to point to www.pandaadmin.com bucket')

if __name__ == '__main__':
    update_cloudfront_origin()