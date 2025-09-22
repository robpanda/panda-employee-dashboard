# Panda Exteriors Employee Dashboard

A comprehensive employee management system with smart import functionality, duplicate detection, and merchandise tracking.

## Features

- **Smart Import System**: Automatically handles CSV/Excel imports with intelligent employee matching
- **Duplicate Detection**: Priority-based matching (Email → Last Name → Full Name)
- **Employee Management**: Add, edit, terminate, and reactivate employees
- **Merchandise Tracking**: Track merchandise requests and fulfillment
- **Profile Editing**: Click-to-edit employee profiles
- **Lead Management**: Complete CRM functionality with validation and enrichment

## Files

- `index.html` - Main dashboard application
- `lambda_function.py` - AWS Lambda backend for data persistence
- `create_tables.py` - DynamoDB table creation script
- `undo_import.py` - Script to undo imports

## Deployment

The dashboard is hosted on AWS S3 at:
https://panda-exteriors-map-bucket.s3.amazonaws.com/leads/employee_dashboard.html

## Smart Import Rules

- Anyone NOT on the new list will be terminated
- Anyone NEW will be added as active employee  
- Anyone already in database remains unchanged
- Full backup/undo capability

## Data Sources

- Google Sheets: https://docs.google.com/spreadsheets/d/1vO-94iEtB8FAthneJ8Cx1Cm-iA-oHJiBwOPAGmsiM-4/edit
- Supports CSV and Excel file uploads
- DynamoDB backend for persistence

## Usage

1. Navigate to Smart Import tab
2. Upload CSV file or import from Google Sheets
3. Review changes and use undo if needed
4. Manage employees in Active/Terminated tabs
5. Check Duplicates tab for data quality