import boto3
import os

def deploy_points_page():
    try:
        # Initialize S3 client
        s3 = boto3.client('s3')
        
        # Upload the updated points.html file
        with open('points.html', 'rb') as file:
            s3.upload_fileobj(
                file,
                'www.pandaadmin.com',  # S3 bucket for pandaadmin.com
                'points.html',
                ExtraArgs={'ContentType': 'text/html'}
            )
        
        print("✅ Successfully deployed updated points.html to pandaadmin.com")
        
        # Invalidate CloudFront cache if needed
        try:
            cloudfront = boto3.client('cloudfront')
            # You may need to add the CloudFront distribution ID here
            print("Note: You may need to invalidate CloudFront cache for immediate updates")
        except Exception as e:
            print(f"CloudFront invalidation not configured: {e}")
        
    except Exception as e:
        print(f"❌ Error deploying points page: {str(e)}")

if __name__ == "__main__":
    deploy_points_page()