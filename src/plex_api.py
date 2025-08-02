#!/usr/bin/env python3
"""Plex server API interactions"""

import requests
import re
from import_helper import import_config

# Load configuration
load_config = import_config()
config = load_config()
PLEX_SERVER = config['PLEX_SERVER']
PLEX_TOKEN = config['PLEX_TOKEN']

# Dynamic device storage
available_devices = {}

def load_available_devices():
    """Load available GPU devices from Plex preferences and parse individual device info"""
    global available_devices
    try:
        from urllib.parse import unquote
        
        response = requests.get(
            f"http://{PLEX_SERVER}/:/prefs?X-Plex-Token={PLEX_TOKEN}",
            headers={"Accept": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        
        prefs_data = response.json()
        media_container = prefs_data.get('MediaContainer', {})
        settings = media_container.get('Setting', [])
        
        for setting in settings:
            if setting.get('id') == 'HardwareDevicePath':
                enum_values = setting.get('enumValues', '')
                # Parse enumValues: ":Auto|device_id:Device Name|..."
                devices = {}
                for item in enum_values.split('|'):
                    if ':' in item:
                        device_id, device_name = item.split(':', 1)
                        if device_id:  # Skip empty (Auto) option
                            # URL decode the device ID to make it human-readable
                            decoded_device_id = unquote(device_id)
                            devices[decoded_device_id] = device_name
                available_devices = devices
                return devices
                
    except Exception as e:
        return {}

def get_parsed_gpu_devices():
    """Get parsed GPU devices with individual info for dashboard containers"""
    global available_devices
    
    # Load devices if not already loaded
    if not available_devices:
        load_available_devices()
    
    devices = []
    device_name_counters = {}  # Track duplicate names
    
    for device_id, device_full_name in available_devices.items():
        # Extract device name from brackets [Device Name]
        import re
        bracket_match = re.search(r'\[([^\]]+)\]', device_full_name)
        device_name = bracket_match.group(1) if bracket_match else device_full_name.strip()
        
        # Determine device type
        if 'nvidia' in device_full_name.lower() or '10de' in device_id:
            device_type = 'nvidia'
            glow_color = '#76b900'  # Green for NVIDIA
        elif 'intel' in device_full_name.lower() or '8086' in device_id:
            device_type = 'intel' 
            glow_color = '#0071c5'  # Blue for Intel
        else:
            device_type = 'unknown'
            glow_color = '#666666'  # Gray for unknown
        
        # Handle duplicate device names by adding counter
        if device_name in device_name_counters:
            device_name_counters[device_name] += 1
            display_name = f"{device_name} {device_name_counters[device_name]}"
        else:
            device_name_counters[device_name] = 1
            display_name = device_name
        
        devices.append({
            'id': device_id,
            'name': display_name,
            'full_name': device_full_name,
            'type': device_type,
            'glow_color': glow_color
        })
    
    return devices

def get_current_active_device():
    """Get the currently active GPU device ID"""
    try:
        from urllib.parse import unquote
        
        response = requests.get(
            f"http://{PLEX_SERVER}/:/prefs?X-Plex-Token={PLEX_TOKEN}",
            headers={"Accept": "application/json"},
            timeout=5
        )
        response.raise_for_status()
        
        prefs_data = response.json()
        media_container = prefs_data.get('MediaContainer', {})
        settings = media_container.get('Setting', [])
        
        for setting in settings:
            if setting.get('id') == 'HardwareDevicePath':
                active_device = setting.get('value', '')
                # Decode the device ID to match our stored format
                return unquote(active_device) if active_device else ''
                
    except Exception as e:
        return None
    
    return None

def get_all_active_sessions():
    """Get all active sessions for display purposes"""
    try:
        sessions_response = requests.get(
            f"http://{PLEX_SERVER}/status/sessions?X-Plex-Token={PLEX_TOKEN}",
            headers={"Accept": "application/json"},
            timeout=5
        )
        sessions_data = sessions_response.json().get('MediaContainer', {})
        session_items = sessions_data.get('Metadata', [])
        
        all_sessions = []
        for session in session_items:
            # Extract session info
            user = session.get('User', {}).get('title', 'Unknown User')
            title = session.get('title', 'Unknown Title')
            media_type = session.get('type', 'unknown')
            
            # Get player info
            player = session.get('Player', {})
            device = player.get('title', 'Unknown Device')
            platform = player.get('platform', 'Unknown Platform')
            
            # Check transcoding status separately for video and audio
            video_transcoding = False
            audio_transcoding = False
            
            transcode_session = session.get('TranscodeSession')
            if transcode_session:
                video_decision = transcode_session.get('videoDecision', 'copy')
                audio_decision = transcode_session.get('audioDecision', 'copy')
                video_transcoding = video_decision == 'transcode'
                audio_transcoding = audio_decision == 'transcode'
            
            # Get media info
            media_info = session.get('Media', [{}])[0] if session.get('Media') else {}
            resolution = media_info.get('videoResolution', 'Unknown')
            codec = media_info.get('videoCodec', 'Unknown')
            
            all_sessions.append({
                'user': user,
                'title': title,
                'type': media_type,
                'device': device,
                'platform': platform,
                'video_transcoding': video_transcoding,
                'audio_transcoding': audio_transcoding,
                'transcoding': video_transcoding or audio_transcoding,
                'resolution': resolution,
                'codec': codec
            })
        
        return all_sessions
    except Exception as e:
        return []

def get_plex_status():
    """Get Plex server status and video transcoding session count"""
    try:
        # Get detailed sessions info
        sessions_response = requests.get(
            f"http://{PLEX_SERVER}/status/sessions?X-Plex-Token={PLEX_TOKEN}",
            headers={"Accept": "application/json"},
            timeout=5
        )
        sessions_data = sessions_response.json().get('MediaContainer', {})
        
        # Count only video transcoding sessions
        video_transcoding_sessions = 0
        session_items = sessions_data.get('Metadata', [])
        
        for session in session_items:
            # Check if this is a video session with active transcoding
            media_items = session.get('Media', [])
            for media in media_items:
                # Check if it's video media
                if media.get('videoCodec'):  # Has video codec = video content
                    # Check for active transcoding session
                    transcode_session = session.get('TranscodeSession')
                    if transcode_session:
                        # Verify it's actually transcoding (not just copying/direct stream)
                        video_decision = transcode_session.get('videoDecision', '')
                        if video_decision == 'transcode':
                            video_transcoding_sessions += 1
                            break  # Count this session once even if multiple media parts
        
        # Get server info
        try:
            server_response = requests.get(
                f"http://{PLEX_SERVER}/?X-Plex-Token={PLEX_TOKEN}",
                headers={"Accept": "application/json"},
                timeout=5
            )
            server_info = server_response.json().get('MediaContainer', {})
            server_name = server_info.get('friendlyName', 'Unknown')
            server_version = server_info.get('version', 'Unknown')
            platform = server_info.get('platform', 'Unknown')
            
            return {
                'sessions': video_transcoding_sessions, 
                'status': 'online',
                'server_name': server_name,
                'version': server_version,
                'platform': platform
            }
        except:
            return {'sessions': video_transcoding_sessions, 'status': 'online', 'server_name': 'Unknown', 'version': 'Unknown', 'platform': 'Unknown'}
    except:
        return {'sessions': 0, 'status': 'offline', 'server_name': 'Unknown', 'version': 'Unknown', 'platform': 'Unknown'}

def get_current_gpu():
    """Get current GPU from Plex preferences using JSON API"""
    global available_devices
    
    # Load devices if not already loaded
    if not available_devices:
        load_available_devices()
    
    try:
        response = requests.get(
            f"http://{PLEX_SERVER}/:/prefs?X-Plex-Token={PLEX_TOKEN}",
            headers={"Accept": "application/json"},
            timeout=5
        )
        response.raise_for_status()
        
        # Try JSON parsing first
        try:
            prefs_data = response.json()
            
            # Find HardwareDevicePath in JSON structure
            media_container = prefs_data.get('MediaContainer', {})
            settings = media_container.get('Setting', [])
            
            current_device = None
            for setting in settings:
                if setting.get('id') == 'HardwareDevicePath':
                    current_device = setting.get('value', '')
                    break
                    
        except (ValueError, KeyError):
            # Fallback to XML parsing if JSON fails
            prefs_text = response.text
            hardware_pattern = r'<Setting\s+id="HardwareDevicePath"[^>]*value="([^"]*)"'
            match = re.search(hardware_pattern, prefs_text, re.DOTALL | re.IGNORECASE)
            current_device = match.group(1) if match else None
        
        if current_device and available_devices:
            # Check which GPU is active using dynamic device list
            for device_id, device_name in available_devices.items():
                if device_id == current_device:
                    if 'nvidia' in device_name.lower() or '10de' in device_id:
                        return f"🟢 {device_name}"
                    elif 'intel' in device_name.lower() or '8086' in device_id:
                        return f"🔵 {device_name}"
                    else:
                        return f"⚪ {device_name}"
            return f"❓ UNKNOWN GPU: {current_device}"
        else:
            return "❌ NO HARDWARE PATH FOUND"
            
    except Exception as e:
        return f"❌ ERROR: {str(e)[:50]}"

def switch_to_device(device_id):
    """Switch to a specific device by device ID"""
    global available_devices
    
    # Load devices if not already loaded
    if not available_devices:
        load_available_devices()
    
    # Verify device exists
    if device_id not in available_devices:
        return {'status': 'error', 'message': f'Device ID {device_id} not found'}
    
    device_name = available_devices[device_id]
    
    try:
        response = requests.put(
            f"http://{PLEX_SERVER}/:/prefs",
            params={
                "HardwareDevicePath": device_id,
                "X-Plex-Token": PLEX_TOKEN
            },
            headers={"Accept": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        
        # Determine GPU type based on device
        if "nvidia" in device_name.lower() or "10de" in device_id:
            gpu_type = "NVIDIA"
        elif "intel" in device_name.lower() or "8086" in device_id:
            gpu_type = "INTEL"
        else:
            gpu_type = "UNKNOWN"
        
        return {
            'status': 'success', 
            'device_id': device_id,
            'device_name': device_name,
            'gpu_type': gpu_type
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def switch_gpu_by_type(gpu_type):
    """Switch to GPU by type (nvidia/intel)"""
    global available_devices
    
    # Load devices if not already loaded
    if not available_devices:
        load_available_devices()
    
    # Find appropriate device from available devices
    device_id = None
    target_type = gpu_type.lower()
    
    for dev_id, dev_name in available_devices.items():
        if (target_type == "nvidia" and ("nvidia" in dev_name.lower() or "10de" in dev_id)) or \
           (target_type == "intel" and ("intel" in dev_name.lower() or "8086" in dev_id)):
            device_id = dev_id
            break
    
    if not device_id:
        return {'status': 'error', 'message': f'No {gpu_type.upper()} device found'}
    
    try:
        response = requests.put(
            f"http://{PLEX_SERVER}/:/prefs",
            params={
                "HardwareDevicePath": device_id,
                "X-Plex-Token": PLEX_TOKEN
            },
            headers={"Accept": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        
        return {'status': 'success', 'gpu': gpu_type.upper()}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def get_plex_settings():
    """Get specific Plex server settings for dashboard display"""
    try:
        response = requests.get(
            f"http://{PLEX_SERVER}/:/prefs?X-Plex-Token={PLEX_TOKEN}",
            headers={"Accept": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        
        prefs_data = response.json()
        media_container = prefs_data.get('MediaContainer', {})
        settings = media_container.get('Setting', [])
        
        # Extract the specific settings we need
        settings_map = {}
        for setting in settings:
            settings_map[setting.get('id')] = setting.get('value')
        
        # Get the specific values requested
        friendly_name = settings_map.get('FriendlyName', 'Unknown')
        transcoder_throttle_buffer = settings_map.get('TranscoderThrottleBuffer', 'Unknown')
        transcoder_h264_preset = settings_map.get('TranscoderH264Preset', 'Unknown')
        transcoder_h264_bg_preset = settings_map.get('TranscoderH264BackgroundPreset', 'Unknown')
        transcode_count_limit = settings_map.get('TranscodeCountLimit', 'Unknown')
        
        # Format transcode count limit
        if transcode_count_limit == '0' or transcode_count_limit == 0:
            transcode_count_limit = 'Unlimited'
        
        return {
            'status': 'success',
            'friendly_name': friendly_name,
            'transcoder_throttle_buffer': transcoder_throttle_buffer,
            'transcoder_h264_preset': transcoder_h264_preset,
            'transcoder_h264_background_preset': transcoder_h264_bg_preset,
            'transcode_count_limit': transcode_count_limit
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'friendly_name': 'Error',
            'transcoder_throttle_buffer': 'Error',
            'transcoder_h264_preset': 'Error',
            'transcoder_h264_background_preset': 'Error',
            'transcode_count_limit': 'Error'
        }

def get_debug_info():
    """Get debug information for troubleshooting"""
    global available_devices
    
    # Load devices if not already loaded
    if not available_devices:
        load_available_devices()
    
    try:
        # Get current preferences
        response = requests.get(
            f"http://{PLEX_SERVER}/:/prefs?X-Plex-Token={PLEX_TOKEN}",
            headers={"Accept": "application/json"},
            timeout=5
        )
        
        prefs_data = response.text
        current_gpu_status = get_current_gpu()
        
        return {
            'status_code': response.status_code,
            'gpu_detection': current_gpu_status,
            'raw_prefs': prefs_data[:500] if len(prefs_data) > 500 else prefs_data,
            'available_devices': available_devices,
            'plex_server': PLEX_SERVER
        }
        
    except Exception as e:
        return {
            'status_code': 'ERROR',
            'gpu_detection': f'Error: {str(e)}',
            'raw_prefs': 'Failed to fetch',
            'available_devices': available_devices,
            'plex_server': PLEX_SERVER
        }
