# Quick Fix & Deploy Guide

## The Issue
The Lambda function is created but needs AWS SDK v3 dependencies. Your npm cache has permission issues preventing installation.

## Quick Solutions

### Solution 1: Fix npm permissions (Recommended - 30 seconds)
```bash
# Fix npm cache permissions
sudo chown -R $(whoami):staff ~/.npm

# Install and deploy
cd /Users/robwinters/Documents/GitHub/panda-employee-dashboard/lambda/referral-system
npm install
bash ../../scripts/deploy-referral-lambda.sh
```

### Solution 2: Use temporary directory (If sudo not available)
```bash
# Create fresh temp directory
mkdir -p /tmp/lambda-deploy
cd /tmp/lambda-deploy

# Copy files
cp /Users/robwinters/Documents/GitHub/panda-employee-dashboard/lambda/referral-system/index.js .
cp /Users/robwinters/Documents/GitHub/panda-employee-dashboard/lambda/referral-system/package.json .

# Install with --prefer-offline to avoid cache
npm install --prefer-offline --no-save

# Deploy
zip -r function.zip index.js package.json node_modules
aws lambda update-function-code \
  --function-name panda-referral-system-api \
  --zip-file fileb://function.zip \
  --region us-east-2

# Wait and test
aws lambda wait function-updated --function-name panda-referral-system-api --region us-east-2
curl "https://7paaginnvg.execute-api.us-east-2.amazonaws.com/prod/referral/stats"
```

### Solution 3: Use Docker (Most reliable)
```bash
cd /Users/robwinters/Documents/GitHub/panda-employee-dashboard/lambda/referral-system

# Build with Docker
docker run --rm \
  -v "$PWD":/var/task \
  -w /var/task \
  public.ecr.aws/lambda/nodejs:18 \
  npm install --production

# Deploy
zip -r function.zip index.js package.json node_modules
aws lambda update-function-code \
  --function-name panda-referral-system-api \
  --zip-file fileb://function.zip \
  --region us-east-2
```

## Test After Deployment

```bash
# Test stats endpoint
curl -s "https://7paaginnvg.execute-api.us-east-2.amazonaws.com/prod/referral/stats" | jq

# Should return:
# {
#   "totalAdvocates": 50,
#   "activeAdvocates": 50,
#   "totalLeads": 50,
#   "leadsByStatus": { ... },
#   "totalPayouts": 1950.00,
#   "pendingPayouts": ...,
#   "paidPayouts": ...
# }

# Test advocates endpoint
curl -s "https://7paaginnvg.execute-api.us-east-2.amazonaws.com/prod/referral/advocates" | jq '.advocates | length'
# Should return: 50

# Test dashboard endpoint
curl -s "https://7paaginnvg.execute-api.us-east-2.amazonaws.com/prod/referral/dashboard" | jq '.stats'
```

## If All Else Fails: Manual AWS Console Upload

1. Go to: https://console.aws.amazon.com/lambda/home?region=us-east-2#/functions/panda-referral-system-api
2. Download pre-built package: https://npm.pkg.go.dev/@aws-sdk/client-dynamodb
3. Create zip with index.js + node_modules
4. Upload via Console "Upload from" → ".zip file"

## Next: Build the Frontend

Once the API is working, follow the guide in `GTR-REPLACEMENT-SUMMARY.md` to build the frontend interface.

Quick frontend test:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Referral System Test</title>
</head>
<body>
    <h1>Referral System</h1>
    <div id="stats"></div>
    <script>
        fetch('https://7paaginnvg.execute-api.us-east-2.amazonaws.com/prod/referral/stats')
            .then(r => r.json())
            .then(data => {
                document.getElementById('stats').innerHTML = `
                    <p>Total Advocates: ${data.totalAdvocates}</p>
                    <p>Total Leads: ${data.totalLeads}</p>
                    <p>Total Payouts: $${data.totalPayouts}</p>
                `;
            });
    </script>
</body>
</html>
```

Save as `test.html` and open in browser to verify API is working!
