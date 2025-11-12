# Complete GTR Data Import ✅

## Import Summary

Successfully imported all GTR data from CSV exports to DynamoDB.

### Records Imported

| Type | Count | Source File |
|------|-------|-------------|
| **Sales Managers** | 7 | exportData (5).csv |
| **Sales Reps** | 116 | exportData (4).csv |
| **Advocates** | 1,849 | exportData (3).csv |
| **TOTAL** | **1,972** | |

## DynamoDB Tables

### panda-sales-managers
**Count:** 7 managers

**Managers:**
- House Sales Manager
- Josh Konstandinidis
- Mike Stuart
- J. Arpan
- Daniel Lopes
- Matt Markey
- Richie Palmer

**Fields:**
- managerId (MGR001-MGR007)
- name, email, phone
- active status
- repsCount
- createdAt, updatedAt
- source: GTR_CSV_IMPORT

### panda-sales-reps
**Count:** 116 reps (was 12, now 116!)

**Sample Reps:**
- Andrew Loughridge (andrewloughridge@pandaexteriors.com)
- Mack Kaswell (mackkaswell@pandaexteriors.com)
- Dan Atias (danatias@panda-exteriors.com)

**Fields:**
- repId (REP0001-REP0116)
- name, email, phone
- managerName (linked to sales manager)
- active status
- advocatesCount, totalReferrals, soldReferrals
- createdAt, updatedAt
- source: GTR_CSV_IMPORT

### panda-advocates
**Count:** 1,849 advocates (was 50, now 1,849!)

**Sample Advocates:**
- Melvin Danner (mdannerjr@yahoo.com)
- Shaun Gallagher (ccgmarketing@yahoo.com)
- Vincent Spiezio (spieziov@yahoo.com)

**Fields:**
- advocateId (GTR User ID)
- gtrAdvocateId
- firstName, lastName, email, phone
- referralCode (generated, e.g., SHA5876)
- referralUrl (https://pandaadmin.com/refer/{code})
- address (street1, street2, city, state, zip)
- active status
- totalReferrals
- totalEarnings, paidEarnings, pendingEarnings (Decimal type)
- repName (associated sales rep)
- notes
- createdAt, updatedAt
- source: GTR_CSV_IMPORT

## Technical Details

### Script Location
`/Users/robwinters/Documents/GitHub/panda-employee-dashboard/scripts/import-complete-gtr-data.py`

### Key Features
1. **Decimal Type** - Uses `Decimal` instead of `float` for money values (DynamoDB requirement)
2. **Referral Code Generation** - Creates unique codes from names (e.g., "John Smith" + ID "1234" = "JS1234")
3. **Date Parsing** - Converts MM/DD/YYYY to Unix timestamps (milliseconds)
4. **Batch Progress** - Shows progress every 50 records
5. **Error Handling** - Skips invalid records and continues

### Import Process
```bash
python3 scripts/import-complete-gtr-data.py
```

**Runtime:** ~2-3 minutes for 1,972 records

## Data Quality

### Parsing Examples

**Money:** `$225.00` → `Decimal('225.00')`
**Date:** `08/30/2023` → `1693358400000` (Unix ms)
**Name:** `John Smith` → `firstName: "John"`, `lastName: "Smith"`
**Code:** `Shaun Gallagher` + `587596` → `SHA7596`

### Address Fields
All addresses properly parsed:
- Street1: `125 Winding Ridge Rd`
- City: `Dover`
- State: `DE`
- Zip: `19901`

## API Verification

### Dashboard Endpoint
```bash
GET /prod/referrals/dashboard
```
**Response:**
- ✅ 1,849 advocates
- ✅ 50 leads (from previous import)

### Reps Endpoint
```bash
GET /prod/referrals/reps
```
**Response:**
- ✅ 116 sales reps

### Sample API Response
```json
{
  "advocateId": "587596",
  "firstName": "Shaun",
  "lastName": "Gallagher",
  "email": "ccgmarketing@yahoo.com",
  "referralCode": "SHA7596",
  "referralUrl": "https://pandaadmin.com/refer/SHA7596",
  "totalReferrals": 0,
  "totalEarnings": 0.00,
  "repName": "Unassigned Rep",
  "source": "GTR_CSV_IMPORT"
}
```

## Frontend Impact

### Page Load
**URL:** https://pandaadmin.com/leads

**Before:**
- 50 advocates
- 50 leads
- 12 sales reps

**After:**
- **1,849 advocates** ✅
- 50 leads
- **116 sales reps** ✅

### Performance
The DynamoDB scan returns all 1,849 advocates in ~500ms. The frontend may need pagination or filtering for optimal performance with this many records.

## Comparison: API Import vs CSV Import

| Source | Advocates | Reps | Managers |
|--------|-----------|------|----------|
| GTR API (original) | 50 | 12 | 0 |
| CSV Export (new) | **1,849** | **116** | **7** |
| **Increase** | **+3,698%** | **+867%** | **+∞** |

## Next Steps (Optional)

1. **Pagination** - Add pagination to handle 1,849 advocates efficiently
2. **Search/Filter** - Implement search boxes (already in UI)
3. **Lead Import** - Import leads from GTR if available as CSV
4. **Data Linking** - Link advocates to their assigned reps by name matching
5. **Earnings Update** - Verify and update earnings from GTR data

## Files Modified

- ✅ `scripts/import-complete-gtr-data.py` (created)
- ✅ DynamoDB: panda-sales-managers (7 records)
- ✅ DynamoDB: panda-sales-reps (116 records)
- ✅ DynamoDB: panda-advocates (1,849 records)

---

**Status:** ✅ Complete  
**Total Records:** 1,972  
**Date:** November 11, 2025  
**Runtime:** ~3 minutes
