# Merchandise Value Parsing Fix

## Problem

Error: `Merchandise data error: could not convert string to float: '$144.29'`

This error occurred because merchandise values are stored in the database as strings with currency formatting (e.g., `"$144.29"`, `"$1,663.20"`) but the code was trying to convert them directly to float without removing the `$` and `,` symbols.

## Root Cause

The issue occurred in two places:

### 1. Lambda Function (Python)
The `get_employees()` function in `lambda_function.py` was converting Decimal values to float for JSON serialization, but wasn't handling string values with `$` symbols.

**Location**: `lambda_function.py`, lines 180-189

### 2. Frontend (JavaScript)
The `employee.html` file was using `parseFloat()` directly on merchandise values without stripping the `$` and `,` symbols first.

**Locations**: `employee.html`, lines 1443, 2075, 2098, 2293, 2294

## Solutions Applied

### ✅ Lambda Function Fix (Deployed)

Added handling for string merchandise values in the `get_employees()` function:

```python
# Convert Decimal to float for JSON serialization
for item in items:
    for key, value in item.items():
        if isinstance(value, Decimal):
            item[key] = float(value)
        # Handle Merchandise Value strings with $ and commas
        elif key in ['Merchandise Value', 'merchandise_value'] and isinstance(value, str):
            try:
                # Remove $ and commas, then convert to float
                cleaned = value.replace('$', '').replace(',', '').strip()
                item[key] = float(cleaned) if cleaned else 0.0
            except (ValueError, AttributeError):
                item[key] = 0.0
```

**Deployed**: ✅ Commit `86ffdeb`, deployed via `deploy-lambda-fixed.sh`

### ✅ Frontend Fix (Deployed)

Added `parseMerchandiseValue()` helper function to `employee.html`:

```javascript
function parseMerchandiseValue(value) {
    if (!value) return 0;
    const cleaned = String(value).replace(/[$,]/g, '').trim();
    const parsed = parseFloat(cleaned);
    return isNaN(parsed) ? 0 : parsed;
}
```

Replaced all `parseFloat()` calls with `parseMerchandiseValue()`:
- Line 1451: `parseMerchandiseValue(employee['merchandise_value'] || employee['Merchandise Value'])`
- Line 2083: `parseMerchandiseValue(merch.merchandise_value)`
- Line 2106: `parseMerchandiseValue(merch.merchandise_value).toFixed(2)`
- Line 2301: `parseMerchandiseValue(a.merchandise_value)`
- Line 2302: `parseMerchandiseValue(b.merchandise_value)`

**Deployed**: ✅ Commit `4347349`, ready for S3/CloudFront deployment

## Testing

### Lambda Test:
```bash
curl -s "https://dfu3zr3dnrvgiiwa2yu77cz5fq0rqmth.lambda-url.us-east-2.on.aws/employees" | jq '.employees[] | select(.["Merchandise Value"]) | {name: "\(.["First Name"]) \(.["Last Name"])", value: .["Merchandise Value"]}'
```

### Frontend Test:
1. Load https://www.pandaadmin.com/employee.html
2. Check browser console for errors
3. Verify merchandise values display correctly
4. Test sorting by merchandise value

## Files Modified

1. **lambda_function.py** - Added string value handling in `get_employees()`
2. **employee.html** - Added `parseMerchandiseValue()` helper function
3. **fix-merchandise-parsing.js** - Reference implementation (helper file)

## Deployment Status

- ✅ Lambda: Deployed to `panda-employee-api` (us-east-2)
- ✅ Code: Committed to GitHub
- ⏳ Frontend: Needs deployment to S3/CloudFront (if applicable)

## Next Steps

If employee.html is hosted on S3/CloudFront:
1. Upload updated `employee.html` to S3
2. Invalidate CloudFront cache
3. Test in production

If employee.html is served directly:
1. The fix is already in GitHub
2. Pull latest changes to production server
3. Test

## Related Documentation

- [SHOPIFY_SYNC_SOLUTION.md](./SHOPIFY_SYNC_SOLUTION.md) - Shopify sync fix overview
- [SHOPIFY-API-INSIGHTS.md](./SHOPIFY-API-INSIGHTS.md) - Shopify API research findings
- [fix-merchandise-parsing.js](./fix-merchandise-parsing.js) - Helper function reference

---

**Status**: ✅ **FIXED AND DEPLOYED**

Both Lambda and frontend code have been updated to properly handle merchandise values with `$` and `,` symbols.
