# Fleet Management System - Quick Start Guide

## 🚀 Deploy in 3 Steps

### Step 1: Create Tables (5 minutes)
```bash
cd /Users/robwinters/Documents/GitHub/panda-employee-dashboard
./create-fleet-tables.sh
```
✅ Creates 6 DynamoDB tables for fleet management

### Step 2: Import Your Data (2 minutes)
```bash
./import-fleet-data.py
```
✅ Imports all 112 vehicles, accidents, EZ passes, and maintenance records from your Excel file

### Step 3: Deploy System (3 minutes)
```bash
./deploy-fleet-lambda.sh
```
✅ Deploys Lambda function, API Gateway routes, and frontend page

## 🎯 Access Your System

**Frontend**: https://pandaadmin.com/fleet-assets.html

## 📊 What You Get

### Dashboard
- **112 Total Vehicles** tracked
- **98 Assigned** to drivers
- **10 Floaters** available
- **4 Downed** needing repair
- **Real-time fleet value**

### Vehicle Management
- ✅ Add/edit vehicles
- ✅ Check out to drivers
- ✅ Check in from drivers
- ✅ Track mileage and value
- ✅ Filter by status (assigned, floater, downed)
- ✅ Search by name, VIN, license plate

### Accident Tracking
- ✅ Report accidents with photos/video
- ✅ Track estimates vs actual costs
- ✅ Record claim numbers
- ✅ Monitor repair status
- ✅ Calculate total costs

### EZ Pass Management
- ✅ Track all EZ Pass IDs
- ✅ Assign to vehicles
- ✅ Monitor active/canceled status
- ✅ Inventory management

### Maintenance Alerts
- ✅ Registration expiration tracking
- ✅ Insurance renewal reminders
- ✅ Emissions test schedules
- ✅ Overdue item alerts
- ✅ Maintenance history

### Request Workflow
- ✅ Employees request vehicles
- ✅ Manager approval
- ✅ Admin assigns vehicle
- ✅ Track duration and return

## 📱 Key Features

### For Fleet Managers
1. **Dashboard Overview** - See everything at a glance
2. **Quick Filters** - Find vehicles by status instantly
3. **Assignment Tracking** - Know who has what
4. **Cost Monitoring** - Track accident and maintenance costs

### For Drivers
1. **Vehicle Requests** - Request a vehicle for your territory
2. **Check-out Process** - Simple assignment workflow
3. **Incident Reporting** - Report accidents immediately

### For Admins
1. **Complete Control** - Manage all aspects of the fleet
2. **Maintenance Scheduling** - Never miss a renewal
3. **Financial Tracking** - Monitor all costs
4. **Historical Data** - Full audit trail

## 🔍 Quick Tips

### Search for a Vehicle
Type in the search bar:
- Asset name: "Panda 7"
- Driver: "Jason Daniel"
- VIN: last 6 digits
- License plate: "PANDA07"

### Filter by Status
Click the status buttons:
- **All** - Show everything
- **Assigned** - Currently with drivers
- **Floaters** - Available to assign
- **Downed** - Needs attention

### Check Out a Vehicle
1. Find a **floater** vehicle
2. Click the check-out icon (sign-out)
3. Enter driver details
4. Confirm assignment

### Check In a Vehicle
1. Find the **assigned** vehicle
2. Click the check-in icon (sign-in)
3. Update mileage
4. Confirm return

### Report an Accident
1. Go to **Accidents** tab
2. Click **Report Accident**
3. Select vehicle
4. Fill in details
5. Upload photos/video
6. Submit report

### Track Maintenance
1. Go to **Maintenance** tab
2. See overdue items in yellow alert
3. Click schedule for new maintenance
4. Mark complete when done

## 📋 Data Imported

From your Excel file "Fleet Dept Vehicle Sheet.xlsx":

### Assigned Sheet → Vehicles
- 98 vehicles currently assigned
- Driver contact information
- Department assignments
- Phone numbers on vehicles

### FloatersDowned Sheet → Available Vehicles
- 10 floater vehicles ready to assign
- 4 downed vehicles needing repair
- Location information

### Accidents Sheet → Accident Records
- Historical accident data
- Repair estimates and costs
- Insurance claim information
- Completion dates

### EZ Pass Sheet → EZ Pass Inventory
- All EZ Pass IDs
- Current assignments
- Active/canceled status
- Bag inventory

### Sold Sheet → Sales History
- 20 sold vehicles
- Sale prices and dates
- Buyer information

### Emmisions+ Sheet → Maintenance Schedule
- Registration expiration dates
- Emissions test schedules
- Insurance renewal dates
- Vanity plate orders

## 🛠️ Common Tasks

### Add a New Vehicle
1. **Vehicles** tab → **Add Vehicle** button
2. Fill in:
   - Asset name (e.g., "Panda 125")
   - Year, make, model
   - VIN and license plate
   - Department and territory
3. Save

### Assign EZ Pass
1. **EZ Pass** tab → **Add EZ Pass** button
2. Enter EZ Pass ID
3. Select vehicle
4. Choose territory
5. Save

### Schedule Maintenance
1. **Maintenance** tab → **Schedule Maintenance** button
2. Select vehicle
3. Choose type (emissions, registration, insurance)
4. Set due date
5. Add provider and cost estimate
6. Save

### Approve Vehicle Request
1. **Requests** tab
2. Find pending request
3. Click ✓ to approve or ✗ to reject
4. Add notes if needed
5. Assign available vehicle

## 📊 Reports Available

### Fleet Summary
- Total vehicles by status
- Fleet value
- Utilization rate

### Accident Costs
- Total repair costs
- Insurance payouts
- Average cost per accident

### Maintenance Due
- Upcoming renewals
- Overdue items
- Cost projections

## 🔗 API Endpoints

All endpoints are at:
`https://z6q74akq5f.execute-api.us-east-2.amazonaws.com/prod`

- `/vehicles` - Vehicle management
- `/accidents` - Accident tracking
- `/ezpass` - EZ Pass management
- `/maintenance` - Maintenance scheduling
- `/requests` - Vehicle requests
- `/fleet-stats` - Dashboard statistics

## 💡 Pro Tips

1. **Use Filters** - Status filters make finding vehicles fast
2. **Search Smart** - Search works across multiple fields
3. **Check Overdue** - Red badge shows overdue maintenance
4. **Track Costs** - Record actual costs for better budgeting
5. **Regular Updates** - Keep mileage and status current

## 📞 Need Help?

### Check These First:
1. **Browser Console** - F12 for error messages
2. **Lambda Logs** - CloudWatch logs for backend issues
3. **API Test** - Try endpoints directly with curl
4. **Table Data** - Verify DynamoDB has data

### Common Issues:

**Can't see vehicles?**
- Check API URL in frontend code
- Verify tables have data
- Check CORS headers

**Import failed?**
- Verify Excel file path
- Check AWS credentials
- Ensure tables exist

**Changes not saving?**
- Check Lambda logs
- Verify permissions
- Test API endpoint directly

## 🎉 You're Ready!

Your fleet management system is now live with:
- ✅ 112 vehicles tracked
- ✅ Complete accident history
- ✅ EZ Pass inventory
- ✅ Maintenance schedules
- ✅ Request workflow
- ✅ Real-time dashboard

**Access now**: https://pandaadmin.com/fleet-assets.html

---

**Questions?** Check [FLEET-DEPLOYMENT-GUIDE.md](./FLEET-DEPLOYMENT-GUIDE.md) for detailed documentation.
