# Deploy Employee Portal to mypandapoints.com

## Files to Upload to S3 Bucket

The following files need to be uploaded to the mypandapoints.com S3 bucket:

### Required Files:
1. `employee-portal/index.html` → Upload as `index.html` (root)
2. `employee-portal/dashboard.html` → Upload as `dashboard.html`

### AWS CLI Commands:

```bash
# Upload index.html (login page)
aws s3 cp employee-portal/index.html s3://mypandapoints.com/index.html --content-type "text/html"

# Upload dashboard.html
aws s3 cp employee-portal/dashboard.html s3://mypandapoints.com/dashboard.html --content-type "text/html"

# Set cache control headers
aws s3 cp employee-portal/index.html s3://mypandapoints.com/index.html --content-type "text/html" --cache-control "no-cache, no-store, must-revalidate"
aws s3 cp employee-portal/dashboard.html s3://mypandapoints.com/dashboard.html --content-type "text/html" --cache-control "no-cache, no-store, must-revalidate"
```

### Manual Upload via AWS Console:
1. Go to AWS S3 Console
2. Find the mypandapoints.com bucket
3. Upload `employee-portal/index.html` as `index.html`
4. Upload `employee-portal/dashboard.html` as `dashboard.html`
5. Set both files to public read access
6. Set cache control headers to prevent caching

### Features Included:
- ✅ Promotional banner for new referral program
- ✅ Employee login with proper authentication
- ✅ Points balance display
- ✅ Gift card redemption functionality
- ✅ Shopify integration for gift cards
- ✅ Responsive design
- ✅ Session management
- ✅ Error handling

### API Integration:
- Uses same Lambda API: `https://dfu3zr3dnrvgiiwa2yu77cz5fq0rqmth.lambda-url.us-east-2.on.aws`
- Employee login endpoint: `/employee-login`
- Gift card redemption: `/gift-cards`

### Test Credentials:
Use any employee email/password from the database to test the portal.