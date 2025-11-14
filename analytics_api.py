#!/usr/bin/env python3
"""
Analytics API for Water Kiosk Transaction Data
Processes CSV files and provides aggregated analytics data via REST API
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import csv
import glob
from datetime import datetime
from collections import defaultdict
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
CSV_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
CSV_PATTERN = 'transactions*.csv'

def process_csv_file(file_path):
    """Process a single CSV file and return aggregated data"""
    user_volumes = defaultdict(float)
    user_access_count = defaultdict(int)
    total_transactions = 0
    pass_count = 0
    fail_count = 0
    kiosk_activity = defaultdict(int)
    volume_distribution = defaultdict(int)
    individual_volumes = []

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    user_id = row.get('User_ID', '').strip()
                    volume = float(row.get('Volume_ML', 0))
                    response = row.get('Response', '').strip().upper()
                    client = row.get('Client_Name', '').strip()

                    if user_id and volume >= 0:
                        user_volumes[user_id] += volume
                        user_access_count[user_id] += 1
                        total_transactions += 1
                        individual_volumes.append(volume)

                        # Categorize volume for distribution (100ml ranges)
                        if volume <= 100:
                            volume_distribution['0-100ml'] += 1
                        elif volume <= 200:
                            volume_distribution['101-200ml'] += 1
                        elif volume <= 300:
                            volume_distribution['201-300ml'] += 1
                        elif volume <= 400:
                            volume_distribution['301-400ml'] += 1
                        elif volume <= 500:
                            volume_distribution['401-500ml'] += 1
                        elif volume <= 600:
                            volume_distribution['501-600ml'] += 1
                        elif volume <= 700:
                            volume_distribution['601-700ml'] += 1
                        elif volume <= 800:
                            volume_distribution['701-800ml'] += 1
                        elif volume <= 900:
                            volume_distribution['801-900ml'] += 1
                        elif volume <= 1000:
                            volume_distribution['901-1000ml'] += 1
                        else:
                            volume_distribution['1000ml+'] += 1

                        if response == 'PASS':
                            pass_count += 1
                        else:
                            fail_count += 1

                        if client:
                            kiosk_activity[client] += 1
                except (ValueError, KeyError):
                    continue

    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return None

    if total_transactions == 0:
        return None

    success_rate = (pass_count / total_transactions * 100) if total_transactions > 0 else 0
    average_volume = sum(user_volumes.values()) / len(user_volumes) if user_volumes else 0
    average_access_count = sum(user_access_count.values()) / len(user_access_count) if user_access_count else 0
    total_volume = sum(user_volumes.values())

    return {
        'user_volumes': dict(user_volumes),
        'user_access_count': dict(user_access_count),
        'total_transactions': total_transactions,
        'pass_count': pass_count,
        'fail_count': fail_count,
        'success_rate': round(success_rate, 2),
        'average_volume': round(average_volume, 2),
        'average_access_count': round(average_access_count, 2),
        'kiosk_activity': dict(kiosk_activity),
        'total_volume': round(total_volume, 2),
        'unique_users': len(user_volumes),
        'volume_distribution': dict(volume_distribution),
        'individual_volumes': individual_volumes
    }

def get_available_files():
    """Get list of available CSV files"""
    pattern = os.path.join(CSV_DIRECTORY, CSV_PATTERN)
    files = glob.glob(pattern)

    file_info = []
    for file_path in sorted(files, reverse=True):
        try:
            stat = os.stat(file_path)
            file_info.append({
                'name': os.path.basename(file_path),
                'path': file_path,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
        except:
            continue

    return file_info

@app.route('/api/analytics/files', methods=['GET'])
def get_files():
    """Get list of available CSV files"""
    files = get_available_files()
    return jsonify(files)

@app.route('/api/analytics/analyze', methods=['GET'])
def analyze_data():
    """Analyze selected CSV file(s)"""
    file_names = request.args.getlist('files')

    if not file_names:
        # Default to most recent file
        available_files = get_available_files()
        if available_files:
            file_names = [available_files[0]['name']]
        else:
            return jsonify({'error': 'No CSV files found'}), 404

    # Combine data from multiple files
    combined_data = {
        'user_volumes': defaultdict(float),
        'user_access_count': defaultdict(int),
        'total_transactions': 0,
        'pass_count': 0,
        'fail_count': 0,
        'kiosk_activity': defaultdict(int),
        'volume_distribution': defaultdict(int),
        'individual_volumes': [],
        'files_processed': []
    }

    for file_name in file_names:
        file_path = os.path.join(CSV_DIRECTORY, file_name)
        if os.path.exists(file_path):
            data = process_csv_file(file_path)
            if data:
                for user_id, volume in data['user_volumes'].items():
                    combined_data['user_volumes'][user_id] += volume

                for user_id, count in data['user_access_count'].items():
                    combined_data['user_access_count'][user_id] += count

                combined_data['total_transactions'] += data['total_transactions']
                combined_data['pass_count'] += data['pass_count']
                combined_data['fail_count'] += data['fail_count']

                for kiosk, count in data['kiosk_activity'].items():
                    combined_data['kiosk_activity'][kiosk] += count

                for vol_range, count in data['volume_distribution'].items():
                    combined_data['volume_distribution'][vol_range] += count

                combined_data['individual_volumes'].extend(data['individual_volumes'])
                combined_data['files_processed'].append(file_name)

    if combined_data['total_transactions'] == 0:
        return jsonify({'error': 'No valid transaction data found'}), 404

    # Calculate metrics
    success_rate = (combined_data['pass_count'] / combined_data['total_transactions'] * 100) if combined_data['total_transactions'] > 0 else 0
    average_volume = sum(combined_data['user_volumes'].values()) / len(combined_data['user_volumes']) if combined_data['user_volumes'] else 0
    average_access_count = sum(combined_data['user_access_count'].values()) / len(combined_data['user_access_count']) if combined_data['user_access_count'] else 0

    # Prepare top users
    user_volumes = dict(combined_data['user_volumes'])
    user_access_count = dict(combined_data['user_access_count'])
    sorted_users_volume = sorted(user_volumes.items(), key=lambda x: x[1], reverse=True)[:20]
    sorted_users_access = sorted(user_access_count.items(), key=lambda x: x[1], reverse=True)[:20]

    # Prepare kiosk data
    kiosk_activity = dict(combined_data['kiosk_activity'])
    sorted_kiosks = sorted(kiosk_activity.items(), key=lambda x: x[1], reverse=True)

    result = {
        'files_processed': combined_data['files_processed'],
        'summary': {
            'total_transactions': combined_data['total_transactions'],
            'unique_users': len(combined_data['user_volumes']),
            'total_volume': round(sum(combined_data['user_volumes'].values()), 2),
            'success_rate': round(success_rate, 2),
            'pass_count': combined_data['pass_count'],
            'fail_count': combined_data['fail_count'],
            'average_volume': round(average_volume, 2),
            'average_access_count': round(average_access_count, 2)
        },
        'top_users_by_volume': {
            'labels': [user[0] for user in sorted_users_volume],
            'data': [user[1] for user in sorted_users_volume]
        },
        'top_users_by_frequency': {
            'labels': [user[0] for user in sorted_users_access],
            'data': [user[1] for user in sorted_users_access]
        },
        'volume_distribution': dict(combined_data['volume_distribution']),
        'kiosk_activity': {
            'labels': [kiosk[0] for kiosk in sorted_kiosks],
            'data': [kiosk[1] for kiosk in sorted_kiosks]
        }
    }

    return jsonify(result)

@app.route('/api/analytics/daily-trends', methods=['GET'])
def daily_trends():
    """Analyze trends across multiple days"""
    files = get_available_files()

    if not files:
        return jsonify({'error': 'No CSV files found'}), 404

    daily_data = defaultdict(float)
    daily_transactions = defaultdict(int)

    # Process each file
    for file_info in files:
        file_path = file_info['path']
        # Extract date from filename (transactions_MMDDYY.csv)
        filename = file_info['name']
        try:
            # Parse filename like transactions_110625.csv -> 11/06/25
            date_part = filename.replace('transactions_', '').replace('.csv', '')
            if len(date_part) == 6:
                month = date_part[:2]
                day = date_part[2:4]
                year = date_part[4:6]
                date_str = f"20{year}-{month}-{day}"  # 2025-11-06 format
            else:
                continue

            data = process_csv_file(file_path)
            if data:
                daily_data[date_str] = data['total_volume']
                daily_transactions[date_str] = data['total_transactions']
        except:
            continue

    # Sort by date
    sorted_dates = sorted(daily_data.keys())
    volumes = [daily_data[date] for date in sorted_dates]
    transactions = [daily_transactions[date] for date in sorted_dates]

    # Format dates for display
    display_dates = [date.replace('20', '') for date in sorted_dates]  # 25-11-06

    return jsonify({
        'dates': sorted_dates,
        'display_dates': display_dates,
        'volumes': volumes,
        'transactions': transactions,
        'total_volume': sum(volumes),
        'total_transactions': sum(transactions),
        'average_daily_volume': round(sum(volumes) / len(volumes), 2) if volumes else 0,
        'average_daily_transactions': round(sum(transactions) / len(transactions), 2) if transactions else 0
    })

@app.route('/api/analytics/weekday-trends', methods=['GET'])
def weekday_trends():
    """Analyze usage patterns by day of week"""
    files = get_available_files()

    if not files:
        return jsonify({'error': 'No CSV files found'}), 404

    # Day of week aggregation
    weekday_volumes = defaultdict(float)
    weekday_transactions = defaultdict(int)
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Process each file
    for file_info in files:
        file_path = file_info['path']
        filename = file_info['name']
        try:
            # Parse filename like transactions_110625.csv -> 11/06/25
            date_part = filename.replace('transactions_', '').replace('.csv', '')
            if len(date_part) == 6:
                month = date_part[:2]
                day = date_part[2:4]
                year = date_part[4:6]
                date_str = f"20{year}-{month}-{day}"

                # Get day of week (0=Monday, 6=Sunday)
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                day_of_week = date_obj.weekday()
                day_name = day_names[day_of_week]

                data = process_csv_file(file_path)
                if data:
                    weekday_volumes[day_name] += data['total_volume']
                    weekday_transactions[day_name] += data['total_transactions']
        except:
            continue

    # Prepare output in day order
    result = {
        'days': [],
        'volumes': [],
        'transactions': [],
        'total_volume': sum(weekday_volumes.values()),
        'total_transactions': sum(weekday_transactions.values()),
        'average_volume_by_day': {},
        'average_transactions_by_day': {}
    }

    for day_name in day_names:
        if day_name in weekday_volumes:
            result['days'].append(day_name)
            result['volumes'].append(round(weekday_volumes[day_name], 2))
            result['transactions'].append(weekday_transactions[day_name])
            result['average_volume_by_day'][day_name] = round(weekday_volumes[day_name], 2)
            result['average_transactions_by_day'][day_name] = weekday_transactions[day_name]

    return jsonify(result)

@app.route('/api/analytics/health', methods=['GET'])
def health():
    """Health check endpoint"""
    files = get_available_files()
    return jsonify({
        'status': 'ok',
        'csv_files_found': len(files),
        'directory': CSV_DIRECTORY
    })

if __name__ == '__main__':
    print("🚀 Starting Analytics API...")
    print(f"📁 CSV Directory: {CSV_DIRECTORY}")
    print(f"🔍 Looking for files: {CSV_PATTERN}")
    print(f"🌐 API will be available at: http://localhost:5000")
    print(f"📊 Available endpoints:")
    print(f"   - GET /api/analytics/files")
    print(f"   - GET /api/analytics/analyze?files=filename.csv")
    print(f"   - GET /api/analytics/daily-trends")
    print(f"   - GET /api/analytics/weekday-trends")
    print(f"   - GET /api/analytics/health")

    app.run(host='0.0.0.0', port=5000, debug=False)
