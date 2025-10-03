import boto3
import json

def setup_dns():
    route53 = boto3.client('route53')
    
    # Create hosted zone for mypandapoints.com
    try:
        response = route53.create_hosted_zone(
            Name='mypandapoints.com',
            CallerReference=str(hash('mypandapoints.com')),
            HostedZoneConfig={
                'Comment': 'Hosted zone for Panda Points portal'
            }
        )
        
        hosted_zone_id = response['HostedZone']['Id'].split('/')[-1]
        print(f'Created hosted zone: {hosted_zone_id}')
        
        # Get CloudFront distribution domain
        cloudfront_domain = 'd1aormva1txfoz.cloudfront.net'
        
        # Create A record for root domain
        route53.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                'Changes': [{
                    'Action': 'CREATE',
                    'ResourceRecordSet': {
                        'Name': 'mypandapoints.com',
                        'Type': 'A',
                        'AliasTarget': {
                            'DNSName': cloudfront_domain,
                            'EvaluateTargetHealth': False,
                            'HostedZoneId': 'Z2FDTNDATAQYW2'  # CloudFront hosted zone ID
                        }
                    }
                }]
            }
        )
        
        # Create A record for www subdomain
        route53.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                'Changes': [{
                    'Action': 'CREATE',
                    'ResourceRecordSet': {
                        'Name': 'www.mypandapoints.com',
                        'Type': 'A',
                        'AliasTarget': {
                            'DNSName': cloudfront_domain,
                            'EvaluateTargetHealth': False,
                            'HostedZoneId': 'Z2FDTNDATAQYW2'  # CloudFront hosted zone ID
                        }
                    }
                }]
            }
        )
        
        # Get name servers
        ns_response = route53.get_hosted_zone(Id=hosted_zone_id)
        name_servers = ns_response['DelegationSet']['NameServers']
        
        print(f'DNS records created successfully!')
        print(f'Name servers for domain registrar:')
        for ns in name_servers:
            print(f'  {ns}')
            
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    setup_dns()