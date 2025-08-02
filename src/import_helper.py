#!/usr/bin/env python3
"""
Bulletproof import helper for Plex GPU Balancer
Handles imports regardless of execution context
"""

import sys
import os
from pathlib import Path

def setup_imports():
    """Setup proper import paths for the project"""
    # Get the directory where this script is located
    current_dir = Path(__file__).parent.absolute()
    
    # Get the project root (parent of src)
    project_root = current_dir.parent
    
    # Add both src and project root to Python path if not already there
    src_path = str(current_dir)
    root_path = str(project_root)
    
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    if root_path not in sys.path:
        sys.path.insert(0, root_path)

def import_config():
    """Import config module with fallback strategies"""
    setup_imports()
    
    # Try multiple import strategies
    try:
        # Try direct import (works when run from src/)
        from config import load_config
        return load_config
    except ImportError:
        try:
            # Try with src prefix (works when run from project root)
            from src.config import load_config
            return load_config
        except ImportError:
            try:
                # Try absolute path import
                import importlib.util
                config_path = Path(__file__).parent / 'config.py'
                spec = importlib.util.spec_from_file_location("config", config_path)
                config_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(config_module)
                return config_module.load_config
            except Exception as e:
                raise ImportError(f"Could not import config module: {e}")

def import_plex_api():
    """Import plex_api functions with fallback strategies"""
    setup_imports()
    
    try:
        from plex_api import get_parsed_gpu_devices, load_available_devices
        return get_parsed_gpu_devices, load_available_devices
    except ImportError:
        try:
            from src.plex_api import get_parsed_gpu_devices, load_available_devices
            return get_parsed_gpu_devices, load_available_devices
        except ImportError as e:
            raise ImportError(f"Could not import plex_api functions: {e}")

def import_gpu_monitors():
    """Import GPU monitor functions with fallback strategies"""
    setup_imports()
    
    # Intel GPU monitor
    try:
        from intel_gpu_monitor import start_intel_monitor, get_all_intel_gpu_data
        intel_funcs = (start_intel_monitor, get_all_intel_gpu_data)
    except ImportError:
        try:
            from src.intel_gpu_monitor import start_intel_monitor, get_all_intel_gpu_data
            intel_funcs = (start_intel_monitor, get_all_intel_gpu_data)
        except ImportError:
            intel_funcs = (None, None)
    
    # NVIDIA GPU monitor
    try:
        from nvidia_gpu_monitor import start_nvidia_monitor, get_all_nvidia_gpu_data
        nvidia_funcs = (start_nvidia_monitor, get_all_nvidia_gpu_data)
    except ImportError:
        try:
            from src.nvidia_gpu_monitor import start_nvidia_monitor, get_all_nvidia_gpu_data
            nvidia_funcs = (start_nvidia_monitor, get_all_nvidia_gpu_data)
        except ImportError:
            nvidia_funcs = (None, None)
    
    return intel_funcs, nvidia_funcs

def import_gpu_metrics():
    """Import GPU metrics functions with fallback strategies"""
    setup_imports()
    
    try:
        from gpu_metrics import get_all_gpu_metrics
        return get_all_gpu_metrics
    except ImportError:
        try:
            from src.gpu_metrics import get_all_gpu_metrics
            return get_all_gpu_metrics
        except ImportError as e:
            raise ImportError(f"Could not import gpu_metrics: {e}")
