#!/usr/bin/env python3
"""Balance configuration handler for GPU load balancing settings"""

import configparser
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from plex_api import load_available_devices

CONFIG_FILE = 'balance.conf'

def get_config_file_path():
    """Get the full path to the balance.conf file"""
    # Look for balance.conf in the root project directory
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(root_dir, CONFIG_FILE)

def create_default_config():
    """Create a default balance.conf file with auto-discovered GPU devices"""
    config = configparser.ConfigParser()
    config.optionxform = str  # Preserve case sensitivity
    
    # Add header comment (will be lost in configparser, but we'll add it manually)
    config.add_section('gpu_devices')
    config.add_section('balancing_method')
    config.add_section('gpu_priority')
    config.add_section('preferred_order_settings')
    config.add_section('split_sessions_settings')
    config.add_section('max_sessions')
    config.add_section('rate_limiting')
    config.add_section('system')
    
    # Set default values
    config.set('balancing_method', 'method', 'preferred-order')
    
    config.set('preferred_order_settings', 'load_threshold_percentage', '80')
    config.set('preferred_order_settings', 'load_threshold_seconds', '30')
    
    config.set('split_sessions_settings', 'load_limit_percentage', '75')
    config.set('split_sessions_settings', 'load_limit_seconds', '60')
    
    config.set('rate_limiting', 'min_switch_interval_seconds', '10')
    config.set('rate_limiting', 'enabled', 'true')
    
    config.set('system', 'auto_restart_service', 'true')
    config.set('system', 'auto_balancing_enabled', 'true')
    config.set('system', 'config_version', '1.0')
    
    # Try to auto-populate GPU devices
    try:
        devices = load_available_devices()
        if devices and isinstance(devices, dict):
            # Add GPU devices from dict {device_id: device_name}
            for i, (device_id, device_name) in enumerate(devices.items(), 1):
                config.set('gpu_devices', f'gpu{i}', device_id)
                
                # Set default max sessions
                config.set('max_sessions', f'gpu{i}_max_sessions', '5')
                
                # Initialize global priority settings (empty by default)
                if i <= 3:  # Only set up to 3 priorities initially
                    config.set('gpu_priority', f'priority_{i}', '')
    except Exception as e:
        print(f"Warning: Could not auto-populate GPU devices: {e}")
    
    return config

def load_balance_config():
    """Load balance configuration from balance.conf file"""
    config_path = get_config_file_path()
    
    try:
        if not os.path.exists(config_path):
            print("balance.conf not found, creating default configuration...")
            config = create_default_config()
            save_balance_config(config)
            return config
            
        config = configparser.ConfigParser()
        config.optionxform = str  # Preserve case sensitivity
        config.read(config_path)
        
        # Validate required sections exist
        required_sections = ['gpu_devices', 'balancing_method', 'preferred_order_settings', 
                           'split_sessions_settings', 'max_sessions', 'system']
        
        for section in required_sections:
            if not config.has_section(section):
                print(f"Missing section '{section}' in balance.conf, recreating...")
                config = create_default_config()
                save_balance_config(config)
                break
                
        return config
        
    except Exception as e:
        print(f"Error loading balance.conf: {e}")
        print("Creating new default configuration...")
        config = create_default_config()
        save_balance_config(config)
        return config

def save_balance_config(config):
    """Save balance configuration to balance.conf file"""
    config_path = get_config_file_path()
    
    try:
        # Update timestamp in system section
        if config.has_section('system'):
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
            config.set('system', 'last_updated', timestamp)
        
        # Write config with custom header
        with open(config_path, 'w') as f:
            f.write("# Plex GPU Load Balancer Configuration\n")
            f.write("# Auto-generated configuration file for GPU balancing settings\n")
            f.write(f"# Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
            config.write(f)
            
        return True
        
    except Exception as e:
        print(f"Error saving balance.conf: {e}")
        return False

def get_gpu_devices_mapping():
    """Get the GPU devices mapping from config"""
    config = load_balance_config()
    devices = {}
    
    if config.has_section('gpu_devices'):
        for key, value in config.items('gpu_devices'):
            devices[key] = value
            
    return devices

def get_current_settings():
    """Get current balancing settings as a dictionary"""
    config = load_balance_config()
    settings = {}
    
    try:
        # Get balancing method
        if config.has_section('balancing_method'):
            settings['method'] = config.get('balancing_method', 'method', fallback='preferred-order')
        
        # Get global GPU priorities
        settings['gpu_priorities'] = {}
        if config.has_section('gpu_priority'):
            for key, value in config.items('gpu_priority'):
                if key.startswith('priority_'):
                    settings['gpu_priorities'][key] = value
        
        # Get preferred order settings
        if config.has_section('preferred_order_settings'):
            settings['preferred_order'] = {}
            settings['preferred_order']['load_threshold_percentage'] = config.getint('preferred_order_settings', 'load_threshold_percentage', fallback=80)
            settings['preferred_order']['load_threshold_seconds'] = config.getint('preferred_order_settings', 'load_threshold_seconds', fallback=30)
        
        # Get split sessions settings
        if config.has_section('split_sessions_settings'):
            settings['split_sessions'] = {}
            settings['split_sessions']['load_limit_percentage'] = config.getint('split_sessions_settings', 'load_limit_percentage', fallback=75)
            settings['split_sessions']['load_limit_seconds'] = config.getint('split_sessions_settings', 'load_limit_seconds', fallback=60)
        
        # Get max sessions
        if config.has_section('max_sessions'):
            settings['max_sessions'] = {}
            for key, value in config.items('max_sessions'):
                settings['max_sessions'][key] = config.getint('max_sessions', key, fallback=5)
        
        # Get GPU devices
        settings['gpu_devices'] = get_gpu_devices_mapping()
        
        # Get rate limiting settings
        if config.has_section('rate_limiting'):
            settings['rate_limiting'] = {}
            settings['rate_limiting']['min_switch_interval_seconds'] = config.getint('rate_limiting', 'min_switch_interval_seconds', fallback=10)
            settings['rate_limiting']['enabled'] = config.getboolean('rate_limiting', 'enabled', fallback=True)
        
        # Get system settings
        if config.has_section('system'):
            settings['system'] = {}
            settings['system']['auto_balancing_enabled'] = config.getboolean('system', 'auto_balancing_enabled', fallback=True)
            settings['system']['auto_restart_service'] = config.getboolean('system', 'auto_restart_service', fallback=True)
        
        return settings
        
    except Exception as e:
        print(f"Error getting current settings: {e}")
        return {}

def update_settings(settings_data):
    """Update balancing settings from provided data"""
    try:
        config = load_balance_config()
        
        # Update balancing method
        if 'method' in settings_data:
            config.set('balancing_method', 'method', settings_data['method'])
        
        # Update global GPU priorities from either method
        priorities_to_save = {}
        if 'preferred_order' in settings_data and 'priorities' in settings_data['preferred_order']:
            priorities_to_save = settings_data['preferred_order']['priorities']
        elif 'split_sessions' in settings_data and 'priorities' in settings_data['split_sessions']:
            priorities_to_save = settings_data['split_sessions']['priorities']
        
        # Save priorities to global gpu_priority section
        if priorities_to_save:
            if not config.has_section('gpu_priority'):
                config.add_section('gpu_priority')
            for priority_key, gpu_value in priorities_to_save.items():
                config.set('gpu_priority', priority_key, gpu_value)
        
        # Update preferred order settings
        if 'preferred_order' in settings_data:
            po_data = settings_data['preferred_order']
            
            if 'load_threshold_percentage' in po_data:
                config.set('preferred_order_settings', 'load_threshold_percentage', str(po_data['load_threshold_percentage']))
            
            if 'load_threshold_seconds' in po_data:
                config.set('preferred_order_settings', 'load_threshold_seconds', str(po_data['load_threshold_seconds']))
        
        # Update split sessions settings
        if 'split_sessions' in settings_data:
            ss_data = settings_data['split_sessions']
            
            if 'load_limit_percentage' in ss_data:
                config.set('split_sessions_settings', 'load_limit_percentage', str(ss_data['load_limit_percentage']))
            
            if 'load_limit_seconds' in ss_data:
                config.set('split_sessions_settings', 'load_limit_seconds', str(ss_data['load_limit_seconds']))
        
        # Update max sessions
        if 'max_sessions' in settings_data:
            for gpu_key, session_count in settings_data['max_sessions'].items():
                config.set('max_sessions', gpu_key, str(session_count))
        
        # Update rate limiting settings
        if 'rate_limiting' in settings_data:
            rate_data = settings_data['rate_limiting']
            if not config.has_section('rate_limiting'):
                config.add_section('rate_limiting')
            
            if 'min_switch_interval_seconds' in rate_data:
                config.set('rate_limiting', 'min_switch_interval_seconds', str(rate_data['min_switch_interval_seconds']))
            
            if 'enabled' in rate_data:
                config.set('rate_limiting', 'enabled', str(rate_data['enabled']).lower())
        
        # Update system settings
        if 'system' in settings_data:
            system_data = settings_data['system']
            if 'auto_balancing_enabled' in system_data:
                config.set('system', 'auto_balancing_enabled', str(system_data['auto_balancing_enabled']).lower())
        
        # Save the updated config
        return save_balance_config(config)
        
    except Exception as e:
        print(f"Error updating settings: {e}")
        return False

def refresh_gpu_devices():
    """Refresh GPU devices from Plex API and update config"""
    try:
        config = load_balance_config()
        devices = load_available_devices()
        
        if not devices:
            print("Warning: No devices returned from Plex API")
            return False
            
        # Handle case where devices might be a string (error message)
        if isinstance(devices, str):
            print(f"Warning: Devices API returned string: {devices}")
            return False
            
        # Ensure devices is a dict (load_available_devices returns dict)
        if not isinstance(devices, dict):
            print(f"Warning: Devices is not a dict: {type(devices)}")
            return False
            
        # Clear existing GPU devices
        config.remove_section('gpu_devices')
        config.add_section('gpu_devices')
        
        # Add current devices from dict {device_id: device_name}
        for i, (device_id, device_name) in enumerate(devices.items(), 1):
            config.set('gpu_devices', f'gpu{i}', device_id)
            
            # Add max sessions if not exists
            gpu_sessions_key = f'gpu{i}_max_sessions'
            if not config.has_option('max_sessions', gpu_sessions_key):
                config.set('max_sessions', gpu_sessions_key, '5')
        
        return save_balance_config(config)
        
    except Exception as e:
        print(f"Error refreshing GPU devices: {e}")
        return False

if __name__ == '__main__':
    # Test the configuration system
    print("Testing balance configuration system...")
    
    # Load config
    config = load_balance_config()
    print("✅ Configuration loaded successfully")
    
    # Get current settings
    settings = get_current_settings()
    print("✅ Current settings retrieved")
    print(f"Current method: {settings.get('method', 'unknown')}")
    print(f"GPU devices: {len(settings.get('gpu_devices', {}))}")
    
    # Test refresh devices
    refresh_result = refresh_gpu_devices()
    print(f"✅ Device refresh: {'Success' if refresh_result else 'Failed'}")
