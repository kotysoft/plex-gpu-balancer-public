#!/usr/bin/env python3
"""Standalone GPU Metrics Collector Service with Historical Data API"""

import time
import logging
import sys
import os
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS

# Add src directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import monitoring systems
from gpu_metrics import (
    start_gpu_metrics_collector, stop_gpu_metrics_collector,
    get_all_gpu_metrics, get_device_metrics, get_active_device_metrics,
    get_summary_stats, start_background_workers, stop_background_workers
)

from historical_gpu_data import (
    start_historical_data_collector, stop_historical_data_collector,
    get_all_devices_historical_matrix, get_device_historical_matrix,
    get_data_availability
)

# Import individual GPU monitors
try:
    from intel_gpu_monitor import start_intel_monitor, stop_all_monitors as stop_intel_monitors
    INTEL_MONITOR_AVAILABLE = True
except ImportError:
    INTEL_MONITOR_AVAILABLE = False
    def start_intel_monitor():
        return False
    def stop_intel_monitors():
        pass

try:
    from nvidia_gpu_monitor import start_nvidia_monitor, stop_all_monitors as stop_nvidia_monitors
    NVIDIA_MONITOR_AVAILABLE = True
except ImportError:
    NVIDIA_MONITOR_AVAILABLE = False
    def start_nvidia_monitor():
        return False
    def stop_nvidia_monitors():
        pass

# Setup logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GPUCollectorService:
    """Standalone GPU metrics collection service"""
    
    def __init__(self):
        self.running = False
        self.intel_started = False
        self.nvidia_started = False
        self.collector_started = False
        self.historical_started = False
    
    def start_all_collectors(self):
        """Start all GPU monitoring collectors"""
        logger.info("🚀 Starting GPU Collector Service")
        
        # Start individual GPU device monitors FIRST
        if INTEL_MONITOR_AVAILABLE:
            logger.info("🔵 Starting Intel GPU Monitor...")
            self.intel_started = start_intel_monitor()
            if self.intel_started:
                logger.info("   ✅ Intel GPU Monitor started successfully")
                # Give it time to start collecting data
                time.sleep(2)
            else:
                logger.warning("   ⚠️  Intel GPU Monitor failed to start")
        else:
            logger.info("🔵 Intel GPU Monitor not available")
        
        if NVIDIA_MONITOR_AVAILABLE:
            logger.info("🟢 Starting NVIDIA GPU Monitor...")
            self.nvidia_started = start_nvidia_monitor()
            if self.nvidia_started:
                logger.info("   ✅ NVIDIA GPU Monitor started successfully")
                # Give it time to start collecting data
                time.sleep(2)
            else:
                logger.warning("   ⚠️  NVIDIA GPU Monitor failed to start")
        else:
            logger.info("🟢 NVIDIA GPU Monitor not available")
        
        # Start central GPU metrics collector AFTER individual monitors
        logger.info("⚡ Starting Central GPU Metrics Collector...")
        self.collector_started = start_background_workers()
        if self.collector_started:
            logger.info("   ✅ Central collector started successfully")
            # Give it time to start collecting from the individual monitors
            time.sleep(2)
        else:
            logger.warning("   ⚠️  Central collector failed to start")
        
        # Start historical data collector LAST
        logger.info("📊 Starting Historical GPU Data Collector...")
        self.historical_started = start_historical_data_collector()
        if self.historical_started:
            logger.info("   ✅ Historical data collector started successfully")
            time.sleep(1)
        else:
            logger.warning("   ⚠️  Historical data collector failed to start")
        
        self.running = True
        logger.info("🎯 GPU Collector Service fully initialized!")
        
        # Verify data collection is working
        logger.info("🔍 Verifying data collection...")
        time.sleep(3)  # Wait for first data cycle
        
        from gpu_metrics import get_all_gpu_metrics
        test_metrics = get_all_gpu_metrics()
        device_count = test_metrics.get('device_count', 0)
        
        if device_count > 0:
            logger.info(f"   ✅ Successfully collecting data from {device_count} GPU devices")
        else:
            logger.error("   ❌ No GPU devices detected - checking individual monitors...")
            
            # Test individual monitors
            if INTEL_MONITOR_AVAILABLE:
                try:
                    from intel_gpu_monitor import get_all_intel_gpu_data
                    intel_data = get_all_intel_gpu_data()
                    if intel_data:
                        logger.info(f"   🔵 Intel monitor has {len(intel_data)} devices")
                    else:
                        logger.warning("   🔵 Intel monitor has no data")
                except Exception as e:
                    logger.error(f"   🔵 Intel monitor error: {e}")
            
            if NVIDIA_MONITOR_AVAILABLE:
                try:
                    from nvidia_gpu_monitor import get_all_nvidia_gpu_data
                    nvidia_data = get_all_nvidia_gpu_data()
                    if nvidia_data:
                        logger.info(f"   🟢 NVIDIA monitor has {len(nvidia_data)} devices")
                    else:
                        logger.warning("   🟢 NVIDIA monitor has no data")
                except Exception as e:
                    logger.error(f"   🟢 NVIDIA monitor error: {e}")
        
        return True
    
    def stop_all_collectors(self):
        """Stop all GPU monitoring collectors"""
        logger.info("🛑 Stopping GPU Collector Service...")
        
        # Stop all monitors
        if self.intel_started:
            try:
                stop_intel_monitors()
                logger.info("   ✅ Intel GPU monitors stopped")
            except Exception as e:
                logger.error(f"   ❌ Error stopping Intel monitors: {e}")
        
        if self.nvidia_started:
            try:
                stop_nvidia_monitors()
                logger.info("   ✅ NVIDIA GPU monitors stopped")
            except Exception as e:
                logger.error(f"   ❌ Error stopping NVIDIA monitors: {e}")
        
        if self.collector_started:
            try:
                stop_background_workers()
                logger.info("   ✅ Central collector stopped")
            except Exception as e:
                logger.error(f"   ❌ Error stopping central collector: {e}")
        
        if self.historical_started:
            try:
                stop_historical_data_collector()
                logger.info("   ✅ Historical data collector stopped")
            except Exception as e:
                logger.error(f"   ❌ Error stopping historical collector: {e}")
        
        self.running = False
        logger.info("🏁 GPU Collector Service shutdown complete")
    
    def run_service(self):
        """Run the collector service"""
        if not self.start_all_collectors():
            logger.error("❌ Failed to start collectors")
            return
        
        try:
            logger.info("⚡ GPU Collector Service running - clients can now access data")
            while self.running:
                time.sleep(5)  # Keep service alive
                
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown signal received")
        finally:
            self.stop_all_collectors()

# Service instance
_gpu_service = None

def start_gpu_collector_service():
    """Start the standalone GPU collector service"""
    global _gpu_service
    if _gpu_service is None:
        _gpu_service = GPUCollectorService()
        return _gpu_service.start_all_collectors()
    return True

def stop_gpu_collector_service():
    """Stop the standalone GPU collector service"""
    global _gpu_service
    if _gpu_service is not None:
        _gpu_service.stop_all_collectors()
        _gpu_service = None

def is_gpu_collector_running():
    """Check if the GPU collector service is running (cross-process compatible)"""
    try:
        # Test if the monitoring components are actually working
        metrics = get_all_gpu_metrics()
        historical_data = get_all_devices_historical_matrix()
        
        # If we can get metrics and historical data, the service is running
        return (isinstance(metrics, dict) and 
                isinstance(historical_data, (dict, list)) and
                metrics.get('timestamp') is not None)
    except Exception:
        return False

# API functions for clients to use
def get_gpu_metrics():
    """Get all GPU metrics (client API)"""
    try:
        return get_all_gpu_metrics()
    except Exception as e:
        logger.error(f"❌ Error getting GPU metrics: {e}")
        return {'error': str(e)}

def get_device_load_data(device_id, timeframe_seconds=30):
    """Get device HISTORICAL AVERAGE load over timeframe (client API for balancer)"""
    try:
        # Use collector service API directly - centralized historical data!
        import requests
        from urllib.parse import quote
        from urllib3.util.retry import Retry
        from requests.adapters import HTTPAdapter
        
        try:
            # Create optimized session for internal API calls
            if not hasattr(get_device_load_data, 'session'):
                get_device_load_data.session = requests.Session()
                
                # Configure retry strategy for internal calls
                retry_strategy = Retry(
                    total=2,
                    backoff_factor=0.05,
                    status_forcelist=[500, 502, 503, 504],
                )
                
                # Configure HTTP adapter with connection pooling
                adapter = HTTPAdapter(
                    max_retries=retry_strategy,
                    pool_connections=5,
                    pool_maxsize=5,
                    pool_block=False
                )
                
                get_device_load_data.session.mount("http://", adapter)
                get_device_load_data.session.timeout = (2, 5)  # Faster internal timeouts
            
            # URL encode the device ID for the API call
            encoded_device_id = quote(device_id, safe='')
            collector_url = f'http://localhost:8081/api/device-load/{encoded_device_id}/{timeframe_seconds}'
            
            response = get_device_load_data.session.get(collector_url)
            if response.status_code == 200:
                data = response.json()
                load_percent = data.get('load_percent')
                
                if load_percent is not None:
                    return load_percent  # Already rounded by collector service
        
        except requests.RequestException:
            # Collector service not available, try local historical data (fallback)
            pass
        
        # Fallback: try local historical data directly
        try:
            from historical_gpu_data import get_historical_averages
            averages = get_historical_averages(device_id, timeframe_seconds)
            
            if averages and isinstance(averages, dict):
                highest_util = averages.get('highest', 0)
                if highest_util >= 0:  # Include zero values!
                    return round(highest_util, 2)
                
                main_load = averages.get('main_load', 0)
                if main_load >= 0:  # Include zero values!
                    return round(main_load, 2)
        except Exception:
            pass
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Error getting device load data for {device_id}: {e}")
        return None

def get_device_historical_data(device_id):
    """Get historical data for device (client API)"""
    try:
        return get_device_historical_matrix(device_id)
    except Exception as e:
        logger.error(f"❌ Error getting historical data for {device_id}: {e}")
        return []

# Flask API Server for Historical Data
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/historical-data')
def api_historical_data():
    """Get historical data matrix for ALL devices (dashboard bulk request)"""
    try:
        historical_matrix = get_all_devices_historical_matrix()
        return jsonify(historical_matrix)
    except Exception as e:
        logger.error(f"❌ Error getting historical data matrix: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/device-load/<device_id>/<int:timeframe_seconds>')
def api_device_load(device_id, timeframe_seconds):
    """Get specific device load for specific timeframe (balancer request)"""
    try:
        from urllib.parse import unquote
        decoded_device_id = unquote(device_id)
        
        # Use historical data directly 
        from historical_gpu_data import get_historical_averages
        averages = get_historical_averages(decoded_device_id, timeframe_seconds)
        
        if averages and isinstance(averages, dict):
            # Return highest utilization for load balancing decisions
            highest_util = averages.get('highest', 0)
            if highest_util >= 0:
                return jsonify({
                    'device_id': decoded_device_id,
                    'timeframe_seconds': timeframe_seconds,
                    'load_percent': round(highest_util, 2),
                    'timestamp': datetime.now().isoformat()
                })
            
            # Fallback to main_load
            main_load = averages.get('main_load', 0)
            if main_load >= 0:
                return jsonify({
                    'device_id': decoded_device_id,
                    'timeframe_seconds': timeframe_seconds,
                    'load_percent': round(main_load, 2),
                    'timestamp': datetime.now().isoformat()
                })
        
        return jsonify({
            'device_id': decoded_device_id,
            'timeframe_seconds': timeframe_seconds,
            'load_percent': None,
            'error': 'No historical data available',
            'timestamp': datetime.now().isoformat()
        }), 404
        
    except Exception as e:
        logger.error(f"❌ Error getting device load for {device_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def api_status():
    """Service status endpoint"""
    try:
        metrics = get_all_gpu_metrics()
        historical_available = bool(get_all_devices_historical_matrix())
        
        return jsonify({
            'status': 'running',
            'service': 'GPU Collector Service',
            'device_count': metrics.get('device_count', 0),
            'historical_data_available': historical_available,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

def run_api_server():
    """Run the Flask API server for historical data"""
    logger.info("🌐 Starting Historical Data API Server on 0.0.0.0:8081...")
    try:
        app.run(host='0.0.0.0', port=8081, debug=False, threaded=True)
    except Exception as e:
        logger.error(f"❌ Failed to start API server: {e}")

class GPUCollectorWithAPI(GPUCollectorService):
    """GPU Collector Service with Flask API server"""
    
    def __init__(self):
        super().__init__()
        self.api_thread = None
    
    def start_all_collectors(self):
        """Start collectors and API server"""
        # Start the collectors first
        success = super().start_all_collectors()
        
        if success:
            # Start API server in separate thread
            import threading
            self.api_thread = threading.Thread(target=run_api_server, daemon=True)
            self.api_thread.start()
            logger.info("   ✅ Historical Data API Server started on port 8081")
            time.sleep(1)  # Give API server time to start
        
        return success

if __name__ == "__main__":
    service = GPUCollectorWithAPI()
    service.run_service()
