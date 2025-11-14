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

## Generating Transaction Data

Before running the dashboard with analytics, you must generate transaction data using the Python scripts in the `transactions/` directory.

### Step 1: Generate Kiosk Users and PINs

This creates 10 kiosks with randomized user databases and PIN assignments:

```bash
cd ~/workspace/cloud_server/water-kiosk-control-panel/transactions
source ../venv/bin/activate
python3 generate_kiosk_users.py
```

This script:
- Creates 10 kiosks (numbered 0000-9999)
- Generates 50-100 users per kiosk with Ugandan phone numbers (708XXXXXX format)
- Assigns random 4-digit PINs to each user
- Creates `kiosk_metadata.csv` and `kiosk_user_pin.csv` in each kiosk directory

### Step 2: Generate Transaction Data

This generates 30 days of realistic transaction data for each kiosk:

```bash
python3 generate_transactions.py
```

This script:
- Generates 30 days of transaction history (starting from Oct 15, 2025)
- Creates daily CSV files for each kiosk: `transactions_KIOSK_MMDDYY.csv`
- Simulates realistic usage patterns with:
  - 3-7 transactions per user per day (depending on user type)
  - 98% success rate (PASS/FAIL responses)
  - Random volume dispensing (100-600 mL per transaction)
  - Multiple client machines per kiosk
- Identifies ~5% of users as "abusive users" with higher daily limits

### Directory Structure After Generation

```
transactions/
├── kiosk_0001/
│   ├── kiosk_metadata.csv          # Kiosk metadata
│   ├── kiosk_user_pin.csv          # User database with PINs
│   ├── transactions_0001_101525.csv # Oct 15, 2025
│   ├── transactions_0001_101625.csv # Oct 16, 2025
│   └── ... (30 days of data)
├── kiosk_0002/
│   └── ...
└── ... (10 kiosks total)
```

### Configuration

To customize data generation, edit the configuration variables at the top of each script:

**generate_kiosk_users.py:**
- `NUM_KIOSKS` - Number of kiosks to create (default: 10)
- `MIN_USERS_PER_KIOSK` - Minimum users per kiosk (default: 50)
- `MAX_USERS_PER_KIOSK` - Maximum users per kiosk (default: 100)

**generate_transactions.py:**
- `NUM_DAYS` - Number of days of data (default: 30)
- `MIN_VOLUME_ML` - Minimum dispense volume (default: 100)
- `MAX_VOLUME_ML` - Maximum dispense volume (default: 600)
- `PASS_PERCENTAGE` - Percentage of successful transactions (default: 0.98 = 98%)

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

The dashboard will be on port 8888, analytics API on port 8082. Press `Ctrl+C` to stop either server.

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

### Requirements

Before using analytics, you must:
1. Run `generate_kiosk_users.py` to create kiosk user databases
2. Run `generate_transactions.py` to generate transaction CSV files
3. Run `analytics_api.py` in the virtual environment to start the backend API

### Usage

1. **Open the Dashboard**: Navigate to `http://localhost:8888/dashboard.html`
2. **Go to Analytics Tab**: Click the "Analytics" tab in the left sidebar
3. **View Top 3 Graphs** (automatically loaded):
   - **Total Water Dispensed Per Day** - Daily consumption across all kiosks
   - **Total Transactions Per Day** - Daily transaction count across all kiosks
   - **Usage by Day of Week** - Weekday vs weekend patterns
4. **Individual Kiosk Analysis**:
   - Select a kiosk from the dropdown
   - (Optional) Select a specific date, or leave empty for all days
   - Click "Load Kiosk Data"
5. **View Kiosk Visualizations**:
   - Key metrics (transactions, users, average volume, success rate)
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

The analytics tab uses dynamically generated transaction data:
- **10 Kiosks** with unique user databases
- **50-100 users per kiosk** with Ugandan phone numbers (708XXXXXX)
- **30 days of transaction history** (Oct 15 - Nov 13, 2025)
- **Realistic usage patterns**:
  - 3-7 transactions per user per day
  - 98% success rate (2% failures)
  - 100-600 mL per transaction
  - Multiple clients per kiosk
  - ~5% "abusive users" with higher consumption limits

Generated data is stored as CSV files in the `transactions/kiosk_XXXX/` directories.

The **Dashboard** and **Users** tabs use hardcoded sample data. To connect them to real data, update the JavaScript with API calls to your backend services.

## API Integration

### Analytics API (Port 8082)

The analytics tab uses real API endpoints for processing transaction data:

```
GET /api/analytics/health - Health check endpoint
GET /api/analytics/kiosks - List all available kiosks
GET /api/analytics/kiosk/<kiosk_id>/dates - Get available dates for a kiosk
GET /api/analytics/aggregated - All-kiosk daily and weekday aggregation (for top 3 graphs)
GET /api/analytics/kiosk/<kiosk_id>?date=all - All data for a specific kiosk
GET /api/analytics/kiosk/<kiosk_id>?date=YYYY-MM-DD - Single day data for a kiosk
```

**Example Usage:**
```bash
# Get list of all kiosks
curl http://localhost:8082/api/analytics/kiosks

# Get available dates for kiosk 0001
curl http://localhost:8082/api/analytics/kiosk/0001/dates

# Get all data for kiosk 0001
curl http://localhost:8082/api/analytics/kiosk/0001?date=all

# Get single day data (2025-10-15) for kiosk 0001
curl http://localhost:8082/api/analytics/kiosk/0001?date=2025-10-15
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

### "No kiosks found" in Analytics
- You must run the transaction data generation scripts first:
  ```bash
  cd transactions
  python3 generate_kiosk_users.py
  python3 generate_transactions.py
  ```
- Verify kiosk directories were created in `transactions/` directory

### "Error loading kiosks"
- Check that analytics_api.py server is running on port 8082
- Verify the virtual environment is activated before running analytics_api.py
- Check browser console for detailed error messages

### Charts not displaying or showing "NaN"
- Ensure transaction data was generated successfully (run both generation scripts)
- Verify analytics_api.py is running and accessible at http://localhost:8082/api/analytics/health
- Check browser console for JavaScript errors
- Try refreshing the page

### Port already in use
If port 8082 or 8888 is already in use:
- Edit `analytics_api.py` line 395: change `port=8082`
- Edit `serve.py` and modify the port

### Memory issues with large datasets
- Large transaction files may consume significant memory
- Consider reducing `NUM_DAYS` in `generate_transactions.py` if memory is limited

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
