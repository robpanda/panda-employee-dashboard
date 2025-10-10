# Shopify Order Sync for Employee Merchandise Tracking

## ✅ What Was Built

A complete Shopify order sync system to track employee merchandise purchases for your 90-day charge-back policy.

### 🎯 Problem Solved
- Manually importing employee merchandise purchases was tedious
- Need to track purchases for employees who leave within 90 days
- Hard to see which employees have outstanding merchandise charges

### ✨ Solution
Automatic sync of Shopify orders to employee records, matching by email address.

## 🚀 How to Use

### Step 1: Access the Merchandise Section
1. Go to https://www.pandaadmin.com/employee.html
2. Login with admin credentials
3. Click "🛍️ Merchandise" tab

### Step 2: Sync Shopify Orders
1. Click the **"Sync Shopify Orders"** button (yellow/warning button)
2. Wait for the sync to complete (usually 5-10 seconds)
3. See the success message: "✅ Successfully synced X Shopify orders!"
4. Merchandise table automatically refreshes with new data

### Step 3: Review Synced Orders
- Shopify orders show a **Shopify badge**
- Order details include "[Shopify #1234] Item Name"
- Values are automatically calculated
- Status reflects fulfillment (Pending/Shipped)

## 📊 What Gets Synced

### From Shopify to Employee Record:
- **Customer Email** → Matches employee email
- **Order Number** → Stored as `shopify_order_number`
- **Line Items** → Added to `merch_requested` field
- **Total Price** → Added to `merchandise_value`
- **Fulfillment Status** → Sets `merch_sent` (Yes/No)
- **Order Date** → Stored as `shopify_order_date`

### Example Before Sync:
```
Employee: John Doe (john@pandaexteriors.com)
Merch Requested: [empty]
Merchandise Value: $0.00
```

### Example After Sync:
```
Employee: John Doe (john@pandaexteriors.com)
Merch Requested: [Shopify #1234] GAF 2025 Polo - Black (x2), GAF Cap (x1)
Merchandise Value: $85.00
Status: Shipped
```

## 🔧 Technical Details

### API Endpoint
**POST** `/sync-shopify-merchandise`

### How It Works:
1. **Fetch Orders**: Gets last 50 orders from Shopify GraphQL API
2. **Get Employees**: Loads all employees from DynamoDB
3. **Match by Email**: Creates email → employee mapping
4. **Update Records**: For each matching order:
   - Appends order details to existing merchandise
   - Adds order value to total
   - Updates fulfillment status
   - Stores Shopify order metadata
5. **Return Results**: Shows synced count and any errors

### Shopify API Connection
- **Store**: `e0a6e2.myshopify.com` (pandaexteriors)
- **Access Token**: Stored securely in Lambda function
- **API Version**: 2023-10
- **Query Type**: GraphQL
- **Orders Fetched**: Last 50 orders

### Employee Matching
Orders are matched to employees by **email address**:
- Shopify customer email must match employee email exactly
- Case-insensitive matching
- Unmatched orders are reported but not synced

## 📋 Sync Results

### Success Message:
```
✅ Successfully synced 12 Shopify orders!
```

### With Warnings:
```
✅ Successfully synced 10 Shopify orders!
⚠️ 2 orders could not be matched to employees
```

### Common Reasons for Unmatched Orders:
1. Customer email doesn't match any employee email
2. Order has no customer email
3. Customer is not an employee (regular customer order)

## 🎯 90-Day Charge-Back Policy

### Use Case:
When an employee leaves within 90 days, you need to know:
- What merchandise they received
- Total value to charge back
- When items were shipped

### How to Track:
1. **View Merchandise**: Click employee name to see full details
2. **Check Value**: See `merchandise_value` column
3. **Review Items**: See all items in `merch_requested`
4. **Check Date**: See when items were shipped
5. **Calculate Charge**: Use total value for charge-back

### Example Scenario:
```
Employee: Jane Smith
Hire Date: September 1, 2025
Termination Date: November 15, 2025
Days Employed: 75 days (< 90)

Merchandise Received:
- [Shopify #5678] Safety Vest ($45)
- [Shopify #5892] Work Boots ($120)
Total Value: $165.00

Action: Charge back $165.00 from final paycheck
```

## 🔄 Sync Frequency

### Recommended Schedule:
- **Weekly**: Sync once per week to catch new orders
- **Before Terminations**: Always sync before processing a termination
- **After Bulk Orders**: Sync after company-wide merchandise distributions

### Manual Sync Only:
- System does NOT auto-sync
- You control when to sync
- Prevents accidental overwrites
- Allows review of orders first

## ⚠️ Important Notes

### Data Handling:
1. **Appends, Doesn't Replace**: New orders are added to existing merchandise records
2. **No Duplicates Checking**: Re-syncing the same order will create duplicates
3. **No Order Deletion**: Synced orders cannot be removed automatically
4. **Manual Entry Preserved**: Hand-entered merchandise is kept

### Best Practices:
1. ✅ Sync regularly (weekly)
2. ✅ Review unmatched orders
3. ✅ Verify employee emails match Shopify
4. ✅ Export data before major syncs (backup)
5. ❌ Don't sync multiple times without checking
6. ❌ Don't rely solely on auto-sync (always review)

## 🐛 Troubleshooting

### Problem: "Sync failed" Error
**Solution**: Check Lambda logs and verify Shopify API credentials

### Problem: No Orders Synced
**Possible Causes**:
- No new orders in Shopify
- All order emails don't match employees
- Shopify API credentials expired

### Problem: Wrong Employee Matched
**Cause**: Multiple employees with same email
**Solution**: Ensure each employee has unique email

### Problem: Values Doubled
**Cause**: Synced same orders twice
**Solution**: Manually edit employee record to remove duplicates

## 📞 Support

### Check Sync Logs:
```bash
aws logs tail /aws/lambda/panda-employee-dashboard --region us-east-2 --follow
```

### Test Shopify Connection:
1. Go to Shopify Admin
2. Check API credentials under: Apps > Develop apps
3. Verify access token has `read_orders` permission

### Verify Employee Emails:
1. Export employee list
2. Check email addresses match Shopify customers
3. Update any mismatches

## 📊 Example Sync Output

### Console Logs:
```
SYNC: Starting Shopify merchandise sync
SYNC: Retrieved 15 Shopify orders
SYNC: Found 245 employees
SYNC: Updated employee 10123 with order #1234
SYNC: Updated employee 10456 with order #1235
SYNC: No employee found for email customer@gmail.com
SYNC: Completed - 12 orders synced, 3 errors
```

### Result JSON:
```json
{
  "success": true,
  "message": "Successfully synced 12 Shopify orders",
  "synced": 12,
  "total_orders": 15,
  "errors": [
    "No employee found for customer@gmail.com",
    "No employee found for external@company.com",
    "Order 1240 has no email, skipping"
  ]
}
```

## ✅ Success Checklist

After syncing, verify:
- [ ] Synced count matches expected orders
- [ ] No critical errors in results
- [ ] Merchandise table shows Shopify badges
- [ ] Order values look correct
- [ ] Fulfillment statuses accurate
- [ ] Unmatched orders are expected (non-employees)

---

**Feature Status**: ✅ Live and Working
**Endpoint**: `/sync-shopify-merchandise`
**Shopify Store**: pandaexteriors.myshopify.com
**Last Updated**: October 10, 2025
**Version**: 1.0
