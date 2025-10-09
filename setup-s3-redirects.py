import boto3
import json

def setup_s3_redirects():
    s3 = boto3.client('s3', region_name='us-east-1')
    bucket_name = 'www.pandaadmin.com'
    
    # Website configuration with redirect rules
    website_config = {
        'IndexDocument': {'Suffix': 'index.html'},
        'ErrorDocument': {'Key': 'error.html'},
        'RoutingRules': [
            {
                'Condition': {
                    'KeyPrefixEquals': 'employee'
                },
                'Redirect': {
                    'ReplaceKeyWith': 'employee.html'
                }
            },
            {
                'Condition': {
                    'KeyPrefixEquals': 'admin'
                },
                'Redirect': {
                    'ReplaceKeyWith': 'admin.html'
                }
            },
            {
                'Condition': {
                    'KeyPrefixEquals': 'points'
                },
                'Redirect': {
                    'ReplaceKeyWith': 'points.html'
                }
            },
            {
                'Condition': {
                    'KeyPrefixEquals': 'referrals'
                },
                'Redirect': {
                    'ReplaceKeyWith': 'referrals.html'
                }
            },
            {
                'Condition': {
                    'KeyPrefixEquals': 'login'
                },
                'Redirect': {
                    'ReplaceKeyWith': 'login.html'
                }
            }
        ]
    }
    
    try:
        s3.put_bucket_website(
            Bucket=bucket_name,
            WebsiteConfiguration=website_config
        )
        print("✅ Successfully configured S3 redirects for pandaadmin.com")
        print("   /employee → /employee.html")
        print("   /admin → /admin.html") 
        print("   /points → /points.html")
        print("   /referrals → /referrals.html")
        print("   /login → /login.html")
        
    except Exception as e:
        print(f"❌ Error setting up redirects: {str(e)}")

if __name__ == "__main__":
    setup_s3_redirects()