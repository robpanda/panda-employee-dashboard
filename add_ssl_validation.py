import boto3

def add_ssl_validation_records():
    route53 = boto3.client('route53')
    
    hosted_zone_id = 'Z0594005ILLG803LMSY7'
    
    # Add validation records
    route53.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch={
            'Changes': [
                {
                    'Action': 'CREATE',
                    'ResourceRecordSet': {
                        'Name': '_1cab28db2b0da4df44791ee5e2b1e935.mypandapoints.com.',
                        'Type': 'CNAME',
                        'TTL': 300,
                        'ResourceRecords': [{'Value': '_c2513790e5564204d37aa68d4206c7e6.xlfgrmvvlj.acm-validations.aws.'}]
                    }
                },
                {
                    'Action': 'CREATE',
                    'ResourceRecordSet': {
                        'Name': '_bea963deb071176237acf60eaf0b2d2d.www.mypandapoints.com.',
                        'Type': 'CNAME',
                        'TTL': 300,
                        'ResourceRecords': [{'Value': '_e5cd861c2547c74e2a2a52a9222cb63d.xlfgrmvvlj.acm-validations.aws.'}]
                    }
                }
            ]
        }
    )
    
    print('SSL validation records added to Route 53')

if __name__ == '__main__':
    add_ssl_validation_records()