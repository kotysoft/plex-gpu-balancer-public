#!/usr/bin/env python3
"""Intelligent Plex GPU Load Balancer with Configuration-Driven Logic"""

import time
import logging
import sys
import os
from datetime import datetime

# Add src directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import balance configuration system
from balance_config import get_current_settings, get_gpu_devices_mapping

# Import GPU collector service
try:
    from gpu_collector_service import get_device_load_data, is_gpu_collector_running
    GPU_MONITORING_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  GPU collector service not available: {e}")
    GPU_MONITORING_AVAILABLE = False
    def get_device_load_data(device_id, timeframe_seconds):
        return None
    def is_gpu_collector_running():
        return False

# Import NVIDIA monitoring for session counting
try:
    from nvidia_gpu_monitor import get_all_nvidia_gpu_data
    NVIDIA_MONITORING_AVAILABLE = True
except ImportError:
    NVIDIA_MONITORING_AVAILABLE = False
    def get_all_nvidia_gpu_data():
        return {}

# Import Plex API functions
from plex_api import get_plex_status, get_current_active_device, switch_to_device, load_available_devices

# Configuration
CHECK_INTERVAL = 5  # seconds between evaluations

# Global state
total_switches = 0
service_start_time = datetime.now()
last_optimal_gpu = None
split_sessions_rotation_index = 0
last_switch_time = None

# Session tracking for improved balancing
last_total_sessions = 0
last_session_check_time = None
session_change_detected = False
last_gpu_session_counts = {}

# Smart config reloading state
last_config_check_time = 0
last_config_mtime = 0

# Setup logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Console output only
    ]
)
logger = logging.getLogger(__name__)

class IntelligentPlexGPUBalancer:
    """Intelligent GPU balancer using configuration-driven algorithms"""
    
    def __init__(self):
        self.available_devices = {}
        self.gpu_devices_mapping = {}
        self.balance_settings = {}
        self.load_settings()
        
    def should_reload_config(self):
        """Check if config file has been modified and needs reloading"""
        global last_config_check_time, last_config_mtime
        
        current_time = time.time()
        
        # Only check file modification time every 5 seconds to reduce filesystem calls
        if current_time - last_config_check_time < 5:
            return False
            
        last_config_check_time = current_time
        
        try:
            # Get balance.conf file path
            from balance_config import get_config_file_path
            config_path = get_config_file_path()
            
            if os.path.exists(config_path):
                current_mtime = os.path.getmtime(config_path)
                
                # First time or file has been modified
                if last_config_mtime == 0 or current_mtime > last_config_mtime:
                    last_config_mtime = current_mtime
                    return True
                    
        except Exception as e:
            logger.warning(f"⚠️  Unable to check config file modification time: {e}")
            # Fallback to time-based reloading every 30 seconds
            return current_time % 30 == 0
            
        return False
    
    def load_settings(self):
        """Load balance configuration and available GPU devices"""
        try:
            # Load balance configuration
            self.balance_settings = get_current_settings()
            self.gpu_devices_mapping = get_gpu_devices_mapping()
            
            # Load available devices from Plex
            self.available_devices = load_available_devices()
            
            logger.info(f"✅ Loaded balance settings: method={self.balance_settings.get('method', 'unknown')}")
            logger.info(f"✅ Loaded {len(self.available_devices)} GPU devices from Plex")
            
        except Exception as e:
            logger.error(f"❌ Failed to load settings: {e}")
            self.balance_settings = {'method': 'preferred-order', 'system': {'auto_balancing_enabled': True}}
            self.gpu_devices_mapping = {}
            self.available_devices = {}
    
    def get_plex_sessions(self):
        """Get current total Plex sessions"""
        try:
            plex_status = get_plex_status()
            return plex_status.get('sessions', 0)
        except Exception as e:
            logger.error(f"❌ Failed to get Plex sessions: {e}")
            return 0
    
    def get_nvidia_sessions_per_gpu(self):
        """Get session count per NVIDIA GPU"""
        sessions_per_gpu = {}
        
        if not NVIDIA_MONITORING_AVAILABLE:
            return sessions_per_gpu
            
        try:
            nvidia_data = get_all_nvidia_gpu_data()
            if isinstance(nvidia_data, dict):
                for device_id, device_data in nvidia_data.items():
                    process_count = device_data.get('process_count', 0)
                    sessions_per_gpu[device_id] = process_count
                    
        except Exception as e:
            logger.error(f"❌ Failed to get NVIDIA sessions: {e}")
            
        return sessions_per_gpu
    
    def calculate_intel_sessions(self, total_plex_sessions, nvidia_sessions):
        """Calculate Intel GPU sessions (total - nvidia sessions)"""
        total_nvidia_sessions = sum(nvidia_sessions.values())
        intel_sessions = max(0, total_plex_sessions - total_nvidia_sessions)
        return intel_sessions
    
    def get_device_load_analysis(self, device_id, timeframe_seconds):
        """Analyze device load over specified timeframe using GPU collector service"""
        if not GPU_MONITORING_AVAILABLE:
            return None
            
        # Check if GPU collector service is running
        if not is_gpu_collector_running():
            logger.warning("⚠️  GPU collector service not running - load analysis unavailable")
            return None
            
        try:
            # Use GPU collector service API
            avg_utilization = get_device_load_data(device_id, timeframe_seconds)
            return avg_utilization
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze load for {device_id}: {e}")
            return None
    
    def get_gpu_session_count(self, device_id):
        """Get current session count for a specific GPU device"""
        nvidia_sessions = self.get_nvidia_sessions_per_gpu()
        total_plex_sessions = self.get_plex_sessions()
        
        # Check if this is an NVIDIA device
        if device_id in nvidia_sessions:
            return nvidia_sessions[device_id]
            
        # For Intel (or other non-NVIDIA), calculate estimated sessions
        intel_sessions = self.calculate_intel_sessions(total_plex_sessions, nvidia_sessions)
        
        # If this device appears to be Intel/integrated, return calculated sessions
        device_name = self.available_devices.get(device_id, '').lower()
        if 'intel' in device_name or '8086' in device_id:
            return intel_sessions
            
        # For unknown devices, assume 0 sessions
        return 0
    
    def get_all_gpu_session_counts(self):
        """Get session counts for all GPU devices"""
        session_counts = {}
        gpu_priority_order = self.get_gpu_priority_order()
        
        for device_id in gpu_priority_order:
            session_counts[device_id] = self.get_gpu_session_count(device_id)
            
        return session_counts
    
    def detect_session_changes(self):
        """Detect if there have been session changes since last check"""
        global last_total_sessions, last_session_check_time, session_change_detected, last_gpu_session_counts
        
        current_total_sessions = self.get_plex_sessions()
        current_time = time.time()
        current_gpu_sessions = self.get_all_gpu_session_counts()
        
        # Initialize on first run
        if last_session_check_time is None:
            last_total_sessions = current_total_sessions
            last_session_check_time = current_time
            last_gpu_session_counts = current_gpu_sessions.copy()
            session_change_detected = False
            return False
        
        # Check for total session count changes
        total_sessions_changed = current_total_sessions != last_total_sessions
        
        # Check for individual GPU session count changes
        gpu_sessions_changed = current_gpu_sessions != last_gpu_session_counts
        
        # Detect session changes
        if total_sessions_changed or gpu_sessions_changed:
            session_change_detected = True
            logger.info(f"🔍 Session change detected: Total {last_total_sessions}→{current_total_sessions}, GPU sessions changed: {gpu_sessions_changed}")
            
            # Log detailed session changes
            if gpu_sessions_changed:
                for device_id in current_gpu_sessions:
                    old_count = last_gpu_session_counts.get(device_id, 0)
                    new_count = current_gpu_sessions[device_id]
                    if old_count != new_count:
                        device_name = self.available_devices.get(device_id, device_id)
                        logger.info(f"📊 {device_name}: {old_count}→{new_count} sessions")
        else:
            session_change_detected = False
        
        # Update tracking variables
        last_total_sessions = current_total_sessions
        last_session_check_time = current_time
        last_gpu_session_counts = current_gpu_sessions.copy()
        
        return session_change_detected
    
    def find_least_loaded_gpu(self):
        """Find the GPU with the least number of sessions for rebalancing"""
        gpu_priority_order = self.get_gpu_priority_order()
        method_settings = self.balance_settings.get('split_sessions', {})
        
        if not gpu_priority_order:
            return None, "No GPU priority order configured"
        
        # Get session counts and filter out overloaded GPUs
        available_gpus = []
        for device_id in gpu_priority_order:
            is_overloaded, reason = self.is_gpu_overloaded(device_id, method_settings)
            if not is_overloaded:
                session_count = self.get_gpu_session_count(device_id)
                available_gpus.append((device_id, session_count))
        
        if not available_gpus:
            return None, "All GPUs are overloaded"
        
        # Sort by session count (ascending) and return the least loaded
        available_gpus.sort(key=lambda x: x[1])
        least_loaded_device = available_gpus[0][0]
        least_loaded_sessions = available_gpus[0][1]
        
        device_name = self.available_devices.get(least_loaded_device, least_loaded_device)
        return least_loaded_device, f"Least loaded GPU: {device_name} ({least_loaded_sessions} sessions)"
    
    def should_rebalance_sessions(self):
        """Check if session rebalancing is needed based on uneven distribution"""
        gpu_priority_order = self.get_gpu_priority_order()
        method_settings = self.balance_settings.get('split_sessions', {})
        
        if len(gpu_priority_order) < 2:
            return False, None, "Only one GPU available"
        
        # Get session counts for available GPUs
        available_sessions = []
        for device_id in gpu_priority_order:
            is_overloaded, reason = self.is_gpu_overloaded(device_id, method_settings)
            if not is_overloaded:
                session_count = self.get_gpu_session_count(device_id)
                available_sessions.append((device_id, session_count))
        
        if len(available_sessions) < 2:
            return False, None, "Less than 2 available GPUs"
        
        # Check if there's significant imbalance (difference > 1 session)
        min_sessions = min(sessions for _, sessions in available_sessions)
        max_sessions = max(sessions for _, sessions in available_sessions)
        
        if max_sessions - min_sessions > 1:
            # Find least loaded GPU
            least_loaded = min(available_sessions, key=lambda x: x[1])
            device_name = self.available_devices.get(least_loaded[0], least_loaded[0])
            return True, least_loaded[0], f"Rebalancing to {device_name} (imbalance: {max_sessions} vs {min_sessions} sessions)"
        
        return False, None, f"Sessions balanced (max difference: {max_sessions - min_sessions})"
    
    def is_gpu_overloaded(self, device_id, method_settings):
        """Check if GPU is overloaded based on session limits and load thresholds"""
        try:
            # Get GPU key for this device
            gpu_key = None
            for key, mapped_device_id in self.gpu_devices_mapping.items():
                if mapped_device_id == device_id:
                    gpu_key = key
                    break
                    
            if not gpu_key:
                return False, "GPU key not found"
            
            # Check session limit
            max_sessions_key = f"{gpu_key}_max_sessions"
            max_sessions = self.balance_settings.get('max_sessions', {}).get(max_sessions_key, 5)
            current_sessions = self.get_gpu_session_count(device_id)
            
            # Handle graceful fallback for Intel session counting
            if current_sessions is None or current_sessions < 0:
                logger.warning(f"⚠️  Session count unavailable for {device_id}, ignoring session limit")
            else:
                if current_sessions >= max_sessions:
                    return True, f"session limit reached ({current_sessions}/{max_sessions})"
            
            # Check load threshold
            method = self.balance_settings.get('method', 'preferred-order')
            if method == 'preferred-order':
                threshold_percentage = method_settings.get('load_threshold_percentage', 80)
                threshold_seconds = method_settings.get('load_threshold_seconds', 30)
            else:  # split-sessions
                threshold_percentage = method_settings.get('load_limit_percentage', 75)
                threshold_seconds = method_settings.get('load_limit_seconds', 60)
            
            avg_load = self.get_device_load_analysis(device_id, threshold_seconds)
            if avg_load is not None and avg_load > threshold_percentage:
                return True, f"load threshold exceeded ({avg_load:.1f}% > {threshold_percentage}% over {threshold_seconds}s)"
            
            return False, "within limits"
            
        except Exception as e:
            logger.error(f"❌ Error checking GPU overload for {device_id}: {e}")
            return False, f"error: {e}"
    
    def get_gpu_priority_order(self):
        """Get ordered list of GPU device IDs by priority"""
        gpu_priorities = self.balance_settings.get('gpu_priorities', {})
        ordered_devices = []
        
        # Sort by priority number
        for i in range(1, len(self.available_devices) + 1):
            priority_key = f"priority_{i}"
            if priority_key in gpu_priorities:
                gpu_key = gpu_priorities[priority_key]
                if gpu_key in self.gpu_devices_mapping:
                    device_id = self.gpu_devices_mapping[gpu_key]
                    if device_id in self.available_devices:
                        ordered_devices.append(device_id)
        
        return ordered_devices
    
    def evaluate_preferred_order_method(self):
        """Evaluate optimal GPU using preferred-order method"""
        method_settings = self.balance_settings.get('preferred_order', {})
        gpu_priority_order = self.get_gpu_priority_order()
        
        if not gpu_priority_order:
            logger.warning("⚠️  No GPU priority order configured")
            return None, "No priority order configured"
        
        # Check GPUs in priority order
        for device_id in gpu_priority_order:
            is_overloaded, reason = self.is_gpu_overloaded(device_id, method_settings)
            device_name = self.available_devices.get(device_id, device_id)
            
            if not is_overloaded:
                return device_id, f"Selected {device_name} (priority GPU, {reason})"
        
        # All GPUs are overloaded, select the least loaded one by priority
        logger.warning("⚠️  All GPUs are overloaded, selecting highest priority GPU")
        return gpu_priority_order[0], f"All GPUs overloaded, using highest priority: {self.available_devices.get(gpu_priority_order[0], gpu_priority_order[0])}"
    
    def evaluate_split_sessions_method(self):
        """Evaluate optimal GPU using split-sessions method with session change detection"""
        global split_sessions_rotation_index
        
        method_settings = self.balance_settings.get('split_sessions', {})
        gpu_priority_order = self.get_gpu_priority_order()
        
        if not gpu_priority_order:
            logger.warning("⚠️  No GPU priority order configured")
            return None, "No priority order configured"
        
        # Detect session changes
        session_changed = self.detect_session_changes()
        
        # Check if we need to rebalance based on uneven session distribution
        should_rebalance, rebalance_device, rebalance_reason = self.should_rebalance_sessions()
        
        current_device_id = None
        try:
            current_device_id = get_current_active_device()
        except:
            pass
        
        # If sessions are unbalanced and current GPU is not the least loaded, rebalance
        if should_rebalance and current_device_id != rebalance_device:
            logger.info(f"🔄 Session rebalancing triggered: {rebalance_reason}")
            return rebalance_device, rebalance_reason
        
        # Find available (non-overloaded) GPUs
        available_gpus = []
        for device_id in gpu_priority_order:
            is_overloaded, reason = self.is_gpu_overloaded(device_id, method_settings)
            if not is_overloaded:
                available_gpus.append(device_id)
        
        if not available_gpus:
            # All GPUs overloaded, use highest priority
            logger.warning("⚠️  All GPUs overloaded in split-sessions, using highest priority")
            return gpu_priority_order[0], f"All GPUs overloaded, using highest priority: {self.available_devices.get(gpu_priority_order[0], gpu_priority_order[0])}"
        
        # Only rotate to next GPU if:
        # 1. Session change was detected (new session started)
        # 2. OR current GPU is overloaded/not available
        current_gpu_available = current_device_id in available_gpus if current_device_id else False
        
        if session_changed and self.get_plex_sessions() > last_total_sessions:
            # New session detected - rotate to next GPU
            if split_sessions_rotation_index >= len(available_gpus):
                split_sessions_rotation_index = 0
                
            selected_device = available_gpus[split_sessions_rotation_index]
            device_name = self.available_devices.get(selected_device, selected_device)
            
            split_sessions_rotation_index = (split_sessions_rotation_index + 1) % len(available_gpus)
            
            logger.info(f"🔄 New session detected - rotating to next GPU")
            return selected_device, f"New session rotation: {device_name} (session change detected)"
        
        elif not current_gpu_available:
            # Current GPU is overloaded or not available - switch to next available
            if split_sessions_rotation_index >= len(available_gpus):
                split_sessions_rotation_index = 0
                
            selected_device = available_gpus[split_sessions_rotation_index]
            device_name = self.available_devices.get(selected_device, selected_device)
            
            split_sessions_rotation_index = (split_sessions_rotation_index + 1) % len(available_gpus)
            
            return selected_device, f"Current GPU unavailable - switching to: {device_name}"
        
        else:
            # No session change and current GPU is available - stay on current GPU
            if current_device_id and current_device_id in available_gpus:
                device_name = self.available_devices.get(current_device_id, current_device_id)
                return current_device_id, f"No session change - staying on: {device_name}"
            else:
                # Fallback to first available GPU
                selected_device = available_gpus[0]
                device_name = self.available_devices.get(selected_device, selected_device)
                return selected_device, f"Fallback selection: {device_name}"
    
    def evaluate_optimal_gpu(self):
        """Determine the optimal GPU based on current method and conditions"""
        method = self.balance_settings.get('method', 'preferred-order')
        
        if method == 'preferred-order':
            return self.evaluate_preferred_order_method()
        elif method == 'split-sessions':
            return self.evaluate_split_sessions_method()
        else:
            logger.error(f"❌ Unknown balancing method: {method}")
            return None, f"Unknown method: {method}"
    
    def switch_gpu_if_needed(self, optimal_device_id, reason):
        """Switch GPU if the optimal choice differs from current active GPU"""
        global total_switches, last_optimal_gpu, last_switch_time
        
        try:
            current_device_id = get_current_active_device()
            
            if optimal_device_id == current_device_id:
                # No switch needed
                if optimal_device_id != last_optimal_gpu:
                    device_name = self.available_devices.get(optimal_device_id, optimal_device_id)
                    logger.info(f"✅ GPU already optimal: {device_name}")
                    last_optimal_gpu = optimal_device_id
                return True
            
            # Check rate limiting before switching
            rate_limiting = self.balance_settings.get('rate_limiting', {})
            rate_limiting_enabled = rate_limiting.get('enabled', True)
            min_switch_interval = rate_limiting.get('min_switch_interval_seconds', 10)
            
            if rate_limiting_enabled and last_switch_time is not None:
                time_since_last_switch = time.time() - last_switch_time
                if time_since_last_switch < min_switch_interval:
                    time_remaining = min_switch_interval - time_since_last_switch
                    device_name = self.available_devices.get(optimal_device_id, optimal_device_id)
                    logger.info(f"⏸️  Rate limited: switch to {device_name} delayed {time_remaining:.1f}s (min interval: {min_switch_interval}s)")
                    return False
            
            # Switch needed
            device_name = self.available_devices.get(optimal_device_id, optimal_device_id)
            
            result = switch_to_device(optimal_device_id)
            if result.get('status') == 'success':
                total_switches += 1
                last_switch_time = time.time()
                trigger_type = "intelligent" if reason else "manual"
                logger.info(f"🔄 Switched to {device_name} - {reason} (switch #{total_switches}, trigger: {trigger_type})")
                last_optimal_gpu = optimal_device_id
                return True
            else:
                logger.error(f"❌ Failed to switch to {device_name}: {result.get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during GPU switch: {e}")
            return False
    
    def run_balancer(self):
        """Main intelligent balancer loop"""
        global service_start_time
        
        logger.info(f"🚀 Starting Intelligent Plex GPU Load Balancer")
        logger.info(f"🔧 Method: {self.balance_settings.get('method', 'unknown')}")
        logger.info(f"⏱️  Check interval: {CHECK_INTERVAL} seconds")
        logger.info(f"🎯 Auto-balancing: {'enabled' if self.balance_settings.get('system', {}).get('auto_balancing_enabled', True) else 'disabled'}")
        
        while True:
            try:
                # Smart config reloading - only reload when config file is actually modified
                if self.should_reload_config():
                    logger.info("🔄 Config file modified, reloading settings...")
                    self.load_settings()
                
                # Check if auto-balancing is enabled
                auto_balancing_enabled = self.balance_settings.get('system', {}).get('auto_balancing_enabled', True)
                
                if not auto_balancing_enabled:
                    if int(time.time()) % 60 == 0:  # Log every minute when disabled
                        logger.info("⏸️  Auto-balancing disabled - manual control active")
                    time.sleep(CHECK_INTERVAL)
                    continue
                
                # Evaluate optimal GPU with detailed debugging
                optimal_device_id, reason = self.evaluate_optimal_gpu()
                
                # Optimized debug logging - more frequent during activity, less during stable periods
                current_sessions = self.get_plex_sessions()
                
                # Debug logging frequency based on activity level
                if current_sessions > 0:
                    # Active transcoding - log every 15 seconds
                    log_debug = int(time.time()) % 15 == 0
                else:
                    # No active sessions - log every 60 seconds to reduce noise
                    log_debug = int(time.time()) % 60 == 0
                
                if log_debug:
                    intel_device_id = self.gpu_devices_mapping.get('gpu2')
                    nvidia_device_id = self.gpu_devices_mapping.get('gpu1')
                    
                    if intel_device_id:
                        intel_sessions = self.get_gpu_session_count(intel_device_id)
                        intel_overloaded, intel_reason = self.is_gpu_overloaded(intel_device_id, self.balance_settings.get('preferred_order', {}))
                        logger.info(f"📊 Intel: {intel_sessions} sessions, overloaded: {intel_overloaded} ({intel_reason})")
                    
                    if nvidia_device_id:
                        nvidia_sessions = self.get_gpu_session_count(nvidia_device_id)
                        nvidia_overloaded, nvidia_reason = self.is_gpu_overloaded(nvidia_device_id, self.balance_settings.get('preferred_order', {}))
                        logger.info(f"📊 NVIDIA: {nvidia_sessions} sessions, overloaded: {nvidia_overloaded} ({nvidia_reason})")
                
                if optimal_device_id:
                    self.switch_gpu_if_needed(optimal_device_id, reason)
                else:
                    logger.warning(f"⚠️  No optimal GPU found: {reason}")
                
                # Status logging every 30 seconds
                if int(time.time()) % 30 == 0:
                    total_sessions = self.get_plex_sessions()
                    uptime = str(datetime.now() - service_start_time).split('.')[0]  # Remove microseconds
                    logger.info(f"📊 Status: {total_sessions} sessions | {total_switches} switches | uptime: {uptime}")
                
                time.sleep(CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("🛑 Stopping intelligent GPU balancer...")
                break
            except Exception as e:
                logger.error(f"❌ Error in balancer loop: {e}")
                time.sleep(CHECK_INTERVAL)

def get_stats():
    """Get current statistics for API endpoints"""
    uptime = str(datetime.now() - service_start_time).split('.')[0]
    return {
        'total_switches': total_switches,
        'uptime': uptime,
        'last_check': datetime.now().strftime('%H:%M:%S'),
        'check_interval': CHECK_INTERVAL,
        'last_optimal_gpu': last_optimal_gpu,
        'version': 'intelligent-v2.1-session-aware'
    }

if __name__ == "__main__":
    logger.info("📊 Using centralized historical data from GPU collector service")
    balancer = IntelligentPlexGPUBalancer()
    balancer.run_balancer()
