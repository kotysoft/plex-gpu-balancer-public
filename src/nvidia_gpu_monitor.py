#!/usr/bin/env python3
"""
NVIDIA GPU Monitor - Individual Device Monitoring
Uses nvidia-smi for per-device metrics collection with background threads
"""

import sys
import os
import threading
import time
import subprocess
from datetime import datetime

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from import_helper import import_plex_api

# Import plex_api functions
get_parsed_gpu_devices, load_available_devices = import_plex_api()

# Global monitor instances
_nvidia_monitors = {}
_monitor_lock = threading.Lock()

class OptimizedNvidiaMonitor:
    def __init__(self, device_info, gpu_index=0, update_interval=1):
        self.device_info = device_info
        self.device_id = device_info['id']
        self.device_name = device_info['name']
        self.gpu_index = gpu_index  # nvidia-smi GPU index
        self.update_interval = update_interval
        self.running = False
        self.thread = None
        self.latest_metrics = {}
        
    def start_monitoring(self):
        """Start background monitoring thread"""
        if self.running:
            return True
            
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        return True
    
    def _monitor_loop(self):
        """Background monitoring loop using nvidia-smi"""
        while self.running:
            try:
                # Get basic GPU metrics
                metrics = {
                    'timestamp': datetime.now().isoformat(),
                    'device': self.device_name,
                    'device_id': self.device_id,
                    'gpu_index': self.gpu_index,
                    'status': 'success'
                }
                
                # Query specific GPU by index - now including encoder/decoder utilization
                result = subprocess.run([
                    'nvidia-smi', 
                    f'--id={self.gpu_index}',
                    '--query-gpu=utilization.gpu,utilization.memory,utilization.encoder,utilization.decoder,temperature.gpu,fan.speed,power.draw,memory.used,memory.total',
                    '--format=csv,noheader,nounits'
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0 and result.stdout.strip():
                    parts = result.stdout.strip().split(', ')
                    if len(parts) >= 9:
                        util_gpu, util_mem, util_enc, util_dec, temp, fan, power, mem_used, mem_total = parts[:9]
                        
                        # Clean and parse values safely
                        def safe_int(value):
                            try:
                                return int(float(value.strip())) if value.strip() != 'N/A' else 0
                            except (ValueError, AttributeError):
                                return 0
                        
                        def safe_float(value):
                            try:
                                return float(value.strip()) if value.strip() != 'N/A' else 0.0
                            except (ValueError, AttributeError):
                                return 0.0
                        
                        mem_used_val = safe_int(mem_used)
                        mem_total_val = safe_int(mem_total)
                        mem_free_val = mem_total_val - mem_used_val if mem_total_val > 0 else 0
                        
                        metrics.update({
                            'utilization_percent': safe_int(util_gpu),
                            'memory_utilization_percent': safe_int(util_mem),
                            'encoder_utilization_percent': safe_int(util_enc),
                            'decoder_utilization_percent': safe_int(util_dec),
                            'temperature_celsius': safe_int(temp),
                            'fan_speed_percent': safe_int(fan),
                            'power_watts': safe_float(power),
                            'memory_used_mb': mem_used_val,
                            'memory_total_mb': mem_total_val,
                            'memory_free_mb': mem_free_val,
                            'memory_used_percent': (mem_used_val / mem_total_val * 100) if mem_total_val > 0 else 0
                        })
                else:
                    # Set error values
                    metrics.update({
                        'utilization_percent': 0,
                        'memory_utilization_percent': 0,
                        'encoder_utilization_percent': 0,
                        'decoder_utilization_percent': 0,
                        'temperature_celsius': 0,
                        'fan_speed_percent': 0,
                        'power_watts': 0.0,
                        'memory_used_mb': 0,
                        'memory_total_mb': 0,
                        'memory_free_mb': 0,
                        'memory_used_percent': 0
                    })
                
                # Get processes for this specific GPU
                processes = []
                try:
                    proc_result = subprocess.run([
                        'nvidia-smi', 
                        f'--id={self.gpu_index}',
                        '--query-compute-apps=pid,name,used_memory', 
                        '--format=csv,noheader'
                    ], capture_output=True, text=True, timeout=5)
                    
                    if proc_result.returncode == 0 and proc_result.stdout.strip():
                        for line in proc_result.stdout.strip().split('\n'):
                            if line.strip():
                                parts = line.split(', ')
                                if len(parts) >= 3:
                                    pid, name, mem = parts[:3]
                                    if mem.strip() != '0 MiB' and mem.strip() != 'N/A':
                                        processes.append({
                                            'pid': pid,
                                            'name': name,
                                            'memory': mem
                                        })
                except:
                    pass
                
                metrics['processes'] = processes
                metrics['process_count'] = len(processes)
                
                self.latest_metrics = metrics
                
            except Exception as e:
                # Set error status
                self.latest_metrics = {
                    'timestamp': datetime.now().isoformat(),
                    'device': self.device_name,
                    'device_id': self.device_id,
                    'gpu_index': self.gpu_index,
                    'status': 'error',
                    'error': str(e),
                    'utilization_percent': 0,
                    'memory_utilization_percent': 0,
                    'encoder_utilization_percent': 0,
                    'decoder_utilization_percent': 0,
                    'temperature_celsius': 0,
                    'fan_speed_percent': 0,
                    'power_watts': 0.0,
                    'memory_used_mb': 0,
                    'memory_total_mb': 0,
                    'memory_free_mb': 0,
                    'memory_used_percent': 0,
                    'processes': [],
                    'process_count': 0
                }
            
            time.sleep(self.update_interval)
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        
    def get_latest_metrics(self):
        """Get cached metrics (lightweight)"""
        return self.latest_metrics.copy() if self.latest_metrics else {
            'timestamp': datetime.now().isoformat(),
            'device': self.device_name,
            'device_id': self.device_id,
            'gpu_index': self.gpu_index,
            'status': 'no_data',
            'utilization_percent': 0,
            'memory_utilization_percent': 0,
            'encoder_utilization_percent': 0,
            'decoder_utilization_percent': 0,
            'temperature_celsius': 0,
            'fan_speed_percent': 0,
            'power_watts': 0.0,
            'memory_used_mb': 0,
            'memory_total_mb': 0,
            'memory_free_mb': 0,
            'memory_used_percent': 0,
            'processes': [],
            'process_count': 0
        }

def _get_nvidia_gpu_count():
    """Get the number of NVIDIA GPUs available"""
    try:
        result = subprocess.run(['nvidia-smi', '-L'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return len([line for line in result.stdout.strip().split('\n') if line.startswith('GPU ')])
    except:
        pass
    return 0

def start_nvidia_monitor():
    """Start NVIDIA GPU monitors for all NVIDIA devices"""
    global _nvidia_monitors
    
    with _monitor_lock:
        try:
            # Load devices
            load_available_devices()
            devices = get_parsed_gpu_devices()
            nvidia_devices = [dev for dev in devices if dev['type'] == 'nvidia']
            
            if not nvidia_devices:
                return False
            
            # Get total NVIDIA GPU count
            gpu_count = _get_nvidia_gpu_count()
            if gpu_count == 0:
                return False
            
            # Start monitors for each NVIDIA device
            gpu_index = 0
            for device in nvidia_devices:
                device_id = device['id']
                if device_id not in _nvidia_monitors and gpu_index < gpu_count:
                    monitor = OptimizedNvidiaMonitor(device, gpu_index=gpu_index, update_interval=1)
                    if monitor.start_monitoring():
                        _nvidia_monitors[device_id] = monitor
                    gpu_index += 1
            
            return len(_nvidia_monitors) > 0
            
        except Exception as e:
            return False

def get_nvidia_gpu_data():
    """Get NVIDIA GPU data for ALL NVIDIA devices (lightweight)"""
    global _nvidia_monitors
    
    # Return data from all NVIDIA monitors
    with _monitor_lock:
        if not _nvidia_monitors:
            return None
            
        # If only one NVIDIA device, return its data directly
        if len(_nvidia_monitors) == 1:
            monitor = next(iter(_nvidia_monitors.values()))
            return monitor.get_latest_metrics()
        
        # Multiple NVIDIA devices - return first available data
        for monitor in _nvidia_monitors.values():
            data = monitor.get_latest_metrics()
            if data.get('status') == 'success':
                return data
    
    return None

def get_all_nvidia_gpu_data():
    """Get data for ALL NVIDIA GPU devices"""
    global _nvidia_monitors
    
    all_data = {}
    with _monitor_lock:
        for device_id, monitor in _nvidia_monitors.items():
            all_data[device_id] = monitor.get_latest_metrics()
    
    return all_data

def get_nvidia_process_count():
    """Get total NVIDIA GPU process count across all devices"""
    total_processes = 0
    with _monitor_lock:
        for monitor in _nvidia_monitors.values():
            data = monitor.get_latest_metrics()
            if data and data.get('process_count'):
                total_processes += data['process_count']
    return total_processes

def stop_all_monitors():
    """Stop all NVIDIA monitors"""
    global _nvidia_monitors
    
    with _monitor_lock:
        for monitor in _nvidia_monitors.values():
            monitor.stop_monitoring()
        _nvidia_monitors.clear()

# Legacy compatibility functions
class NvidiaGPUMonitor:
    """Legacy compatibility wrapper"""
    def __init__(self, device_id):
        self.device_id = device_id
        
    def get_metrics(self):
        """Legacy method - returns basic metrics"""
        data = get_nvidia_gpu_data()
        if not data:
            return {
                "utilization": 0,
                "temperature": 0,
                "fan_speed": 0,
                "power_draw": 0,
                "processes": 0
            }
        
        return {
            "utilization": data.get('utilization_percent', 0),
            "temperature": data.get('temperature_celsius', 0),
            "fan_speed": data.get('fan_speed_percent', 0),
            "power_draw": data.get('power_watts', 0),
            "processes": data.get('process_count', 0)
        }
