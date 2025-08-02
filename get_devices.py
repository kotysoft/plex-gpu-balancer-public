import sys
sys.path.append('src')
from plex_api import load_available_devices
import json

devices = load_available_devices()
print(json.dumps(devices, indent=4))
