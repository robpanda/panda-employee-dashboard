import boto3

def request_ssl_certificate():
    acm = boto3.client('acm', region_name='us-east-1')  # Must be us-east-1 for CloudFront
    
    response = acm.request_certificate(
        DomainName='mypandapoints.com',
        SubjectAlternativeNames=['www.mypandapoints.com'],
        ValidationMethod='DNS'
    )
    
    certificate_arn = response['CertificateArn']
    print(f'Certificate requested: {certificate_arn}')
    
    # Get validation records
    import time
    time.sleep(5)  # Wait for certificate to be processed
    
    cert_details = acm.describe_certificate(CertificateArn=certificate_arn)
    
    if 'DomainValidationOptions' in cert_details['Certificate']:
        print('\nDNS validation records needed:')
        for domain_validation in cert_details['Certificate']['DomainValidationOptions']:
            if 'ResourceRecord' in domain_validation:
                record = domain_validation['ResourceRecord']
                print(f'Domain: {domain_validation["DomainName"]}')
                print(f'Name: {record["Name"]}')
                print(f'Value: {record["Value"]}')
                print(f'Type: {record["Type"]}')
                print('---')
    
    return certificate_arn

if __name__ == '__main__':
    request_ssl_certificate()