# Fleet Asset Management System - Deployment Guide

## Overview

This comprehensive fleet management system tracks:
- **Vehicles** (112 total: 98 assigned, 10 floaters, 4 downed)
- **Accidents** with repair estimates and claims
- **EZ Pass** assignments and tracking
- **Maintenance** schedules (emissions, registration, insurance)
- **Vehicle Requests** with approval workflow
- **Sales Records** for sold/traded vehicles

## Architecture

### Backend
- **Lambda Function**: `lambda_fleet.py`
- **DynamoDB Tables**: 6 tables for complete fleet data
- **API Gateway**: RESTful endpoints for all operations

### Frontend
- **URL**: https://pandaadmin.com/fleet-assets.html
- **Features**:
  - Real-time dashboard with fleet stats
  - Vehicle management with check-in/out
  - Accident reporting and tracking
  - EZ Pass management
  - Maintenance scheduling with overdue alerts
  - Request workflow

## Deployment Steps

### Step 1: Create DynamoDB Tables

```bash
cd /Users/robwinters/Documents/GitHub/panda-employee-dashboard
chmod +x create-fleet-tables.sh
./create-fleet-tables.sh
```

This creates 6 tables:
- `panda-fleet-vehicles`
- `panda-fleet-accidents`
- `panda-fleet-ezpass`
- `panda-fleet-sales`
- `panda-fleet-maintenance`
- `panda-fleet-requests`

### Step 2: Import Existing Data

```bash
# Install required dependencies
pip3 install pandas openpyxl boto3

# Run the import script
chmod +x import-fleet-data.py
./import-fleet-data.py
```

This imports all data from your Excel file:
- 112 vehicles from "Assigned" sheet
- Floater vehicles from "FloatersDowned" sheet
- Accident records from "Accidents" sheet
- EZ Pass data from "EZ Pass" sheet
- Sold vehicles from "Sold" sheet
- Maintenance schedules from "Emmisions+" sheet

### Step 3: Deploy Lambda Function

```bash
chmod +x deploy-fleet-lambda.sh
./deploy-fleet-lambda.sh
```

This will:
1. Package the Lambda function
2. Create/update the Lambda function in AWS
3. Setup API Gateway routes
4. Deploy the frontend to S3
5. Invalidate CloudFront cache

### Step 4: Verify Deployment

1. **Check DynamoDB Tables**:
   ```bash
   aws dynamodb list-tables --region us-east-2 | grep fleet
   ```

2. **Test API Endpoints**:
   ```bash
   # Get fleet stats
   curl https://z6q74akq5f.execute-api.us-east-2.amazonaws.com/prod/fleet-stats

   # Get all vehicles
   curl https://z6q74akq5f.execute-api.us-east-2.amazonaws.com/prod/vehicles

   # Get accidents
   curl https://z6q74akq5f.execute-api.us-east-2.amazonaws.com/prod/accidents
   ```

3. **Access Frontend**:
   - Navigate to https://pandaadmin.com/fleet-assets.html
   - You should see the fleet dashboard with stats

## Features

### 1. Vehicle Management

**Track**:
- Asset ID, year, make, model
- VIN and license plate
- Current driver and contact info
- Territory and location
- Mileage and value
- Status (assigned, floater, downed, maintenance, sold)

**Actions**:
- Add new vehicles
- Edit vehicle details
- Check out to driver
- Check in from driver
- Mark as downed/maintenance
- Record sale

### 2. Accident Tracking

**Capture**:
- Date and vehicle
- Driver and manager
- Claim number and provider
- Estimates vs actual costs
- Documentation (video, police report, statements)
- Fault determination
- Repair shop and completion date

**Workflow**:
- Report new accident
- Update with estimates
- Track repair progress
- Record final costs
- Close claim

### 3. EZ Pass Management

**Track**:
- EZ Pass ID
- Assigned vehicle
- Driver
- Plate number
- Territory
- Status (active, in_bag, canceled)
- Bag IDs for inventory

### 4. Maintenance Scheduling

**Monitor**:
- Emissions due dates
- Registration renewal
- Insurance expiration
- Scheduled maintenance
- Repair needs

**Alerts**:
- Overdue items highlighted
- Dashboard count of overdue
- Filter by status

### 5. Vehicle Requests

**Request Flow**:
1. Employee submits request
2. Specify vehicle type, duration, territory
3. Manager reviews and approves
4. Admin assigns available vehicle
5. Vehicle checked out
6. Return and check-in

## API Endpoints

### Vehicles
- `GET /vehicles` - List all vehicles (filter by status, driver, department)
- `POST /vehicles` - Create new vehicle
- `PUT /vehicles` - Update vehicle
- `DELETE /vehicles` - Mark vehicle as sold
- `POST /checkout` - Check out vehicle to driver
- `POST /checkin` - Check in vehicle

### Accidents
- `GET /accidents` - List all accidents (filter by vehicle, status)
- `POST /accidents` - Report new accident
- `PUT /accidents` - Update accident details

### EZ Pass
- `GET /ezpass` - List all EZ Pass records (filter by vehicle, status)
- `POST /ezpass` - Create new EZ Pass
- `PUT /ezpass` - Update EZ Pass

### Sales
- `GET /sales` - List all sales
- `POST /sales` - Record vehicle sale

### Maintenance
- `GET /maintenance` - List maintenance records (filter by vehicle, status)
- `POST /maintenance` - Schedule maintenance
- `PUT /maintenance` - Update maintenance record
- `GET /overdue-maintenance` - Get overdue items

### Requests
- `GET /requests` - List vehicle requests (filter by status, requester)
- `POST /requests` - Submit new request
- `PUT /requests` - Update request (approve/reject/fulfill)

### Stats
- `GET /fleet-stats` - Get dashboard statistics

## Database Schema

### Vehicles Table
```javascript
{
  vehicle_id: "PANDA-001",
  asset_name: "Panda 7",
  year: "2024",
  make: "Land Rover",
  model: "Defender",
  vin: "SALE27EU3R2311730",
  license_plate: "PANDA 3",
  status: "assigned|floater|downed|maintenance|sold",
  department: "Executive",
  current_driver: "Jason Daniel",
  driver_email: "jason@pandaexteriors.com",
  driver_phone: "(240) 345-9010",
  territory: "MD",
  location: "MD Base",
  mileage: 30953,
  unit_value: 65000,
  // ... additional fields
}
```

### Accidents Table
```javascript
{
  accident_id: "ACC-20241108-ABC123",
  accident_date: "2024-11-08",
  vehicle_id: "Panda69",
  driver: "Jane Doe",
  claim_number: "547896451266",
  panda_repair_estimate: 7000,
  actual_repair_cost: 4000,
  status: "pending|in_repair|completed",
  // ... additional fields
}
```

## Filters and Search

### Vehicle Filters
- **By Status**: All, Assigned, Floaters, Downed
- **By Search**: Asset name, driver, VIN, license plate

### Status Badges
- 🟢 **Assigned** - Currently with driver
- 🔵 **Floater** - Available for assignment
- 🔴 **Downed** - Out of service
- 🟡 **Maintenance** - Scheduled service
- ⚫ **Sold** - No longer in fleet

## Maintenance Alerts

The system automatically:
- Checks registration expiration dates
- Monitors insurance renewal dates
- Tracks emissions test schedules
- Calculates days overdue
- Displays count in alert banner

## Data Import Details

The `import-fleet-data.py` script processes:

1. **Assigned Sheet** → Active vehicles
2. **FloatersDowned Sheet** → Available/downed vehicles
3. **Accidents Sheet** → Historical accidents
4. **EZ Pass Sheet** → EZ Pass inventory
5. **Sold Sheet** → Sales records
6. **Emmisions+ Sheet** → Maintenance schedules

Data is cleaned and normalized:
- NaN values removed
- Dates converted to ISO format
- Status values standardized
- Empty fields handled gracefully

## Security

- All API endpoints use CORS headers
- Lambda has minimal permissions (DynamoDB only)
- S3 bucket access via CloudFront
- No sensitive data in frontend code

## Monitoring

Check Lambda logs:
```bash
aws logs tail /aws/lambda/panda-fleet-management --follow --region us-east-2
```

Check DynamoDB metrics:
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedReadCapacityUnits \
  --dimensions Name=TableName,Value=panda-fleet-vehicles \
  --start-time 2024-11-06T00:00:00Z \
  --end-time 2024-11-07T00:00:00Z \
  --period 3600 \
  --statistics Sum \
  --region us-east-2
```

## Troubleshooting

### Issue: Tables not creating
**Solution**: Check IAM permissions for DynamoDB table creation

### Issue: Lambda function not updating
**Solution**: Wait for function to be in "Active" state before deploying again

### Issue: Frontend not loading data
**Solution**:
1. Check API Gateway deployment
2. Verify CORS headers
3. Check browser console for errors
4. Confirm API URL in frontend code

### Issue: Import script fails
**Solution**:
1. Verify Excel file path
2. Check AWS credentials
3. Ensure tables exist
4. Check data format in Excel sheets

## Cost Estimate

Based on usage:
- **DynamoDB**: ~$5/month (6 tables, minimal traffic)
- **Lambda**: ~$1/month (free tier covers most usage)
- **API Gateway**: ~$3/month (REST API calls)
- **S3**: <$1/month (static hosting)
- **Total**: ~$10/month

## Next Steps

### Enhancements
1. **Email Notifications**
   - Overdue maintenance alerts
   - Accident report notifications
   - Request approval emails

2. **Reports**
   - Monthly fleet utilization
   - Accident costs by quarter
   - Maintenance spending
   - EZ Pass usage reports

3. **Mobile App**
   - Driver check-in/out via phone
   - Photo uploads for accidents
   - Mileage updates

4. **Integrations**
   - Connect to accounting software
   - Insurance provider API
   - GPS tracking integration
   - Fuel card system

## Support

For issues or questions:
- Check Lambda logs first
- Review DynamoDB table data
- Test API endpoints directly
- Check CloudFront distribution

## Files Created

1. `lambda_fleet.py` - Lambda function code
2. `fleet-assets.html` - Frontend application
3. `create-fleet-tables.sh` - DynamoDB table creation
4. `deploy-fleet-lambda.sh` - Full deployment script
5. `import-fleet-data.py` - Data import from Excel
6. `FLEET-SCHEMA.md` - Database schema documentation
7. `FLEET-DEPLOYMENT-GUIDE.md` - This file

## URLs

- **Frontend**: https://pandaadmin.com/fleet-assets.html
- **API Base**: https://z6q74akq5f.execute-api.us-east-2.amazonaws.com/prod

---

**Last Updated**: November 6, 2024
**Version**: 1.0.0
