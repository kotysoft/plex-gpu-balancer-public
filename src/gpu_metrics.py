#!/usr/bin/env python3
"""
GPU Metrics Central Collector - Unified API Response
Collects data from all individual GPU workers and provides unified dashboard API
"""

import threading
import time
from datetime import datetime

# Global unified cache
_unified_device_cache = {}
_cache_lock = threading.Lock()
_collector_running = False
_collector_thread = None

def start_gpu_metrics_collector():
    """Start the central GPU metrics collector"""
    global _collector_running, _collector_thread
    
    if _collector_running:
        return True
        
    _collector_running = True
    _collector_thread = threading.Thread(target=_collector_worker, daemon=True)
    _collector_thread.start()
    return True

def stop_gpu_metrics_collector():
    """Stop the central GPU metrics collector"""
    global _collector_running
    _collector_running = False

def _collector_worker():
    """Central collector worker that gathers data from all device monitors"""
    global _unified_device_cache, _collector_running
    
    while _collector_running:
        try:
            unified_data = {}
            
            # Import GPU monitor functions first
            intel_funcs = None
            nvidia_funcs = None
            try:
                from import_helper import import_gpu_monitors
                intel_funcs, nvidia_funcs = import_gpu_monitors()
            except ImportError:
                pass  # GPU monitors not available
            
            # Collect data from NVIDIA monitors
            try:
                if nvidia_funcs:
                    _, get_all_nvidia_gpu_data = nvidia_funcs
                    nvidia_data = get_all_nvidia_gpu_data()
                    if nvidia_data:
                        for device_id, metrics in nvidia_data.items():
                            unified_data[device_id] = {
                                'device_id': device_id,
                                'device_name': metrics.get('device', 'Unknown NVIDIA GPU'),
                                'device_type': 'nvidia',
                                'status': metrics.get('status', 'unknown'),
                                'timestamp': metrics.get('timestamp', datetime.now().isoformat()),
                                'utilization_percent': metrics.get('utilization_percent', 0),
                                'temperature_celsius': metrics.get('temperature_celsius', 0),
                                'power_watts': metrics.get('power_watts', 0),
                                'memory_used_mb': metrics.get('memory_used_mb', 0),
                                'memory_total_mb': metrics.get('memory_total_mb', 0),
                                'memory_free_mb': metrics.get('memory_free_mb', 0),
                                'memory_utilization_percent': metrics.get('memory_utilization_percent', 0),
                                'memory_used_percent': metrics.get('memory_used_percent', 0),
                                'fan_speed_percent': metrics.get('fan_speed_percent', 0),
                                'processes': metrics.get('processes', []),
                                'process_count': metrics.get('process_count', 0),
                                'vendor_specific': {
                                    'gpu_index': metrics.get('gpu_index', 0),
                                    'encoder_utilization_percent': metrics.get('encoder_utilization_percent', 0),
                                    'decoder_utilization_percent': metrics.get('decoder_utilization_percent', 0),
                                    'nvidia_smi_available': True
                                }
                            }
            except Exception as e:
                pass  # Continue even if NVIDIA collection fails
            
            # Collect data from Intel monitors
            try:
                if intel_funcs:
                    _, get_all_intel_gpu_data = intel_funcs
                    intel_data = get_all_intel_gpu_data()
                    if intel_data:
                        for device_id, metrics in intel_data.items():
                            unified_data[device_id] = {
                                'device_id': device_id,
                                'device_name': metrics.get('device', 'Unknown Intel GPU'),
                                'device_type': 'intel',
                                'status': metrics.get('status', 'unknown'),
                                'timestamp': metrics.get('timestamp', datetime.now().isoformat()),
                                'utilization_percent': max(
                                    metrics.get('engines', {}).get('render_3d_percent', 0),
                                    metrics.get('engines', {}).get('video_percent', 0),
                                    metrics.get('engines', {}).get('video_enhance_percent', 0)
                                ),
                                'temperature_celsius': 0,  # Not available from intel_gpu_top
                                'power_watts': metrics.get('power_package', 0),
                                'memory_used_mb': 0,  # Not available from intel_gpu_top
                                'memory_total_mb': 0,  # Not available from intel_gpu_top
                                'memory_utilization_percent': 0,  # Not available from intel_gpu_top
                                'fan_speed_percent': 0,  # Not applicable for Intel
                                'processes': metrics.get('processes', []),
                                'process_count': metrics.get('processes', {}).get('total_count', 0),
                                'vendor_specific': {
                                    'frequency_mhz': metrics.get('frequency_mhz', 0),
                                    'power_gpu_watts': metrics.get('power_gpu', 0),
                                    'engines': metrics.get('engines', {}),
                                    'intel_gpu_top_available': True
                                }
                            }
            except ImportError:
                pass  # Intel monitor not available
            except Exception as e:
                pass  # Continue even if Intel collection fails
            
            # Apply Intel GPU process count fallback logic
            intel_devices = [device_id for device_id, data in unified_data.items() if data.get('device_type') == 'intel']
            
            # Only apply fallback if there's exactly one Intel GPU
            if len(intel_devices) == 1:
                intel_device_id = intel_devices[0]
                try:
                    # Get Plex transcoding sessions
                    from plex_api import get_plex_status
                    plex_status = get_plex_status()
                    total_plex_sessions = plex_status.get('sessions', 0)
                    
                    if total_plex_sessions > 0:
                        # Calculate total NVIDIA processes
                        total_nvidia_processes = sum(
                            data.get('process_count', 0) 
                            for data in unified_data.values() 
                            if data.get('device_type') == 'nvidia'
                        )
                        
                        # Calculate Intel processes: Plex sessions - NVIDIA processes
                        intel_processes = max(0, total_plex_sessions - total_nvidia_processes)
                        
                        # Update the Intel device with calculated process count
                        unified_data[intel_device_id]['process_count'] = intel_processes
                        
                except Exception:
                    pass  # If fallback fails, keep original process count
            
            # Update unified cache
            with _cache_lock:
                _unified_device_cache = unified_data
                
        except Exception as e:
            pass  # Continue running even if there's an error
        
        time.sleep(1)  # Update every second

def get_all_gpu_metrics():
    """Get unified metrics for ALL GPU devices"""
    global _unified_device_cache
    
    # Start collector if not running
    if not _collector_running:
        start_gpu_metrics_collector()
    
    with _cache_lock:
        return {
            'timestamp': datetime.now().isoformat(),
            'devices': _unified_device_cache.copy(),
            'device_count': len(_unified_device_cache),
            'nvidia_count': len([d for d in _unified_device_cache.values() if d.get('device_type') == 'nvidia']),
            'intel_count': len([d for d in _unified_device_cache.values() if d.get('device_type') == 'intel'])
        }

def get_device_metrics(device_id):
    """Get metrics for a specific device"""
    global _unified_device_cache
    
    with _cache_lock:
        return _unified_device_cache.get(device_id)

def get_active_device_metrics():
    """Get metrics for the currently active Plex device"""
    try:
        from import_helper import import_plex_api
        get_parsed_gpu_devices, load_available_devices = import_plex_api()
        # Note: get_current_active_device is not available in import_plex_api, need to import directly
        from plex_api import get_current_active_device
        active_device_id = get_current_active_device()
        
        if active_device_id:
            return get_device_metrics(active_device_id)
    except:
        pass
    
    return None

def get_metrics_by_type(device_type):
    """Get metrics for all devices of a specific type (nvidia/intel)"""
    global _unified_device_cache
    
    with _cache_lock:
        return {
            device_id: metrics for device_id, metrics in _unified_device_cache.items()
            if metrics.get('device_type') == device_type.lower()
        }

def get_total_utilization_by_type(device_type):
    """Get average utilization for all devices of a specific type"""
    devices = get_metrics_by_type(device_type)
    if not devices:
        return 0
    
    total_util = sum(device.get('utilization_percent', 0) for device in devices.values())
    return total_util / len(devices)

def get_total_process_count():
    """Get total process count across all GPU devices"""
    global _unified_device_cache
    
    with _cache_lock:
        return sum(device.get('process_count', 0) for device in _unified_device_cache.values())

def get_summary_stats():
    """Get summary statistics across all GPU devices"""
    global _unified_device_cache
    
    with _cache_lock:
        if not _unified_device_cache:
            return {
                'total_devices': 0,
                'nvidia_devices': 0,
                'intel_devices': 0,
                'active_devices': 0,
                'avg_utilization': 0,
                'total_processes': 0,
                'total_power_watts': 0
            }
        
        devices = list(_unified_device_cache.values())
        nvidia_count = len([d for d in devices if d.get('device_type') == 'nvidia'])
        intel_count = len([d for d in devices if d.get('device_type') == 'intel'])
        active_count = len([d for d in devices if d.get('status') == 'success'])
        
        total_util = sum(d.get('utilization_percent', 0) for d in devices)
        avg_util = total_util / len(devices) if devices else 0
        
        total_processes = sum(d.get('process_count', 0) for d in devices)
        total_power = sum(d.get('power_watts', 0) for d in devices)
        
        return {
            'total_devices': len(devices),
            'nvidia_devices': nvidia_count,
            'intel_devices': intel_count,
            'active_devices': active_count,
            'avg_utilization': round(avg_util, 1),
            'total_processes': total_processes,
            'total_power_watts': round(total_power, 1)
        }

# Legacy compatibility functions for backward compatibility
def get_gpu_metrics():
    """Legacy function - returns old format for backward compatibility"""
    all_metrics = get_all_gpu_metrics()
    devices = all_metrics.get('devices', {})
    
    # Create legacy format
    nvidia_devices = [d for d in devices.values() if d.get('device_type') == 'nvidia']
    intel_devices = [d for d in devices.values() if d.get('device_type') == 'intel']
    
    # Get first available device of each type for legacy compatibility
    nvidia_data = nvidia_devices[0] if nvidia_devices else {
        'available': False, 'utilization': 0, 'temperature': 0, 
        'fan_speed': 0, 'power_draw': 0, 'processes': []
    }
    
    intel_data = intel_devices[0] if intel_devices else {
        'available': False, 'power_state': 'Unknown', 'temperature': 0, 
        'cpu_temp': 0, 'system_temp': 0, 'processes': []
    }
    
    return {
        'nvidia': {
            'available': nvidia_data.get('status') == 'success' if nvidia_devices else False,
            'utilization': nvidia_data.get('utilization_percent', 0),
            'temperature': nvidia_data.get('temperature_celsius', 0),
            'fan_speed': nvidia_data.get('fan_speed_percent', 0),
            'power_draw': nvidia_data.get('power_watts', 0),
            'processes': nvidia_data.get('processes', [])
        },
        'intel': {
            'available': intel_data.get('status') == 'success' if intel_devices else False,
            'power_state': 'D0' if intel_devices and intel_data.get('status') == 'success' else 'Unknown',
            'temperature': intel_data.get('temperature_celsius', 0),
            'cpu_temp': intel_data.get('temperature_celsius', 0),
            'system_temp': intel_data.get('temperature_celsius', 0),
            'processes': intel_data.get('processes', []),
            'utilization': intel_data.get('utilization_percent', 0)
        }
    }

# Background worker management (legacy compatibility)
def start_background_workers():
    """Legacy function - starts the unified collector"""
    return start_gpu_metrics_collector()

def stop_background_workers():
    """Legacy function - stops the unified collector"""
    stop_gpu_metrics_collector()
