#!/bin/bash

# Deploy to pandaadmin.com
BUCKET="pandaadmin-com"

echo "🚀 Deploying to pandaadmin.com..."

# Deploy files
aws s3 cp public/index.html "s3://$BUCKET/index.html" --content-type "text/html"
aws s3 cp src/pages/dashboard.html "s3://$BUCKET/dashboard.html" --content-type "text/html"
aws s3 cp src/pages/leads.html "s3://$BUCKET/leads.html" --content-type "text/html"
aws s3 sync src/assets/ "s3://$BUCKET/assets/"

# Configure website
aws s3 website "s3://$BUCKET" --index-document index.html

echo "✅ Deployed to https://pandaadmin.com"