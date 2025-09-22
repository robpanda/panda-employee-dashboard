# Deployment Instructions

## GitHub Setup

1. Create a new repository on GitHub named `panda-employee-dashboard`
2. Run these commands to push the code:

```bash
cd /Users/robwinters/panda-employee-dashboard
git remote add origin https://github.com/YOUR_USERNAME/panda-employee-dashboard.git
git branch -M main
git push -u origin main
```

## AWS Deployment

### S3 Hosting
```bash
aws s3 cp index.html s3://panda-exteriors-map-bucket/leads/employee_dashboard.html --content-type "text/html"
```

### Lambda Function
```bash
cd /Users/robwinters/panda-employee-dashboard
zip lambda_function.zip lambda_function.py
aws lambda update-function-code --function-name employee-management --zip-file fileb://lambda_function.zip
```

## Current Live URLs

- **Dashboard**: https://panda-exteriors-map-bucket.s3.amazonaws.com/leads/employee_dashboard.html
- **API**: https://w40mq6ab11.execute-api.us-east-2.amazonaws.com/prod/employees
- **Google Sheets**: https://docs.google.com/spreadsheets/d/1vO-94iEtB8FAthneJ8Cx1Cm-iA-oHJiBwOPAGmsiM-4/edit

## Features Included

✅ Smart CSV/Excel Import  
✅ Duplicate Detection (Email → Name → Full Name)  
✅ Employee Profile Editing  
✅ Merchandise Tracking  
✅ Termination Management  
✅ Backup/Undo Functionality  
✅ Lead Management Integration  
✅ Google Sheets Integration