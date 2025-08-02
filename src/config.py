#!/usr/bin/env python3
"""Configuration management for Plex GPU Load Balancer"""

import configparser
import os

def get_project_root():
    """Get the project root directory from config"""
    # Get the directory containing this script (src/), then go up one level
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Look for config.conf in the project root
    config_file = os.path.join(project_root, 'config.conf')
    if os.path.exists(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        if config.has_section('system') and config.has_option('system', 'project_path'):
            return config.get('system', 'project_path')
    
    # Fallback to detected project root
    return project_root

def load_config():
    """Load configuration from config file"""
    project_root = get_project_root()
    config_file = os.path.join(project_root, 'config.conf')
    
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    
    config = configparser.ConfigParser()
    config.read(config_file)
    
    plex_server = config.get('plex', 'server')
    plex_token = config.get('plex', 'token')
    
    return {
        'PLEX_SERVER': plex_server,
        'PLEX_TOKEN': plex_token,
        'PROJECT_ROOT': project_root,
        'VERSION': 'v1.0.0'
    }
