# Deployment Guide

## Domain Setup Options

### Option 1: Custom Domain (Recommended)
1. **Purchase Domain**: Buy a domain like `pandaexteriors-portal.com`
2. **AWS CloudFront**: Set up distribution for global CDN
3. **Route 53**: Configure DNS routing
4. **SSL Certificate**: Use AWS Certificate Manager

### Option 2: Subdomain
- Use existing domain: `portal.pandaexteriors.com`
- Point CNAME to S3 bucket or CloudFront

### Option 3: Current S3 Setup
- Continue using: `panda-exteriors-map-bucket.s3.amazonaws.com`
- Update paths in config/domain.js

## File Structure

```
public/                 # Landing page
├── index.html         # Main portal entry

src/
├── pages/             # Individual application pages
│   ├── dashboard.html # Employee management
│   └── leads.html     # Lead management
├── assets/
│   ├── css/          # Stylesheets
│   ├── js/           # JavaScript modules
│   └── images/       # Static assets
└── components/       # Reusable components

config/
└── domain.js         # Domain configuration

backend/
├── lambda_function.py # AWS Lambda API
└── undo_import.py    # Utility scripts
```

## Deployment Commands

### S3 Deployment
```bash
# Deploy entire site
aws s3 sync public/ s3://your-bucket/
aws s3 sync src/ s3://your-bucket/src/

# Deploy specific pages
aws s3 cp public/index.html s3://your-bucket/index.html
aws s3 cp src/pages/dashboard.html s3://your-bucket/dashboard/
```

### CloudFront Invalidation
```bash
aws cloudfront create-invalidation --distribution-id YOUR_ID --paths "/*"
```

## URL Structure

- **Portal Home**: `https://your-domain.com/`
- **Employee Dashboard**: `https://your-domain.com/dashboard/`
- **Lead Management**: `https://your-domain.com/leads/`
- **API Endpoints**: `https://api.your-domain.com/`