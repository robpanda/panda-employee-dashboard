# Asset Management System Implementation Plan

## Overview
Build a complete asset management system matching the JotForm workflow, integrated with employee data.

## Components Needed

### 1. DynamoDB Table: `panda-assets`
```javascript
{
  "id": "asset-request-uuid",
  "type": "request", // or "checkout"
  "status": "pending" | "approved" | "rejected" | "checked-out" | "returned",
  "created_at": "2024-10-17T...",
  "updated_at": "2024-10-17T...",
  
  // Supervisor Info
  "supervisor_name": "John Doe",
  "supervisor_email": "john@pandaexteriors.com",
  
  // New Hire Info
  "employee_name": "Jane Smith",
  "employee_email": "jane@pandaexteriors.com",
  "employee_id": "10701", // link to panda-employees
  "start_date": "2024-10-20",
  "phone": "(555) 123-4567",
  "office_location": "Delaware",
  
  // Equipment
  "equipment": [
    {
      "item": "Complete Desktop Setup",
      "quantity": 1,
      "value": 100
    },
    {
      "item": "Laptop",
      "quantity": 1,
      "value": 100
    }
  ],
  "total_value": 200,
  "comments": "Urgent - start date is Monday",
  
  // Approval workflow
  "approved_by": "admin@pandaexteriors.com",
  "approved_at": "2024-10-17T...",
  "rejected_reason": "",
  
  // PDF & Signature
  "pdf_url": "s3://bucket/signed-docs/asset-uuid.pdf",
  "signature_data": "base64...",
  "signed_at": "2024-10-17T...",
  "signed_by_employee": true
}
```

### 2. Lambda Endpoints (add to panda-employee-api)

#### POST `/asset-requests` - Create new request
```javascript
{
  supervisor_name, supervisor_email,
  employee_name, employee_email, start_date, phone, office_location,
  equipment: [{item, quantity}],
  comments
}
```

#### GET `/asset-requests` - Get all requests (with filters)
```javascript
?status=pending|approved|rejected|checked-out
?employee_email=...
```

#### PUT `/asset-requests/{id}/approve` - Approve request
```javascript
{
  approved_by: "admin@example.com"
}
```

#### PUT `/asset-requests/{id}/reject` - Reject request
```javascript
{
  rejected_by: "admin@example.com",
  reason: "..."
}
```

#### POST `/asset-requests/{id}/generate-pdf` - Generate signature PDF
Generates PDF with:
- Asset list
- Values
- Employee signature field
- Returns PDF URL

#### POST `/asset-requests/{id}/sign` - Sign document
```javascript
{
  signature_data: "base64...",
  employee_email: "..."
}
```
Updates status to "checked-out"

### 3. Frontend Updates (assets.html)

#### New Request Form (modal)
- Matches JotForm exactly
- All fields with validation
- Dynamic equipment selection with quantities
- Auto-calculate total value

#### New Requests Tab
- Shows pending requests
- Approve/Reject buttons
- View details modal

#### Approved Tab
- Shows approved requests
- "Generate PDF" button
- Send signature link to employee

#### Checked Out Tab
- Shows assets with status "checked-out"
- Employee name and email
- Asset list
- Checkout date
- View signed PDF

#### Inventory Tab
- Track available equipment
- Current assignments

### 4. PDF Generation
Use library (e.g., PDFKit or jsPDF) to generate:
- Company header
- Employee info
- Asset table with values
- Total value
- Signature box
- Date signed

Store in S3: `panda-assets-docs` bucket

### 5. Email Notifications
- New request submitted → notify admins
- Request approved → notify supervisor
- PDF ready → send signature link to employee
- Asset signed → notify admins & supervisor

## Implementation Steps

1. ✅ Create DynamoDB table
2. ✅ Add Lambda endpoints
3. ✅ Build request form in assets.html
4. ✅ Wire up approval workflow
5. ✅ Implement PDF generation
6. ✅ Add signature capture
7. ✅ Connect to employee data
8. ✅ Test complete workflow
9. ✅ Deploy

## Equipment Options (from JotForm)
- Complete Desktop Setup ($100)
- Complete New Hire Kit for Sales Rep ($100)
- Desktop Computer ($100)
- Desktop Screens ($100)
- Laptop ($100)
- iPad w/case and charger ($100)
- 32 ft Ladder ($100)
- 18 ft Little Giant ladder ($100)
- GAF Sales Kit ($100)
- GOAT Steep Roof Assist ($100)

## Office Locations
- Delaware
- King of Prussia
- Maryland
- New Jersey
- North Carolina
- Tampa
- Virginia
