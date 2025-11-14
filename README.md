# Mission Control Center - Water Kiosk Dashboard

A professional control center dashboard for managing water kiosks across multiple locations. Built with Chart.js and vanilla JavaScript.

## Files

- **dashboard.html** - Complete dashboard interface with embedded CSS and JavaScript (all 4 tabs)
- **serve.py** - Simple Python web server to run the dashboard locally
- **analytics_api.py** - Flask backend for processing CSV transaction data
- **favicon.ico** - Tusafishe logo for browser tab
- **logo.jpg** - Tusafishe logo displayed in header

## Setup

### Virtual Environment

It's recommended to run this project in a Python virtual environment. To set up:

```bash
cd ~/workspace/cloud_server/water-kiosk-control-panel
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip install flask flask-cors
```

### Exiting the Virtual Environment

When you're done working, deactivate the virtual environment:

```bash
deactivate
```

## How to View

### Quick Start (Dashboard Only)

```bash
cd ~/workspace/cloud_server/water-kiosk-control-panel
source venv/bin/activate
python3 serve.py
```

Then open your browser to: **http://localhost:8888/dashboard.html**

### With Analytics (Recommended)

Open two terminals:

**Terminal 1 - Analytics API:**
```bash
cd ~/workspace/cloud_server/water-kiosk-control-panel
source venv/bin/activate
python3 analytics_api.py
```

**Terminal 2 - Dashboard:**
```bash
cd ~/workspace/cloud_server/water-kiosk-control-panel
source venv/bin/activate
python3 serve.py
```

Then open: **http://localhost:8888/dashboard.html**

The dashboard will be on port 8888, analytics API on port 5000. Press `Ctrl+C` to stop either server.

## Features

### Dashboard Tab
- **System Summary** with kiosk status pie chart (blue color scheme)
- **Kiosks Online** - Real-time count and percentage
- **Transactions Yesterday** - Historical transaction count
- **Active Alerts** - Critical and warning alerts with descriptions
- Timestamp showing last update

### Analytics Tab (Real Data Integration)
- **Real CSV Processing**: Select and analyze transaction CSV files
- **Key Metrics**: Total transactions, unique users, average volume, success rate
- **Top Users by Volume**: Horizontal bar chart of heaviest consumers (top 20)
- **Top Users by Frequency**: Horizontal bar chart of most frequent users (top 20)
- **Volume Distribution**: Histogram showing transaction distribution across volume ranges
- **Client Activity**: Breakdown of transactions per kiosk/client
- **Day of Week Analysis**: Usage patterns across each day of the week
- **Dynamic Charts**: All visualizations update based on selected CSV file

### Kiosks Tab
- Searchable table of all kiosks (scalable to 600+)
- Filter by status (Online/Offline/Out of Service)
- Shows: ID, Location, Status, Connected Clients, Firmware Version, Last Seen
- Click to view kiosk details with management actions
- OTA Update, Reboot, and Configure buttons for each kiosk

### Users Tab
- Customer search and management interface
- Filter by status (Active/Inactive)
- View detailed customer accounts with:
  - Account Information (Phone, Name, Account ID, Status, Created Date)
  - Account Details (Credits, PIN, Registration Status, Last Activity)
- Customer Service Actions:
  - Reset PIN
  - Add Credits
  - Activate/Deactivate Account
  - View Transactions
  - Edit Account Information

## Analytics Details

### Usage

1. **Open the Dashboard**: Navigate to `http://localhost:8888/dashboard.html`
2. **Go to Analytics Tab**: Click the "Analytics" tab in the left sidebar
3. **Select a CSV File**: The dropdown will show all available transaction CSV files
4. **Load Analytics**: Click the "Load Analytics" button
5. **View Visualizations**:
   - Key metrics (transactions, users, success rate)
   - Top users by volume (horizontal bar chart)
   - Top users by frequency (horizontal bar chart)
   - Volume distribution (histogram)
   - Client activity breakdown

### CSV File Format

The system expects CSV files with these columns:
- `Timestamp` - When the transaction occurred (optional for display)
- `Client_Name` - Name of the kiosk/client (e.g., "Client 1", "Client 2")
- `User_ID` - Unique user identifier (phone number or ID)
- `PIN` - User PIN (stored but not used in analytics)
- `Volume_ML` - Water volume in milliliters
- `Response` - Transaction status ("PASS" or other)

Example:
```csv
Timestamp,Client_Name,User_ID,PIN,Volume_ML,Response
uptime_38_sec,Client 2,708890499,1345,156,PASS
uptime_41_sec,Client 3,708890780,2876,413,PASS
```

### Key Metrics Dashboard
- **Total Transactions**: Count of all transactions in selected file
- **Unique Users**: Count of unique User_IDs
- **Average Volume**: Mean water volume dispensed
- **Total Volume**: Total volume in liters
- **Success Rate**: Percentage of PASS responses
- **Pass/Fail Count**: Breakdown of successful vs failed transactions

### Visualizations

1. **Top Users by Volume** (Horizontal Bar Chart)
   - Shows the 20 users with highest total volume consumption
   - Blue color scheme matching dashboard design

2. **Top Users by Frequency** (Horizontal Bar Chart)
   - Shows the 20 users with most frequent dispense requests
   - Green color scheme for distinction

3. **Volume Distribution** (Bar Chart)
   - Categorizes transactions by volume ranges
   - Shows how many transactions fall into each range:
     - 0ml
     - 1-100ml
     - 101-250ml
     - 251-500ml
     - 501-1000ml
     - 1000ml+

4. **Client Activity** (Bar Chart)
   - Shows transaction count per client/kiosk
   - Purple color scheme
   - Useful for identifying which dispensers are most active

5. **Day of Week Analysis** (Bar Chart)
   - Shows usage patterns across each day of the week
   - Weekdays (Mon-Fri) displayed in lighter blue, Weekends (Sat-Sun) in darker blue
   - Helps identify peak usage days for capacity planning and scheduling
   - Valuable for school context: shows when water demand is highest
   - Automatically loads when entering Analytics tab

## Design Features

- **Blue gradient background** (#2563eb to #3b82f6) matching Tusafishe branding
- **Drop shadows** on all UI elements for depth and visual separation
- **Rounded corners** on boxes, logo, and main container
- **Vertical tab navigation** with active tab highlighting
- **Responsive layout** with flexbox and CSS grid
- **Chart.js integration** for pie chart visualization
- **Dense data presentation** with tables and search/filter functionality
- **Professional typography** using system fonts

## Sample Data

The dashboard uses hardcoded sample data in JavaScript:
- 10 kiosks (0001-0010): 8 online, 2 offline
- 5 customers with various account statuses
- 1,247 transactions yesterday
- 2 active alerts
- Analytics metrics with daily/monthly trends

To connect to real data, replace the `sampleData` object with API calls to your Flask backend.

## API Integration

### Analytics API

The analytics tab uses real API endpoints for CSV processing:

```
GET /api/analytics/files - Get list of available CSV files
GET /api/analytics/analyze?files=filename.csv - Analyze transaction data
GET /api/analytics/daily-trends - Multi-day trend analysis
GET /api/analytics/weekday-trends - Usage patterns by day of week
GET /api/analytics/health - Health check
```

### Future Integration Points

To connect other dashboard sections to real backends:

```javascript
// Example: Fetch system health
fetch('/api/system/health')
    .then(r => r.json())
    .then(data => {
        updateSummary(data);
        renderKioskStatusChart(data);
    });
```

## Troubleshooting

### "No CSV files found"
- Ensure CSV files are in the same directory as `analytics_api.py` and `serve.py`
- Files must match the pattern `transactions*.csv`

### "Error loading files"
- Check that analytics_api.py server is running on port 5000
- Check browser console for detailed error messages

### Charts not displaying
- Ensure Chart.js library is loaded (CDN)
- Check browser console for JavaScript errors
- Try refreshing the page

### Port already in use
If port 5000 or 8888 is already in use:
- Edit `analytics_api.py` line 137: change `port=5000`
- Edit `serve.py` and modify the port

## Performance

- Handles CSV files with thousands of transactions
- Chart rendering is responsive and smooth
- Data loads in 1-2 seconds for typical files
- Charts update smoothly without page refresh

## Browser Compatibility

- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

All modern browsers with ES6 support.
