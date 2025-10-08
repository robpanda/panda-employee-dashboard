# Staging Environment Setup

## Staging URLs
- **Admin Staging**: http://staging.pandaadmin.com.s3-website.us-east-2.amazonaws.com
- **Portal Staging**: http://staging.mypandapoints.com.s3-website.us-east-2.amazonaws.com

## Deployment Workflow

### 1. Deploy to Staging
```bash
# Deploy admin site to staging
python3 deploy-to-staging.py deploy admin

# Deploy portal site to staging  
python3 deploy-to-staging.py deploy portal
```

### 2. Test in Staging
- Test all functionality on staging URLs
- Verify API integrations work correctly
- Check responsive design and user flows

### 3. Promote to Production
```bash
# Promote admin staging to production
python3 deploy-to-staging.py promote admin

# Promote portal staging to production
python3 deploy-to-staging.py promote portal
```

## S3 Bucket Structure
- **staging.pandaadmin.com** → Admin staging environment
- **staging.mypandapoints.com** → Portal staging environment
- **www.pandaadmin.com** → Admin production
- **panda-portal-frontend-us-east-2** → Portal production

## Benefits
- Safe testing before production deployment
- Rollback capability if issues found
- Isolated environment for development
- Same Lambda functions work with both staging and production