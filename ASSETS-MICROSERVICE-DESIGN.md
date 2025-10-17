# Asset Management Microservice Design

## Architecture Decision: Separate Microservice ✅

### Why Microservice?
1. **Focused Responsibility** - Asset lifecycle management is distinct from employee CRUD
2. **Resource Isolation** - PDF generation doesn't impact employee API performance
3. **Independent Scaling** - Can scale asset API separately for high-volume periods
4. **Cleaner Codebase** - Each service stays maintainable (~500-1000 lines)
5. **Technology Flexibility** - Can use different PDF libraries, storage, etc.
6. **Deployment Independence** - Update asset workflow without employee API changes

## Service Structure

### panda-assets-api (New Lambda Function)
```
lambda_assets.py
├── Asset Request Management
├── Approval Workflow
├── PDF Generation
├── Signature Handling
└── Inventory Tracking
```

**Runtime**: Python 3.9  
**Dependencies**: boto3, reportlab (PDF), pillow (images)  
**Memory**: 512 MB (for PDF generation)  
**Timeout**: 60 seconds

### Infrastructure

#### DynamoDB Table: `panda-assets`
```python
{
    'TableName': 'panda-assets',
    'KeySchema': [
        {'AttributeName': 'id', 'KeyType': 'HASH'}
    ],
    'AttributeDefinitions': [
        {'AttributeName': 'id', 'AttributeType': 'S'},
        {'AttributeName': 'status', 'AttributeType': 'S'},
        {'AttributeName': 'created_at', 'AttributeType': 'S'},
        {'AttributeName': 'employee_email', 'AttributeType': 'S'}
    ],
    'GlobalSecondaryIndexes': [
        {
            'IndexName': 'status-index',
            'KeySchema': [
                {'AttributeName': 'status', 'KeyType': 'HASH'},
                {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
            ]
        },
        {
            'IndexName': 'employee-index',
            'KeySchema': [
                {'AttributeName': 'employee_email', 'KeyType': 'HASH'},
                {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
            ]
        }
    ]
}
```

#### S3 Bucket: `panda-assets-docs`
- Stores generated PDFs
- Signed asset checkout forms
- Employee signatures
- Lifecycle policy: Retain 7 years

#### IAM Role: `panda-assets-lambda-role`
Permissions:
- DynamoDB: panda-assets (read/write)
- DynamoDB: panda-employees (read only - for lookups)
- S3: panda-assets-docs (read/write)
- SES: Send emails

## API Endpoints

### 1. POST /requests - Create Asset Request
```json
Request:
{
  "supervisor_name": "John Doe",
  "supervisor_email": "john@pandaexteriors.com",
  "employee_name": "Jane Smith",
  "employee_email": "jane@pandaexteriors.com",
  "start_date": "2024-10-20",
  "phone": "(555) 123-4567",
  "office_location": "Delaware",
  "equipment": [
    {"item": "Laptop", "quantity": 1, "value": 100},
    {"item": "iPad w/case and charger", "quantity": 1, "value": 100}
  ],
  "comments": "Rush - starts Monday"
}

Response:
{
  "success": true,
  "request_id": "req_abc123",
  "message": "Asset request created successfully"
}
```

### 2. GET /requests?status=pending&limit=50
```json
Response:
{
  "requests": [
    {
      "id": "req_abc123",
      "status": "pending",
      "employee_name": "Jane Smith",
      "employee_email": "jane@pandaexteriors.com",
      "total_value": 200,
      "created_at": "2024-10-17T10:00:00Z",
      "equipment_count": 2
    }
  ],
  "count": 1
}
```

### 3. PUT /requests/{id}/approve
```json
Request:
{
  "approved_by": "admin@pandaexteriors.com",
  "notes": "Approved for Q4 onboarding"
}

Response:
{
  "success": true,
  "message": "Request approved",
  "next_step": "generate_pdf"
}
```

### 4. POST /requests/{id}/pdf - Generate Signature PDF
```json
Response:
{
  "success": true,
  "pdf_url": "https://panda-assets-docs.s3.../req_abc123.pdf",
  "signature_link": "https://www.pandaadmin.com/sign-asset?token=xyz"
}
```

### 5. POST /requests/{id}/sign - Employee Signs
```json
Request:
{
  "signature_data": "data:image/png;base64,...",
  "employee_email": "jane@pandaexteriors.com"
}

Response:
{
  "success": true,
  "message": "Asset checkout complete",
  "status": "checked-out",
  "signed_pdf_url": "https://..."
}
```

## Data Flow

### New Request Flow
```
1. Supervisor fills form on assets.html
   ↓
2. POST /requests → panda-assets-api
   ↓
3. Create record in panda-assets (status: pending)
   ↓
4. Send email notification to admins
   ↓
5. Show in "New Requests" tab
```

### Approval Flow
```
1. Admin clicks "Approve" on assets.html
   ↓
2. PUT /requests/{id}/approve
   ↓
3. Update status to "approved"
   ↓
4. Move to "Approved" tab
   ↓
5. Show "Generate PDF" button
```

### PDF & Signature Flow
```
1. Admin clicks "Generate PDF"
   ↓
2. POST /requests/{id}/pdf
   ↓
3. Lambda generates PDF with ReportLab
   ↓
4. Upload to S3: panda-assets-docs
   ↓
5. Send signature link to employee email
   ↓
6. Employee opens link, signs
   ↓
7. POST /requests/{id}/sign
   ↓
8. Update status to "checked-out"
   ↓
9. Save signed PDF to S3
   ↓
10. Update employee record in panda-employees
   ↓
11. Show in "Checked Out" tab
```

## Integration with Employee API

### Read-Only Queries
```python
# Asset API queries Employee API to:
1. Validate employee email exists
2. Get employee_id for linking
3. Display employee info in PDFs
4. Check supervisor permissions
```

### Write Operations
```python
# After checkout, update employee record:
POST /employees/{id}/assets
{
  "asset_request_id": "req_abc123",
  "assets": ["Laptop", "iPad w/case"],
  "total_value": 200,
  "checkout_date": "2024-10-17"
}
```

## Frontend Changes

### assets.html
```javascript
// Dual API configuration
const EMPLOYEE_API = 'https://dfu3...lambda-url.../';
const ASSETS_API = 'https://xyz...assets-api.../';

// New Request Form
async function submitAssetRequest() {
  const response = await fetch(`${ASSETS_API}/requests`, {
    method: 'POST',
    body: JSON.stringify(formData)
  });
}

// Load requests by status
async function loadRequests(status) {
  const response = await fetch(`${ASSETS_API}/requests?status=${status}`);
  const data = await response.json();
  populateTable(data.requests);
}
```

## Deployment Strategy

### Step 1: Create Infrastructure
```bash
# Create DynamoDB table
aws dynamodb create-table ...

# Create S3 bucket
aws s3 mb s3://panda-assets-docs

# Create IAM role
aws iam create-role ...
```

### Step 2: Deploy Lambda
```bash
# Package with dependencies
pip install -r requirements.txt -t .
zip -r lambda_assets.zip .

# Deploy
aws lambda create-function \
  --function-name panda-assets-api \
  --runtime python3.9 \
  --handler lambda_assets.lambda_handler \
  --zip-file fileb://lambda_assets.zip \
  --memory-size 512 \
  --timeout 60
```

### Step 3: Create Function URL
```bash
aws lambda create-function-url-config \
  --function-name panda-assets-api \
  --auth-type NONE \
  --cors AllowOrigins=*,AllowMethods=GET,POST,PUT
```

### Step 4: Update Frontend
```bash
# Update assets.html with ASSETS_API URL
# Deploy to S3
python3 deploy-assets-page.py
```

## Benefits of This Approach

✅ **Modularity** - Each service has single responsibility  
✅ **Scalability** - Scale assets independently  
✅ **Maintainability** - Smaller, focused codebases  
✅ **Testability** - Easier to test in isolation  
✅ **Reliability** - Failure in assets doesn't affect employees  
✅ **Security** - Fine-grained IAM permissions per service  
✅ **Cost** - Pay only for what you use per service  

## Migration Path

1. ✅ Create `panda-assets-api` (new Lambda)
2. ✅ Create `panda-assets` table
3. ✅ Build asset endpoints
4. ✅ Update assets.html to use new API
5. ✅ Test workflow end-to-end
6. ✅ Deploy to production
7. ⏳ Monitor & iterate

## Next Steps

1. Create lambda_assets.py
2. Set up infrastructure
3. Build request form
4. Implement approval workflow
5. Add PDF generation
6. Deploy & test

