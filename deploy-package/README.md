# 🐼 Panda CRM Deployment Package

Complete deployment package for the Panda CRM system with DynamoDB, Lambda, and API Gateway.

## 🚀 Quick Deploy

```bash
cd deploy-package
chmod +x *.sh
./deploy.sh
```

## 📋 What Gets Deployed

- **DynamoDB Tables**: contacts, collections, config, employees
- **Lambda Function**: CRM API with all endpoints
- **API Gateway**: RESTful API with CORS enabled
- **IAM Roles**: Proper permissions for Lambda to access DynamoDB

## 🛠️ Manual Steps

### 1. Deploy Infrastructure
```bash
./deploy.sh
```

### 2. Update Frontend
```bash
./update-frontend.sh
```

### 3. Test System
Open your leads page and test:
- Contact management
- Collections import
- Configuration settings

## 📁 Package Contents

```
deploy-package/
├── template.yaml          # CloudFormation SAM template
├── samconfig.toml         # SAM configuration
├── deploy.sh             # Automated deployment
├── update-frontend.sh    # Frontend API URL updater
├── src/
│   └── lambda_function.py # Updated Lambda with CRM endpoints
└── README.md            # This file
```

## 🔧 Requirements

- AWS CLI configured
- SAM CLI (auto-installed if missing)
- Proper AWS permissions for CloudFormation, Lambda, DynamoDB, API Gateway

## 🎯 Endpoints Created

- `GET/POST /contacts` - Contact management
- `GET/POST /collections` - Collections with stage tracking
- `GET/POST /config` - System configuration
- `GET/POST /employees` - Existing employee management

## 🔍 Troubleshooting

**Deployment fails**: Check AWS credentials and permissions
**API not working**: Run `./update-frontend.sh` to fix URLs
**CORS errors**: API Gateway CORS is pre-configured

## 🎉 Success!

After deployment, your CRM system will be live with:
- Real DynamoDB storage
- Scalable serverless architecture
- Professional API endpoints
- Full CRUD operations

Your 109 contacts will now save permanently!