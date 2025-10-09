# Termination Date and Refund Email Feature

## Overview
Added termination date functionality to the employee management system with automatic email notifications for merchandise refund collection when employees are terminated within 90 days of employment.

## Features Implemented

### 1. Termination Date Field
- **Location**: Employee edit modal in `employee.html`
- **Field**: Date input for termination date
- **Behavior**: 
  - Optional field (leave blank for active employees)
  - Automatically marks employee as terminated when populated
  - Displays in employee tables with red calendar icon

### 2. Automatic Email Notifications
- **Trigger**: When termination date is set for employee with ≤ 90 days employment
- **Recipient**: robwinters@pandaexteriors.com
- **Conditions**: 
  - Employee employed for 90 days or less
  - Employee has merchandise purchases/requests with value > $0

### 3. Email Content
**Subject**: `Merch Refund Collection Required for Terminated Employee: [Employee Name]`

**Body includes**:
- Employee name and contact information
- Days employed calculation
- Merchandise refund amount (from Shopify orders or employee records)
- List of purchased/requested items
- Professional HTML formatting

### 4. Data Sources for Merchandise
The system checks multiple sources for merchandise information:
1. **Shopify Orders**: Real purchase data matched by email
2. **Employee Records**: Manual merchandise entries
3. **Both personal and work emails** are checked for Shopify matches

## Technical Implementation

### Frontend Changes (`employee.html`)
- Added termination date input field to edit modal
- Updated employee display to show termination dates
- Enhanced termination status detection logic
- Visual indicators for terminated employees

### Backend Changes (`lambda_function.py`)
- New function: `send_termination_refund_email_if_needed()`
- Updated `update_employee()` to trigger email on termination
- Integration with existing Shopify API for merchandise data
- Employment duration calculation
- SES email sending with HTML formatting

### Email Logic Flow
1. Employee termination date is set via edit modal
2. System calculates days employed (termination date - hire date)
3. If ≤ 90 days, system checks for merchandise purchases
4. Retrieves Shopify orders and/or employee merchandise records
5. Calculates total refund amount
6. Sends formatted email to HR with collection details

## Usage Instructions

### For Administrators
1. Navigate to https://www.pandaadmin.com/employee.html
2. Click edit button for any employee
3. Set the "Termination Date" field
4. Save changes
5. If employee meets criteria, email is automatically sent

### Email Criteria
- **Days Employed**: ≤ 90 days
- **Merchandise Value**: > $0
- **Email Sent To**: robwinters@pandaexteriors.com

## Testing
- Comprehensive test scripts created
- Logic verified for various scenarios
- Email formatting tested
- Integration with existing Shopify data confirmed

## Files Modified
- `employee.html` - Added UI components
- `lambda_function.py` - Added email functionality
- Deployed to production Lambda function

## Security & Compliance
- Uses existing SES configuration
- Follows established email patterns
- Secure data handling for employee information
- No sensitive data exposure in logs