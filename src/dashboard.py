#!/usr/bin/env python3
"""Main dashboard application for Plex GPU Load Balancer"""

from flask import Flask, render_template_string, jsonify
import sys
import os
from datetime import datetime
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# Add src directory to path for importing modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modular components
from import_helper import import_config, import_plex_api

# Import config functions
load_config = import_config()

# Import plex_api functions (we'll need to import individual functions as needed)
get_parsed_gpu_devices, load_available_devices = import_plex_api()

# Import additional plex_api functions directly (since import_helper doesn't have all of them)
from plex_api import (
    get_plex_status, get_current_gpu, 
    switch_to_device, switch_gpu_by_type, available_devices, get_debug_info, get_plex_settings,
    get_current_active_device, get_all_active_sessions
)
from gpu_metrics import get_gpu_metrics
from dashboard_template import get_dashboard_template
from balance_config import (
    load_balance_config, get_current_settings, update_settings, 
    refresh_gpu_devices, get_gpu_devices_mapping
)

# Import Intel GPU monitor if available
try:
    from intel_gpu_monitor import start_intel_monitor, get_intel_gpu_data, get_intel_process_count
    INTEL_MONITOR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Intel GPU Monitor not available: {e}")
    INTEL_MONITOR_AVAILABLE = False
    # Create dummy functions to prevent errors
    def start_intel_monitor():
        return False
    def get_intel_gpu_data():
        return None
    def get_intel_process_count():
        return 0

# Import NVIDIA GPU monitor if available
try:
    from nvidia_gpu_monitor import start_nvidia_monitor, get_nvidia_gpu_data, get_nvidia_process_count
    NVIDIA_MONITOR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  NVIDIA GPU Monitor not available: {e}")
    NVIDIA_MONITOR_AVAILABLE = False
    # Create dummy functions to prevent errors
    def start_nvidia_monitor():
        return False
    def get_nvidia_gpu_data():
        return None
    def get_nvidia_process_count():
        return 0

# Import standalone GPU collector service
from gpu_collector_service import (
    start_gpu_collector_service, stop_gpu_collector_service, is_gpu_collector_running,
    get_gpu_metrics as get_collector_gpu_metrics
)

# Import GPU metrics functions
from gpu_metrics import (
    get_all_gpu_metrics, get_device_metrics, get_active_device_metrics,
    get_summary_stats
)

# Import historical GPU data functions
from historical_gpu_data import (
    get_all_devices_historical_matrix, get_device_historical_matrix,
    get_data_availability
)

# Initialize Flask app
app = Flask(__name__)

# Load configuration
config = load_config()
PLEX_SERVER = config['PLEX_SERVER']
PLEX_TOKEN = config['PLEX_TOKEN']
VERSION = config['VERSION']

# Connection pooling for reduced API call overhead
session = requests.Session()

# Configure retry strategy
retry_strategy = Retry(
    total=3,
    backoff_factor=0.1,
    status_forcelist=[429, 500, 502, 503, 504],
)

# Configure HTTP adapter with connection pooling
adapter = HTTPAdapter(
    max_retries=retry_strategy,
    pool_connections=20,  # Pool of connections to maintain
    pool_maxsize=20,      # Maximum number of connections in the pool
    pool_block=False      # Don't block if pool is full
)

# Mount the adapter for HTTP and HTTPS
session.mount("http://", adapter)
session.mount("https://", adapter)

# Set default timeouts for all requests
session.timeout = (5, 10)  # (connect timeout, read timeout)

print("✅ HTTP connection pooling configured (20 connections, 3 retries)")

# Global state
switch_counter = 0

@app.route('/')
def dashboard():
    """Main dashboard route"""
    return render_template_string(get_dashboard_template())

@app.route('/api/status')
def api_status():
    """API endpoint for overall system status"""
    global switch_counter
    next_gpu = "NVIDIA" if switch_counter % 2 == 1 else "INTEL"
    return jsonify({
        'plex': get_plex_status(),
        'plex_server': PLEX_SERVER,
        'counter': switch_counter,
        'next_gpu': next_gpu,
        'version': VERSION,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/switch-device/<device_id>', methods=['POST'])
def switch_to_device_endpoint(device_id):
    """Switch to a specific device by device ID"""
    global switch_counter
    
    try:
        # URL decode the device ID
        from urllib.parse import unquote
        decoded_device_id = unquote(device_id)
        
        result = switch_to_device(decoded_device_id)
        
        if result['status'] == 'success':
            # Update counter based on device type
            if result['gpu_type'] == "NVIDIA":
                switch_counter = 1
            elif result['gpu_type'] == "INTEL":
                switch_counter = 0
            
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/switch/<gpu>', methods=['POST'])
def switch_gpu(gpu):
    """Switch to GPU by type (legacy endpoint)"""
    global switch_counter
    
    result = switch_gpu_by_type(gpu)
    
    if result['status'] == 'success':
        # Update counter based on manual switch
        switch_counter = 1 if gpu == 'nvidia' else 0
        return jsonify(result)
    else:
        return jsonify(result), 500

@app.route('/refresh-devices', methods=['POST'])
def refresh_devices():
    """Refresh available GPU devices from Plex"""
    devices = load_available_devices()
    return jsonify({
        'status': 'success', 
        'devices': devices,
        'count': len(devices)
    })

@app.route('/api/gpu-metrics')
def api_gpu_metrics():
    """Get GPU utilization metrics"""
    return jsonify(get_gpu_metrics())

@app.route('/api/debug')
def api_debug():
    """Debug endpoint for troubleshooting"""
    debug_info = get_debug_info()
    debug_info['version'] = VERSION
    return jsonify(debug_info)

@app.route('/api/plex-settings')
def api_plex_settings():
    """Get Plex server settings for dashboard display"""
    return jsonify(get_plex_settings())

@app.route('/api/plex-sessions')
def api_plex_sessions():
    """Get all active Plex sessions for visibility"""
    sessions = get_all_active_sessions()
    return jsonify({
        'status': 'success',
        'sessions': sessions,
        'count': len(sessions),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/gpu-devices')
def api_gpu_devices():
    """Get parsed GPU devices for individual containers"""
    devices = get_parsed_gpu_devices()
    active_device = get_current_active_device()
    
    return jsonify({
        'status': 'success',
        'devices': devices,
        'active_device': active_device,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/all-intel-gpu-data')
def api_all_intel_gpu_data():
    """Get data from ALL Intel GPU devices"""
    if not INTEL_MONITOR_AVAILABLE:
        return jsonify({'status': 'error', 'message': 'Intel GPU monitor not available'})
    
    try:
        from intel_gpu_monitor import get_all_intel_gpu_data
        all_data = get_all_intel_gpu_data()
        
        return jsonify({
            'status': 'success',
            'devices': all_data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/api/intel-process-count')
def api_intel_process_count():
    """Get process count from Intel GPU monitor"""
    if not INTEL_MONITOR_AVAILABLE:
        return jsonify({'status': 'error', 'message': 'Intel GPU monitor not available'})
    
    count = get_intel_process_count()
    return jsonify({
        'status': 'success',
        'process_count': count
    })

@app.route('/start-intel-monitor', methods=['POST'])
def start_intel_monitor_endpoint():
    """Start Intel GPU monitoring"""
    if not INTEL_MONITOR_AVAILABLE:
        return jsonify({'status': 'error', 'message': 'Intel GPU monitor not available'})
    
    success = start_intel_monitor()
    if success:
        return jsonify({'status': 'success', 'message': 'Intel GPU monitor started'})
    else:
        return jsonify({'status': 'error', 'message': 'Intel GPU monitor already running or failed to start'})

# NEW UNIFIED API ENDPOINTS

@app.route('/api/all-gpu-metrics')
def api_all_gpu_metrics():
    """Get unified metrics for ALL GPU devices from central collector"""
    return jsonify(get_all_gpu_metrics())

@app.route('/api/device-metrics/<device_id>')
def api_device_metrics(device_id):
    """Get metrics for a specific device"""
    from urllib.parse import unquote
    decoded_device_id = unquote(device_id)
    
    metrics = get_device_metrics(decoded_device_id)
    if metrics:
        return jsonify({
            'status': 'success',
            'device_id': decoded_device_id,
            'metrics': metrics
        })
    else:
        return jsonify({
            'status': 'not_found',
            'device_id': decoded_device_id,
            'message': 'Device not found or no data available'
        })

@app.route('/api/active-device-metrics')
def api_active_device_metrics():
    """Get metrics for the currently active Plex device"""
    metrics = get_active_device_metrics()
    if metrics:
        return jsonify({
            'status': 'success',
            'metrics': metrics
        })
    else:
        return jsonify({
            'status': 'no_active_device',
            'message': 'No active device found or no data available'
        })

@app.route('/api/summary-stats')
def api_summary_stats():
    """Get summary statistics across all GPU devices"""
    return jsonify(get_summary_stats())

@app.route('/api/nvidia-gpu-data')
def api_nvidia_gpu_data():
    """Get NVIDIA GPU data from the dedicated monitor"""
    if not NVIDIA_MONITOR_AVAILABLE:
        return jsonify({'status': 'error', 'message': 'NVIDIA GPU monitor not available'})
    
    data = get_nvidia_gpu_data()
    if data:
        return jsonify({
            'status': 'success',
            'data': data,
            'timestamp': data.get('timestamp')
        })
    else:
        return jsonify({
            'status': 'no_data',
            'message': 'No NVIDIA GPU data available yet'
        })

@app.route('/api/all-nvidia-gpu-data')
def api_all_nvidia_gpu_data():
    """Get data from ALL NVIDIA GPU devices"""
    if not NVIDIA_MONITOR_AVAILABLE:
        return jsonify({'status': 'error', 'message': 'NVIDIA GPU monitor not available'})
    
    try:
        from nvidia_gpu_monitor import get_all_nvidia_gpu_data
        all_data = get_all_nvidia_gpu_data()
        
        return jsonify({
            'status': 'success',
            'devices': all_data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

# BALANCE CONFIGURATION API ENDPOINTS

@app.route('/api/balance-settings')
def api_balance_settings():
    """Get current balance configuration settings"""
    try:
        settings = get_current_settings()
        return jsonify({
            'status': 'success',
            'settings': settings,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/balance-settings', methods=['POST'])
def api_update_balance_settings():
    """Update balance configuration settings"""
    try:
        from flask import request
        import subprocess
        settings_data = request.get_json()
        
        if not settings_data:
            return jsonify({
                'status': 'error',
                'message': 'No settings data provided'
            }), 400
        
        success = update_settings(settings_data)
        
        if success:
            # Check if auto_restart_service is enabled
            current_settings = get_current_settings()
            auto_restart = current_settings.get('system', {}).get('auto_restart_service', True)
            
            response_data = {
                'status': 'success',
                'message': 'Balance settings updated successfully',
                'timestamp': datetime.now().isoformat()
            }
            
            # If auto_restart_service is enabled, restart the plex-balancer service
            if auto_restart:
                try:
                    # Try to restart the plex-balancer service
                    result = subprocess.run(
                        ['systemctl', 'restart', 'plex-balancer'], 
                        capture_output=True, 
                        text=True, 
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        response_data['message'] += ' - Service restarted successfully'
                        response_data['service_restarted'] = True
                    else:
                        response_data['message'] += f' - Service restart failed: {result.stderr}'
                        response_data['service_restarted'] = False
                        
                except subprocess.TimeoutExpired:
                    response_data['message'] += ' - Service restart timed out'
                    response_data['service_restarted'] = False
                except Exception as restart_error:
                    response_data['message'] += f' - Service restart error: {str(restart_error)}'
                    response_data['service_restarted'] = False
            else:
                response_data['message'] += ' - Auto-restart disabled'
                response_data['service_restarted'] = False
            
            return jsonify(response_data)
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to update balance settings'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error updating settings: {str(e)}'
        }), 500

@app.route('/api/refresh-balance-devices', methods=['POST'])
def api_refresh_balance_devices():
    """Refresh GPU devices in balance configuration"""
    try:
        success = refresh_gpu_devices()
        
        if success:
            # Get updated settings to return
            settings = get_current_settings()
            return jsonify({
                'status': 'success',
                'message': 'GPU devices refreshed successfully',
                'settings': settings,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to refresh GPU devices'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error refreshing devices: {str(e)}'
        }), 500

# REMOVED: Historical data endpoints now handled directly by collector service
# Frontend should call collector service at localhost:8081/api/historical-data directly

if __name__ == '__main__':
    print(f"🎮 Starting Plex GPU Load Balancer Dashboard v{VERSION}")
    print(f"📡 Monitoring Plex Server: {PLEX_SERVER}")
    print("🎯 Dashboard optimized for 500ms responsive updates")
    print("")
    
    # Start standalone GPU collector service
    print("⚡ Starting GPU Collector Service...")
    collector_started = start_gpu_collector_service()
    if collector_started:
        print("   ✅ GPU Collector Service started successfully")
    else:
        print("   ⚠️  GPU Collector Service failed to start")
    
    print("")
    print("🚀 Dashboard initialized!")
    
    try:
        app.run(host='0.0.0.0', port=8080, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down dashboard...")
        
        # Stop GPU collector service
        if collector_started:
            stop_gpu_collector_service()
            print("   ✅ GPU Collector Service stopped")
        
        print("🏁 Shutdown complete")
