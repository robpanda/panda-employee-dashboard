# Referral System Frontend - Deployment Guide

## 📱 What's Been Created

### Frontend Files
```
src/
├── pages/
│   └── leads-referrals.html   (Main UI - Complete referral management)
├── js/
│   ├── referral-api.js        (API wrapper for backend calls)
│   └── referral-app.js        (Main application logic & UI)
└── manifest.json               (PWA manifest for mobile installation)
```

### Features Included

✅ **Dashboard**
- Total advocates, leads, earnings stats
- Top performing advocates
- Recent leads activity
- Lead status breakdown

✅ **Advocates Management**
- Full list with search/filter
- Referral code display & copy
- Earnings tracking
- Detailed advocate view with:
  - Contact information
  - Performance metrics
  - Lead history
  - Payout history
  - Unique referral link

✅ **Leads Tracking**
- Complete lead list
- Search by name, email, phone
- Filter by status & advocate
- Lead detail modal
- Status update (triggers automatic payouts)
- Contact information display

✅ **Payouts Management**
- All payouts list
- Filter by status (pending/paid)
- Filter by type (signup/$25, qualified/$50, sold/$150)
- Mark as paid functionality
- Export to CSV

✅ **Mobile PWA**
- Progressive Web App manifest
- Installable on iOS/Android
- App-like experience
- Shortcuts to main sections

---

## 🚀 Quick Deploy to S3

### Option 1: Deploy to Existing Riley Dashboard

```bash
# Copy frontend files to Riley dashboard
cd /Users/robwinters/Documents/GitHub/panda-employee-dashboard

# Deploy to S3
aws s3 cp src/pages/leads-referrals.html s3://riley-dashboard-prod/leads.html --region us-east-2
aws s3 cp src/js/referral-api.js s3://riley-dashboard-prod/js/ --region us-east-2
aws s3 cp src/js/referral-app.js s3://riley-dashboard-prod/js/ --region us-east-2
aws s3 cp src/manifest.json s3://riley-dashboard-prod/ --region us-east-2

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/leads.html" "/js/*" "/manifest.json"
```

### Option 2: Deploy to pandaadmin.com

If using a different hosting setup:

```bash
# Upload to your web server
scp src/pages/leads-referrals.html user@pandaadmin.com:/var/www/html/leads.html
scp src/js/referral-*.js user@pandaadmin.com:/var/www/html/js/
scp src/manifest.json user@pandaadmin.com:/var/www/html/
```

### Option 3: Test Locally First

```bash
# Simple HTTP server for testing
cd src/pages
python3 -m http.server 8000

# Then open: http://localhost:8000/leads-referrals.html
```

---

## 🔧 Configuration

### Update API Endpoint (if needed)

If your API endpoint changes, edit `src/js/referral-api.js`:

```javascript
const REFERRAL_API_BASE = 'https://YOUR-API-GATEWAY-URL/prod/referrals';
```

Current endpoint:
```
https://7paaginnvg.execute-api.us-east-2.amazonaws.com/prod/referrals
```

### Logo and Branding

Update the logo path in `leads-referrals.html`:

```html
<img src="/panda-logo.png" alt="Panda Exteriors" height="40">
```

---

## 📱 Installing as Mobile App

### iOS (iPhone/iPad)

1. Open https://pandaadmin.com/leads in Safari
2. Tap the Share button (square with arrow)
3. Scroll down and tap "Add to Home Screen"
4. Name it "Panda Referrals"
5. Tap "Add"

The app will now appear on your home screen like a native app!

### Android

1. Open https://pandaadmin.com/leads in Chrome
2. Tap the three-dot menu
3. Tap "Add to Home screen"
4. Name it "Panda Referrals"
5. Tap "Add"

Or Chrome will automatically show an "Install" banner.

---

## 🎨 Customization

### Colors

Update the theme in `leads-referrals.html`:

```css
.header {
    background: linear-gradient(135deg, #2c5530 0%, #1a3d1f 100%);
}

.btn-panda {
    background: #2c5530;
}
```

### Navigation

Update navigation links in the utility nav:

```html
<a href="/employee.html" class="nav-link">👥 Employees</a>
<a href="/points.html" class="nav-link">⭐ Points</a>
```

---

## 🧪 Testing Checklist

After deployment, test these features:

### Dashboard
- [ ] Stats load correctly
- [ ] Top advocates display
- [ ] Recent leads display
- [ ] Numbers match API data

### Advocates
- [ ] List loads all advocates
- [ ] Search works
- [ ] Filters work (rep, status)
- [ ] Click advocate opens detail modal
- [ ] Referral link copy works
- [ ] Modal shows leads & payouts

### Leads
- [ ] List loads all leads
- [ ] Search works
- [ ] Filters work (status, advocate)
- [ ] Click lead opens detail modal
- [ ] Status update works
- [ ] Payouts auto-create on status change

### Payouts
- [ ] List loads all payouts
- [ ] Filters work (status, type)
- [ ] Mark as paid works
- [ ] CSV export works
- [ ] Earnings update on advocate

### Mobile
- [ ] Responsive on phone
- [ ] PWA install works
- [ ] App shortcuts work
- [ ] Looks good on iOS & Android

---

## 🔐 Authentication (TODO)

Currently, the API is public. To add authentication:

### Option 1: Add to Existing Auth

If pandaadmin.com has authentication:

```javascript
// In referral-api.js, add auth header
static async fetch(endpoint, options = {}) {
    const token = sessionStorage.getItem('pandaAdmin');

    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`  // Add this
        }
    };
    // ... rest of code
}
```

### Option 2: Add Cognito to API Gateway

Configure AWS Cognito authorizer on the API Gateway:

```bash
aws apigateway update-method \
  --rest-api-id 7paaginnvg \
  --resource-id RESOURCE_ID \
  --http-method ANY \
  --patch-operations op=replace,path=/authorizationType,value=COGNITO_USER_POOLS
```

---

## 📊 Future Enhancements

### Phase 2 Features
- [ ] Add new advocate form (currently placeholder)
- [ ] Add new lead form (currently placeholder)
- [ ] Email notifications on status changes
- [ ] SMS notifications to advocates
- [ ] Advanced analytics & charts
- [ ] Bulk import/export
- [ ] Automated payout processing
- [ ] Custom payout amounts
- [ ] Notes/comments on leads
- [ ] Document uploads
- [ ] Calendar integration
- [ ] Performance reports

### Integration Ideas
- [ ] Integrate with Riley Chat for notifications
- [ ] Send SMS via Twilio when leads added
- [ ] Sync with Salesforce
- [ ] Email campaigns to advocates
- [ ] Automated follow-up sequences

---

## 🐛 Troubleshooting

### Data Not Loading

1. Check browser console for errors
2. Verify API endpoint is correct
3. Test API directly:
   ```bash
   curl https://7paaginnvg.execute-api.us-east-2.amazonaws.com/prod/referrals/stats
   ```
4. Check CORS headers

### PWA Not Installing

1. Must be served over HTTPS
2. Manifest must be valid JSON
3. Icons must exist (can use placeholder)
4. Service worker needed for full offline support

### Filters Not Working

1. Check JavaScript console
2. Verify data is loaded
3. Check filter IDs match HTML

---

## 📞 Quick Reference

### URLs
- **Frontend**: https://pandaadmin.com/leads
- **API**: https://7paaginnvg.execute-api.us-east-2.amazonaws.com/prod/referrals
- **Docs**: See REFERRAL-SYSTEM-COMPLETE.md

### Files to Deploy
```
leads.html          → Main page
js/referral-api.js  → API wrapper
js/referral-app.js  → App logic
manifest.json       → PWA config
```

### Test Commands
```bash
# Test API
curl https://7paaginnvg.execute-api.us-east-2.amazonaws.com/prod/referrals/stats | jq

# Validate manifest
npx pwa-asset-generator validate manifest.json

# Test mobile
# Use Chrome DevTools → Device Toolbar
```

---

## ✅ Deployment Checklist

- [ ] Update API endpoint if needed
- [ ] Update logo path
- [ ] Test locally first
- [ ] Deploy HTML file
- [ ] Deploy JavaScript files
- [ ] Deploy manifest
- [ ] Test on desktop browser
- [ ] Test on mobile browser
- [ ] Test PWA installation
- [ ] Verify all features work
- [ ] Check authentication
- [ ] Train users

---

**Status**: Frontend complete and ready to deploy!
**Time to Deploy**: 5-10 minutes
**Next**: Upload files and test!

