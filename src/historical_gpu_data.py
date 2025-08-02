#!/usr/bin/env python3
"""
Historical GPU Data Collection Service
Collects and stores historical GPU metrics for trending analysis
"""

import threading
import time
from datetime import datetime, timedelta
from collections import deque
from typing import Dict, List, Optional

# Import gpu_metrics at module level to avoid circular import issues
import gpu_metrics

# Global data storage - in memory circular buffers
_nvidia_historical_data = {}  # device_id -> deque of metrics
_intel_historical_data = {}   # device_id -> deque of metrics
_data_lock = threading.Lock()
_collector_running = False
_collector_thread = None

# Configuration
MAX_DATA_POINTS = 600  # 10 minutes at 1 second intervals
COLLECTION_INTERVAL = 1  # seconds

class GPUDataPoint:
    """Represents a single GPU data point at a specific time"""
    def __init__(self, timestamp: datetime, metrics: dict):
        self.timestamp = timestamp
        self.metrics = metrics

def start_historical_data_collector():
    """Start the historical data collector"""
    global _collector_running, _collector_thread
    
    if _collector_running:
        return True
        
    _collector_running = True
    _collector_thread = threading.Thread(target=_historical_collector_worker, daemon=True)
    _collector_thread.start()
    return True

def stop_historical_data_collector():
    """Stop the historical data collector"""
    global _collector_running
    _collector_running = False

def _historical_collector_worker():
    """Worker thread that collects historical data"""
    global _collector_running, _nvidia_historical_data, _intel_historical_data
    
    while _collector_running:
        try:
            current_time = datetime.now()
            
            # Collect current GPU metrics
            current_metrics = gpu_metrics.get_all_gpu_metrics()
            
            with _data_lock:
                for device_id, device_data in current_metrics.get('devices', {}).items():
                    device_type = device_data.get('device_type', 'unknown')
                    
                    # Create data point
                    data_point = GPUDataPoint(current_time, device_data)
                    
                    # Store in appropriate historical buffer
                    if device_type == 'nvidia':
                        if device_id not in _nvidia_historical_data:
                            _nvidia_historical_data[device_id] = deque(maxlen=MAX_DATA_POINTS)
                        _nvidia_historical_data[device_id].append(data_point)
                        
                    elif device_type == 'intel':
                        if device_id not in _intel_historical_data:
                            _intel_historical_data[device_id] = deque(maxlen=MAX_DATA_POINTS)
                        _intel_historical_data[device_id].append(data_point)
            
            time.sleep(COLLECTION_INTERVAL)
            
        except Exception as e:
            # Continue running even if there's an error
            time.sleep(COLLECTION_INTERVAL)

def _calculate_average_metrics(data_points: List[GPUDataPoint], device_type: str) -> dict:
    """Calculate average metrics for a set of data points"""
    if not data_points:
        return {}
    
    if device_type == 'nvidia':
        # NVIDIA metrics to track
        metrics = {
            'main_load': [],
            'gpu_util': [],
            'memory_util': [],
            'encoder_util': [],
            'decoder_util': []
        }
        
        for point in data_points:
            metrics['main_load'].append(point.metrics.get('utilization_percent', 0))
            metrics['gpu_util'].append(point.metrics.get('utilization_percent', 0))
            metrics['memory_util'].append(point.metrics.get('memory_utilization_percent', 0))
            metrics['encoder_util'].append(point.metrics.get('vendor_specific', {}).get('encoder_utilization_percent', 0))
            metrics['decoder_util'].append(point.metrics.get('vendor_specific', {}).get('decoder_utilization_percent', 0))
        
        # Calculate averages
        averages = {}
        for key, values in metrics.items():
            averages[key] = sum(values) / len(values) if values else 0
        
        # Calculate highest value
        averages['highest'] = max([
            averages.get('gpu_util', 0),
            averages.get('memory_util', 0),
            averages.get('encoder_util', 0),
            averages.get('decoder_util', 0)
        ])
        
        return averages
        
    elif device_type == 'intel':
        # Intel metrics to track
        metrics = {
            'main_load': [],
            'render_util': [],
            'video_util': [],
            'video_enhance_util': []
        }
        
        for point in data_points:
            main_util = point.metrics.get('utilization_percent', 0)
            engines = point.metrics.get('vendor_specific', {}).get('engines', {})
            
            metrics['main_load'].append(main_util)
            metrics['render_util'].append(engines.get('render_3d_percent', 0))
            metrics['video_util'].append(engines.get('video_percent', 0))
            metrics['video_enhance_util'].append(engines.get('video_enhance_percent', 0))
        
        # Calculate averages
        averages = {}
        for key, values in metrics.items():
            averages[key] = sum(values) / len(values) if values else 0
        
        # Calculate highest value
        averages['highest'] = max([
            averages.get('render_util', 0),
            averages.get('video_util', 0),
            averages.get('video_enhance_util', 0)
        ])
        
        return averages
    
    return {}

def get_historical_averages(device_id: str, timeframe_seconds: int) -> dict:
    """Get average metrics for a device over a specific timeframe"""
    global _nvidia_historical_data, _intel_historical_data
    
    cutoff_time = datetime.now() - timedelta(seconds=timeframe_seconds)
    
    try:
        # Use timeout to prevent deadlock
        if _data_lock.acquire(timeout=0.5):
            try:
                # Determine device type and get data
                device_data = None
                device_type = None
                
                if device_id in _nvidia_historical_data:
                    device_data = list(_nvidia_historical_data[device_id])  # Create copy
                    device_type = 'nvidia'
                elif device_id in _intel_historical_data:
                    device_data = list(_intel_historical_data[device_id])  # Create copy
                    device_type = 'intel'
            finally:
                _data_lock.release()
            
            if not device_data or not device_type:
                return {}
            
            # Filter data points within timeframe (now outside lock)
            relevant_points = [
                point for point in device_data 
                if point.timestamp >= cutoff_time
            ]
            
            return _calculate_average_metrics(relevant_points, device_type)
        else:
            return {}  # Return empty if can't acquire lock
    except Exception as e:
        return {}

def get_device_historical_matrix(device_id: str) -> dict:
    """Get complete historical matrix for a device (10s, 30s, 1m, 5m averages)"""
    timeframes = {
        '10s': 10,
        '30s': 30,
        '1m': 60,
        '5m': 300
    }
    
    matrix = {}
    for label, seconds in timeframes.items():
        averages = get_historical_averages(device_id, seconds)
        matrix[label] = averages if averages else None
    
    return matrix

def get_all_devices_historical_matrix() -> dict:
    """Get historical matrix for all devices"""
    global _nvidia_historical_data, _intel_historical_data
    
    result = {}
    
    try:
        # Use timeout to prevent deadlock
        if _data_lock.acquire(timeout=1.0):
            try:
                # Process NVIDIA devices
                nvidia_device_ids = list(_nvidia_historical_data.keys())
                intel_device_ids = list(_intel_historical_data.keys())
            finally:
                _data_lock.release()
            
            # Process devices outside of lock to avoid deadlock
            for device_id in nvidia_device_ids:
                result[device_id] = get_device_historical_matrix(device_id)
            
            for device_id in intel_device_ids:
                result[device_id] = get_device_historical_matrix(device_id)
        else:
            # If we can't acquire lock, return empty result
            result = {"error": "Unable to acquire data lock", "devices": {}}
    except Exception as e:
        result = {"error": str(e), "devices": {}}
    
    return result

def cleanup_old_data():
    """Clean up data older than 10 minutes (handled automatically by deque maxlen)"""
    # The deque with maxlen automatically handles this, but this function
    # is here for explicit cleanup if needed in the future
    pass

def get_data_availability(device_id: str) -> dict:
    """Get information about data availability for timeframes"""
    global _nvidia_historical_data, _intel_historical_data
    
    with _data_lock:
        device_data = None
        if device_id in _nvidia_historical_data:
            device_data = _nvidia_historical_data[device_id]
        elif device_id in _intel_historical_data:
            device_data = _intel_historical_data[device_id]
        
        if not device_data:
            return {'10s': False, '30s': False, '1m': False, '5m': False}
        
        # Check if we have enough data for each timeframe
        now = datetime.now()
        availability = {}
        
        for label, seconds in [('10s', 10), ('30s', 30), ('1m', 60), ('5m', 300)]:
            cutoff_time = now - timedelta(seconds=seconds)
            has_data = any(point.timestamp >= cutoff_time for point in device_data)
            availability[label] = has_data
        
        return availability
