#!/usr/bin/env python3
import boto3
import os

def deploy_employee_page():
    """Deploy updated employee.html to S3 and invalidate CloudFront cache"""
    try:
        # Initialize S3 client
        s3 = boto3.client('s3')
        
        print("📦 Deploying employee.html to S3...")
        
        # Upload the updated employee.html file
        with open('employee.html', 'rb') as file:
            s3.upload_fileobj(
                file,
                'www.pandaadmin.com',  # S3 bucket for pandaadmin.com
                'employee.html',
                ExtraArgs={'ContentType': 'text/html'}
            )
        
        print("✅ Successfully deployed updated employee.html to www.pandaadmin.com")
        
        # Invalidate CloudFront cache for immediate updates
        try:
            cloudfront = boto3.client('cloudfront')
            
            # Get the CloudFront distribution ID for www.pandaadmin.com
            distributions = cloudfront.list_distributions()
            
            distribution_id = None
            if 'DistributionList' in distributions and 'Items' in distributions['DistributionList']:
                for dist in distributions['DistributionList']['Items']:
                    if 'www.pandaadmin.com' in str(dist.get('Aliases', {}).get('Items', [])):
                        distribution_id = dist['Id']
                        break
            
            if distribution_id:
                print(f"🔄 Invalidating CloudFront cache for distribution {distribution_id}...")
                
                cloudfront.create_invalidation(
                    DistributionId=distribution_id,
                    InvalidationBatch={
                        'Paths': {
                            'Quantity': 1,
                            'Items': ['/employee.html']
                        },
                        'CallerReference': f'employee-html-{os.urandom(8).hex()}'
                    }
                )
                
                print("✅ CloudFront cache invalidated successfully")
            else:
                print("⚠️  CloudFront distribution not found - updates may take time to propagate")
                
        except Exception as e:
            print(f"⚠️  CloudFront invalidation error: {e}")
            print("The file was uploaded successfully, but cache may need manual invalidation")
        
        print("\n🎉 Deployment complete!")
        print("🌐 https://www.pandaadmin.com/employee.html")
        
    except FileNotFoundError:
        print("❌ Error: employee.html not found in current directory")
    except Exception as e:
        print(f"❌ Error deploying employee page: {str(e)}")

if __name__ == "__main__":
    deploy_employee_page()
