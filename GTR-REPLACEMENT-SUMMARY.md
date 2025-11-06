# GTR Replacement System - Deployment Summary

## Overview
Complete referral management system to replace Get The Referral (GTR) service, built on AWS serverless architecture.

## ✅ Completed Components

### 1. Database Infrastructure (DynamoDB)
All tables created in `us-east-2` region:

- **panda-sales-managers** - Sales managers who oversee reps
- **panda-sales-reps** - Sales reps who manage advocates
- **panda-advocates** - Advocates who refer leads
- **panda-referral-leads** - Leads/referrals from advocates
- **panda-referral-payouts** - Payout tracking system

**Created with**: `scripts/create-referral-tables.sh`

### 2. Data Migration
Successfully imported existing GTR data:
- ✅ 50 Advocates imported
- ✅ 12 Sales Reps imported
- ✅ 50 Leads imported
- ✅ 39 Payout records created

**Import script**: `scripts/import-gtr-data.py`

### 3. Backend API (Lambda)
Lambda function created: `panda-referral-system-api`
- Runtime: Node.js 18.x
- Region: us-east-2
- Handler: index.handler
- IAM Role: lambda-dynamodb-role (full DynamoDB access)

**Code location**: `lambda/referral-system/index.js`

### 4. API Gateway Integration
Endpoint: `https://7paaginnvg.execute-api.us-east-2.amazonaws.com/prod/referral`

**Available Routes**:
```
GET  /referral/advocates        - List all advocates
GET  /referral/advocates?repId=123 - Filter by sales rep
GET  /referral/leads             - List all leads
GET  /referral/leads?advocateId=456 - Filter by advocate
GET  /referral/payouts           - List payouts
GET  /referral/reps              - List sales reps
GET  /referral/stats             - System statistics
GET  /referral/dashboard         - Full dashboard data
```

## 🎯 Payout Structure
- **$25** - Advocate signup bonus
- **$50** - Qualified lead (good referral)
- **$150** - Deal closed (sold)

## Hierarchy Structure
```
Sales Manager
  └─ Sales Rep
      └─ Advocate
          └─ Leads/Referrals
```

## 🔧 Pending Tasks

### Lambda Dependency Issue
The Lambda function needs AWS SDK v3 dependencies installed. Due to npm cache permission issues, this needs to be resolved:

**Option 1 - Fix npm cache** (Recommended):
```bash
sudo chown -R $(whoami):staff ~/.npm
cd /Users/robwinters/Documents/GitHub/panda-employee-dashboard/lambda/referral-system
npm install
./deploy-referral-lambda.sh
```

**Option 2 - Use Docker**:
```bash
cd lambda/referral-system
docker run --rm -v "$PWD":/var/task amazon/aws-lambda-nodejs:18 npm install
zip -r function.zip index.js package.json node_modules
aws lambda update-function-code --function-name panda-referral-system-api \
  --zip-file fileb://function.zip --region us-east-2
```

**Option 3 - Use Layers**:
Create a Lambda Layer with AWS SDK v3 and attach it to the function.

### Frontend Development
Need to create the UI at `https://pandaadmin.com/leads` (no .html extension)

**Features to include**:
1. **Dashboard**
   - Total advocates, leads, conversions
   - Payout summary (pending vs paid)
   - Lead status breakdown

2. **Advocate Management**
   - List all advocates with search/filter
   - View individual advocate details
   - Unique referral link for each advocate
   - Earnings breakdown

3. **Lead Management**
   - Lead status tracking (new → contacted → qualified → working → sold/lost)
   - Status update triggers automatic payouts
   - Lead assignment to advocates

4. **Payout Management**
   - Pending payouts list
   - Mark payouts as paid
   - Payout history
   - Export capability

5. **Mobile PWA**
   - Progressive Web App manifest
   - Installable on iOS/Android home screen
   - Offline capability
   - Push notifications for new leads

## 📊 Data Structure Examples

### Advocate Record
```json
{
  "advocateId": "542010",
  "repId": "563935",
  "email": "advocate@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "referralCode": "ABC123",
  "referralUrl": "https://pandaadmin.com/refer/ABC123",
  "totalEarnings": 225.00,
  "pendingEarnings": 50.00,
  "paidEarnings": 175.00,
  "totalLeads": 5,
  "totalConversions": 1,
  "active": true
}
```

### Lead Record
```json
{
  "leadId": "654459",
  "advocateId": "542010",
  "repId": "563935",
  "status": "qualified",
  "firstName": "Jane",
  "lastName": "Customer",
  "email": "customer@example.com",
  "phone": "(555) 123-4567",
  "address": {
    "street1": "123 Main St",
    "city": "Baltimore",
    "state": "MD",
    "zip": "21201"
  },
  "product": "Roofing Referral",
  "createdAt": 1730937600000,
  "source": "GTR_IMPORT"
}
```

### Payout Record
```json
{
  "payoutId": "PAY1730937600_qualified",
  "leadId": "654459",
  "advocateId": "542010",
  "amount": 50.00,
  "type": "qualified",
  "status": "pending",
  "createdAt": 1730937600000,
  "notes": "Qualified lead payout"
}
```

## 🚀 Quick Start (Once Dependencies Fixed)

1. **Test the API**:
```bash
# Get stats
curl https://7paaginnvg.execute-api.us-east-2.amazonaws.com/prod/referral/stats

# Get all advocates
curl https://7paaginnvg.execute-api.us-east-2.amazonaws.com/prod/referral/advocates

# Get leads for specific advocate
curl "https://7paaginnvg.execute-api.us-east-2.amazonaws.com/prod/referral/leads?advocateId=542010"
```

2. **Deploy Frontend**:
```bash
cd src
# Upload to S3 or deploy via Amplify
aws s3 sync . s3://riley-dashboard-prod/leads/
```

3. **Monitor**:
```bash
# View Lambda logs
aws logs tail /aws/lambda/panda-referral-system-api --region us-east-2 --follow

# Check DynamoDB tables
aws dynamodb scan --table-name panda-advocates --region us-east-2 --max-items 5
```

## 📱 Frontend Implementation Plan

### Technology Stack Recommendation:
- **Framework**: React or Vue.js (or vanilla JS for simplicity)
- **UI Library**: Bootstrap 5 (already used in existing pandaadmin.com)
- **Charts**: Chart.js (already used in leads.html)
- **State Management**: Local storage + API calls
- **PWA**: Service worker + manifest.json

### File Structure:
```
src/pages/leads/
  ├── index.html (main page)
  ├── dashboard.html
  ├── advocates.html
  ├── leads.html
  ├── payouts.html
  ├── js/
  │   ├── api.js (API wrapper)
  │   ├── dashboard.js
  │   ├── advocates.js
  │   ├── leads.js
  │   └── payouts.js
  ├── css/
  │   └── referral-system.css
  └── manifest.json (PWA)
```

## 🔐 Security Considerations

1. **Authentication**: Add Cognito or existing auth to API Gateway
2. **Authorization**: Role-based access (Manager > Rep > Advocate views)
3. **Data Validation**: Input sanitization on frontend and backend
4. **Rate Limiting**: API Gateway throttling configured
5. **CORS**: Already configured for cross-origin requests

## 📈 Next Steps

1. **Immediate**: Fix Lambda dependencies and test API endpoints
2. **Short-term**: Build frontend interface
3. **Medium-term**: Add advanced features:
   - Email notifications on lead status changes
   - SMS notifications for advocates
   - Automated payout processing
   - Analytics and reporting
4. **Long-term**: Mobile native apps (iOS/Android)

## 💾 Backup & Recovery

### Backup GTR Data (before switching):
```bash
python3 scripts/import-gtr-data.py > gtr_backup_$(date +%Y%m%d).log
```

### Export DynamoDB Data:
```bash
aws dynamodb scan --table-name panda-advocates --region us-east-2 > advocates_backup.json
aws dynamodb scan --table-name panda-referral-leads --region us-east-2 > leads_backup.json
```

## 📞 Support

- **Lambda Logs**: CloudWatch `/aws/lambda/panda-referral-system-api`
- **DynamoDB Console**: https://console.aws.amazon.com/dynamodbv2
- **API Gateway Console**: https://console.aws.amazon.com/apigateway

## 🎉 Success Metrics

When fully deployed, track:
- Advocate signup rate
- Lead conversion rate (new → qualified → sold)
- Average payout per advocate
- System uptime
- API response times
- Cost savings vs GTR subscription

---

**Status**: Backend infrastructure complete, awaiting Lambda dependency resolution and frontend development.

**Estimated Completion**: 2-4 hours for frontend + PWA implementation
