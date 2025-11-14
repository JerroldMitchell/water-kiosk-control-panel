#!/usr/bin/env python3
"""
Analytics API for Water Kiosk Transaction Data
Processes transaction CSV files from kiosk directories and provides aggregated analytics data via REST API
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import csv
from datetime import datetime
from collections import defaultdict
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
TRANSACTIONS_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'transactions')

# ============================================================================
# DIRECTORY & FILE DISCOVERY
# ============================================================================

def get_kiosk_directories():
    """Discover all kiosk directories in transactions/"""
    kiosks = []

    if not os.path.exists(TRANSACTIONS_DIRECTORY):
        return kiosks

    for item in os.listdir(TRANSACTIONS_DIRECTORY):
        item_path = os.path.join(TRANSACTIONS_DIRECTORY, item)
        if os.path.isdir(item_path) and item.startswith('kiosk_'):
            kiosk_id = item.replace('kiosk_', '')
            kiosks.append(kiosk_id)

    return sorted(kiosks)


def get_dates_for_kiosk(kiosk_id):
    """Get available dates for a specific kiosk by scanning transaction files"""
    dates = set()
    kiosk_dir = os.path.join(TRANSACTIONS_DIRECTORY, f'kiosk_{kiosk_id}')

    if not os.path.exists(kiosk_dir):
        return sorted(list(dates))

    # Look for files like: transactions_0202_110625.csv
    for filename in os.listdir(kiosk_dir):
        if filename.startswith('transactions_') and filename.endswith('.csv'):
            # Extract date from filename: transactions_KIOSK_MMDDYY.csv
            match = re.match(r'transactions_\d+_(\d{6})\.csv', filename)
            if match:
                date_str = match.group(1)
                try:
                    month = date_str[:2]
                    day = date_str[2:4]
                    year = date_str[4:6]
                    date_obj = datetime.strptime(f"20{year}-{month}-{day}", '%Y-%m-%d')
                    dates.add(date_obj.strftime('%Y-%m-%d'))
                except:
                    continue

    return sorted(list(dates))


# ============================================================================
# CSV PROCESSING
# ============================================================================

def process_csv_file(file_path):
    """Process a single CSV file and return aggregated data"""
    user_volumes = defaultdict(float)
    user_access_count = defaultdict(int)
    total_transactions = 0
    pass_count = 0
    fail_count = 0
    individual_volumes = []

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    user_id = row.get('User_ID', '').strip()
                    volume = float(row.get('Volume_ML', 0))
                    response = row.get('Response', '').strip().upper()

                    if user_id and volume >= 0:
                        user_volumes[user_id] += volume
                        user_access_count[user_id] += 1
                        total_transactions += 1
                        individual_volumes.append(volume)

                        if response == 'PASS':
                            pass_count += 1
                        else:
                            fail_count += 1

                except (ValueError, KeyError):
                    continue

    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return None

    if total_transactions == 0:
        return None

    success_rate = (pass_count / total_transactions * 100) if total_transactions > 0 else 0
    total_volume = sum(user_volumes.values())

    return {
        'user_volumes': dict(user_volumes),
        'user_access_count': dict(user_access_count),
        'total_transactions': total_transactions,
        'pass_count': pass_count,
        'fail_count': fail_count,
        'success_rate': round(success_rate, 2),
        'total_volume': round(total_volume, 2),
        'unique_users': len(user_volumes),
        'individual_volumes': individual_volumes
    }


def load_transaction_file(kiosk_id, date):
    """Load raw transaction data from a specific file"""
    kiosk_dir = os.path.join(TRANSACTIONS_DIRECTORY, f'kiosk_{kiosk_id}')

    # Convert date format YYYY-MM-DD to MMDDYY for filename
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        date_file_str = date_obj.strftime('%m%d%y')
    except:
        return None

    filename = f'transactions_{kiosk_id}_{date_file_str}.csv'
    file_path = os.path.join(kiosk_dir, filename)

    if not os.path.exists(file_path):
        return None

    transactions = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                transactions.append({
                    'time': row.get('Timestamp', '').strip(),
                    'client': row.get('Client_Name', '').strip(),
                    'user_id': row.get('User_ID', '').strip(),
                    'volume_ml': int(row.get('Volume_ML', 0)),
                    'response': row.get('Response', '').strip()
                })
    except:
        return None

    return transactions


# ============================================================================
# DATA AGGREGATION
# ============================================================================

def aggregate_all_kiosks_daily():
    """Aggregate daily data from all kiosks"""
    daily_data = defaultdict(lambda: {
        'total_volume_ml': 0,
        'total_transactions': 0,
        'total_users': set(),
        'pass_count': 0,
        'fail_count': 0
    })

    kiosks = get_kiosk_directories()
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_data = defaultdict(lambda: {
        'total_volume_ml': 0,
        'total_transactions': 0
    })

    for kiosk_id in kiosks:
        dates = get_dates_for_kiosk(kiosk_id)

        for date in dates:
            kiosk_dir = os.path.join(TRANSACTIONS_DIRECTORY, f'kiosk_{kiosk_id}')
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            date_file_str = date_obj.strftime('%m%d%y')
            filename = f'transactions_{kiosk_id}_{date_file_str}.csv'
            file_path = os.path.join(kiosk_dir, filename)

            if os.path.exists(file_path):
                data = process_csv_file(file_path)
                if data:
                    daily_data[date]['total_volume_ml'] += data['total_volume']
                    daily_data[date]['total_transactions'] += data['total_transactions']
                    daily_data[date]['total_users'].update(data['user_volumes'].keys())
                    daily_data[date]['pass_count'] += data['pass_count']
                    daily_data[date]['fail_count'] += data['fail_count']

                    # Aggregate by day of week
                    day_name = day_names[date_obj.weekday()]
                    weekday_data[day_name]['total_volume_ml'] += data['total_volume']
                    weekday_data[day_name]['total_transactions'] += data['total_transactions']

    # Convert sets to counts and sort by date
    sorted_daily = []
    for date in sorted(daily_data.keys()):
        entry = daily_data[date]
        sorted_daily.append({
            'date': date,
            'total_volume_ml': round(entry['total_volume_ml'], 2),
            'total_transactions': entry['total_transactions'],
            'total_users': len(entry['total_users']),
            'pass_count': entry['pass_count'],
            'fail_count': entry['fail_count']
        })

    return sorted_daily, weekday_data


def aggregate_kiosk_data(kiosk_id, period='all', date=None):
    """Aggregate data for a specific kiosk"""
    kiosk_dir = os.path.join(TRANSACTIONS_DIRECTORY, f'kiosk_{kiosk_id}')

    if not os.path.exists(kiosk_dir):
        return None

    if period == 'all':
        # Aggregate all days for this kiosk
        dates = get_dates_for_kiosk(kiosk_id)
        daily_data = []
        summary = {
            'total_volume_ml': 0,
            'total_transactions': 0,
            'unique_users': set(),
            'total_pass': 0,
            'total_fail': 0
        }

        for date in dates:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            date_file_str = date_obj.strftime('%m%d%y')
            filename = f'transactions_{kiosk_id}_{date_file_str}.csv'
            file_path = os.path.join(kiosk_dir, filename)

            if os.path.exists(file_path):
                data = process_csv_file(file_path)
                if data:
                    daily_data.append({
                        'date': date,
                        'volume_ml': round(data['total_volume'], 2),
                        'transactions': data['total_transactions'],
                        'users': len(data['user_volumes']),
                        'pass_count': data['pass_count'],
                        'fail_count': data['fail_count']
                    })

                    summary['total_volume_ml'] += data['total_volume']
                    summary['total_transactions'] += data['total_transactions']
                    summary['unique_users'].update(data['user_volumes'].keys())
                    summary['total_pass'] += data['pass_count']
                    summary['total_fail'] += data['fail_count']

        return {
            'kiosk_id': kiosk_id,
            'period': 'all',
            'daily': daily_data,
            'summary': {
                'total_volume_ml': round(summary['total_volume_ml'], 2),
                'total_transactions': summary['total_transactions'],
                'unique_users': len(summary['unique_users']),
                'total_pass': summary['total_pass'],
                'total_fail': summary['total_fail']
            }
        }

    elif period == 'single' and date:
        # Single day for this kiosk
        transactions = load_transaction_file(kiosk_id, date)
        if not transactions:
            return None

        # Calculate summary
        total_volume = sum(t['volume_ml'] for t in transactions)
        unique_users = len(set(t['user_id'] for t in transactions))
        pass_count = sum(1 for t in transactions if t['response'] == 'PASS')
        fail_count = sum(1 for t in transactions if t['response'] == 'FAIL')

        return {
            'kiosk_id': kiosk_id,
            'date': date,
            'transactions': transactions,
            'summary': {
                'total_volume_ml': round(total_volume, 2),
                'total_transactions': len(transactions),
                'unique_users': unique_users,
                'pass_count': pass_count,
                'fail_count': fail_count
            }
        }

    return None


# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/api/analytics/kiosks', methods=['GET'])
def get_kiosks():
    """Get list of available kiosks"""
    kiosks = get_kiosk_directories()
    return jsonify({
        'kiosks': [{'id': kiosk_id, 'name': f'Kiosk {kiosk_id}'} for kiosk_id in kiosks]
    })


@app.route('/api/analytics/kiosk/<kiosk_id>/dates', methods=['GET'])
def get_kiosk_dates(kiosk_id):
    """Get available dates for a specific kiosk"""
    dates = get_dates_for_kiosk(kiosk_id)
    return jsonify({
        'kiosk_id': kiosk_id,
        'dates': dates,
        'total_dates': len(dates)
    })


@app.route('/api/analytics/aggregated', methods=['GET'])
def get_aggregated():
    """Get aggregated data for all kiosks"""
    daily_data, weekday_data = aggregate_all_kiosks_daily()

    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Format weekday data
    weekday_result = {}
    for day_name in day_names:
        if day_name in weekday_data:
            weekday_result[day_name] = {
                'total_volume_ml': round(weekday_data[day_name]['total_volume_ml'], 2),
                'total_transactions': weekday_data[day_name]['total_transactions'],
                'days_included': sum(1 for d in daily_data if datetime.strptime(d['date'], '%Y-%m-%d').strftime('%A') == day_name)
            }

    return jsonify({
        'daily': daily_data,
        'by_day_of_week': weekday_result
    })


@app.route('/api/analytics/kiosk/<kiosk_id>', methods=['GET'])
def get_kiosk_data(kiosk_id):
    """Get data for a specific kiosk (all data or single day)"""
    date = request.args.get('date')

    if date and date != 'all':
        # Single day
        result = aggregate_kiosk_data(kiosk_id, period='single', date=date)
    else:
        # All data
        result = aggregate_kiosk_data(kiosk_id, period='all')

    if result is None:
        return jsonify({'error': f'No data found for kiosk {kiosk_id}'}), 404

    return jsonify(result)


@app.route('/api/analytics/health', methods=['GET'])
def health():
    """Health check endpoint"""
    kiosks = get_kiosk_directories()
    return jsonify({
        'status': 'ok',
        'kiosks_found': len(kiosks),
        'directory': TRANSACTIONS_DIRECTORY
    })


if __name__ == '__main__':
    print("🚀 Starting Analytics API...")
    print(f"📁 Transactions Directory: {TRANSACTIONS_DIRECTORY}")
    print(f"🌐 API will be available at: http://localhost:8082")
    print(f"📊 Available endpoints:")
    print(f"   - GET /api/analytics/kiosks")
    print(f"   - GET /api/analytics/kiosk/<kiosk_id>/dates")
    print(f"   - GET /api/analytics/aggregated")
    print(f"   - GET /api/analytics/kiosk/<kiosk_id>?date=all")
    print(f"   - GET /api/analytics/kiosk/<kiosk_id>?date=YYYY-MM-DD")
    print(f"   - GET /api/analytics/health")

    app.run(host='0.0.0.0', port=8082, debug=False)
