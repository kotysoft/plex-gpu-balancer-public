#!/usr/bin/env python3
"""
Intel GPU Monitor - Optimized Version
Uses background threads and the universal JSON parser for efficient monitoring
"""

import sys
import os
import threading
import time
from datetime import datetime

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the new parsers
from universal_json_parser import UniversalJSONParser
from import_helper import import_plex_api

# Import plex_api functions
get_parsed_gpu_devices, load_available_devices = import_plex_api()

# Global monitor instances
_intel_monitors = {}
_monitor_lock = threading.Lock()

class OptimizedIntelMonitor:
    def __init__(self, device_info, update_interval=1000):
        self.device_info = device_info
        self.device_id = device_info['id']
        self.device_name = device_info['name']
        self.update_interval = update_interval
        self.running = False
        self.thread = None
        self.latest_metrics = {}
        self.parser = UniversalJSONParser()
        
        # Target metrics to extract
        self.target_metrics = [
            'frequency.actual',
            'power.GPU', 
            'power.Package',
            'engines.Render/3D/0.busy',
            'engines.Blitter/0.busy',
            'engines.Video/0.busy', 
            'engines.VideoEnhance/0.busy'
        ]
        
        self.device_filter = self._get_device_filter()
        
    def _get_device_filter(self):
        """Convert Plex device ID to intel_gpu_top device filter"""
        device_id = self.device_id
        
        if '@' in device_id:
            pci_addr = device_id.split('@')[1]
            return f"sys:/sys/devices/pci0000:00/{pci_addr}"
        elif device_id.startswith('pci-'):
            pci_addr = device_id.replace('pci-', '')
            return f"pci:device=8086,card={pci_addr}"
        else:
            return "pci:vendor=8086"
    
    def start_monitoring(self):
        """Start background monitoring thread"""
        if self.running:
            return True
            
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        return True
    
    def _monitor_loop(self):
        """Background monitoring loop using universal parser"""
        import subprocess
        
        cmd = ['intel_gpu_top', '-J', '-s', str(self.update_interval)]
        
        if self.device_filter and self.device_filter != "pci:vendor=8086":
            cmd.extend(['-d', self.device_filter])
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            for json_obj in self.parser.process_stream(process.stdout):
                if not self.running:
                    break
                
                # Extract metrics efficiently
                metrics = {
                    'timestamp': datetime.now().isoformat(),
                    'device': self.device_name,
                    'device_id': self.device_id,
                    'status': 'success'
                }
                
                # Extract target metrics
                for metric_path in self.target_metrics:
                    value = json_obj
                    for key in metric_path.split('.'):
                        if isinstance(value, dict) and key in value:
                            value = value[key]
                        else:
                            value = 0  # Default to 0 instead of None
                            break
                    metrics[metric_path] = value
                    
                # Convert to dashboard-friendly format
                metrics.update({
                    'frequency_mhz': metrics.get('frequency.actual', 0),
                    'power_gpu': metrics.get('power.GPU', 0),
                    'power_package': metrics.get('power.Package', 0),
                    'engines': {
                        'render_3d_percent': metrics.get('engines.Render/3D/0.busy', 0),
                        'blitter_percent': metrics.get('engines.Blitter/0.busy', 0),
                        'video_percent': metrics.get('engines.Video/0.busy', 0),
                        'video_enhance_percent': metrics.get('engines.VideoEnhance/0.busy', 0)
                    },
                    'processes': {'total_count': 0}  # Will be calculated separately in gpu_metrics.py
                })
                
                self.latest_metrics = metrics
                
        except Exception as e:
            # Set error status
            self.latest_metrics = {
                'timestamp': datetime.now().isoformat(),
                'device': self.device_name,
                'device_id': self.device_id,
                'status': 'error',
                'error': str(e),
                'frequency_mhz': 0,
                'power_gpu': 0,
                'power_package': 0,
                'engines': {
                    'render_3d_percent': 0,
                    'blitter_percent': 0,
                    'video_percent': 0,
                    'video_enhance_percent': 0
                },
                'processes': {'total_count': 0}
            }
        finally:
            try:
                if process:
                    process.terminate()
            except:
                pass
    
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        
    def get_latest_metrics(self):
        """Get cached metrics (lightweight)"""
        return self.latest_metrics.copy() if self.latest_metrics else {
            'timestamp': datetime.now().isoformat(),
            'device': self.device_name,
            'device_id': self.device_id,
            'status': 'no_data',
            'frequency_mhz': 0,
            'power_gpu': 0,
            'power_package': 0,
            'engines': {
                'render_3d_percent': 0,
                'blitter_percent': 0,
                'video_percent': 0,
                'video_enhance_percent': 0
            },
            'processes': {'total_count': 0}
        }

def start_intel_monitor():
    """Start Intel GPU monitors for all Intel devices"""
    global _intel_monitors
    
    with _monitor_lock:
        try:
            # Load devices
            load_available_devices()
            devices = get_parsed_gpu_devices()
            intel_devices = [dev for dev in devices if dev['type'] == 'intel']
            
            if not intel_devices:
                return False
            
            # Start monitors for each Intel device
            for device in intel_devices:
                device_id = device['id']
                if device_id not in _intel_monitors:
                    monitor = OptimizedIntelMonitor(device, update_interval=1000)
                    if monitor.start_monitoring():
                        _intel_monitors[device_id] = monitor
            
            return len(_intel_monitors) > 0
            
        except Exception as e:
            return False

def get_intel_gpu_data():
    """Get Intel GPU data for ALL Intel devices (lightweight)"""
    global _intel_monitors
    
    # Return data from all Intel monitors, not just active one
    with _monitor_lock:
        if not _intel_monitors:
            return None
            
        # If only one Intel device, return its data directly
        if len(_intel_monitors) == 1:
            monitor = next(iter(_intel_monitors.values()))
            return monitor.get_latest_metrics()
        
        # Multiple Intel devices - return combined data or first available
        for monitor in _intel_monitors.values():
            data = monitor.get_latest_metrics()
            if data.get('status') == 'success':
                return data
    
    return None

def get_all_intel_gpu_data():
    """Get data for ALL Intel GPU devices"""
    global _intel_monitors
    
    all_data = {}
    with _monitor_lock:
        for device_id, monitor in _intel_monitors.items():
            all_data[device_id] = monitor.get_latest_metrics()
    
    return all_data

def get_intel_process_count():
    """Get Intel GPU process count (lightweight)"""
    data = get_intel_gpu_data()
    if data and data.get('processes'):
        return data['processes'].get('total_count', 0)
    return 0

def stop_all_monitors():
    """Stop all Intel monitors"""
    global _intel_monitors
    
    with _monitor_lock:
        for monitor in _intel_monitors.values():
            monitor.stop_monitoring()
        _intel_monitors.clear()

# Legacy compatibility functions
class IntelGPUMonitor:
    """Legacy compatibility wrapper"""
    def __init__(self, plex_device_id):
        self.plex_device_id = plex_device_id
        
    def get_metrics(self):
        """Legacy method - returns basic metrics"""
        data = get_intel_gpu_data()
        if not data:
            return {
                "engines": {"render": 0, "video": 0, "enhance": 0, "blitter": 0},
                "frequency": 0,
                "power": 0,
                "temperature": 0,
                "clients": 0
            }
        
        return {
            "engines": {
                "render": data.get('engines', {}).get('render_3d_percent', 0),
                "video": data.get('engines', {}).get('video_percent', 0), 
                "enhance": data.get('engines', {}).get('video_enhance_percent', 0),
                "blitter": data.get('engines', {}).get('blitter_percent', 0)
            },
            "frequency": data.get('frequency_mhz', 0),
            "power": data.get('power_gpu', 0),
            "temperature": 0,  # Not available from intel_gpu_top
            "clients": data.get('processes', {}).get('total_count', 0)
        }
