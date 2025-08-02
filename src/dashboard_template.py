#!/usr/bin/env python3
"""
Dashboard HTML template generator for Plex GPU Balancer
"""

# Import all component templates
from templates.base_template import get_base_styles, get_base_javascript
from templates.plex_component import get_plex_styles, get_plex_javascript, get_plex_html
from templates.gpu_component import get_gpu_styles, get_gpu_javascript, get_gpu_html
from templates.intel_gpu_component import get_intel_gpu_styles, get_intel_gpu_javascript
from templates.nvidia_gpu_component import get_nvidia_gpu_styles, get_nvidia_gpu_javascript
from templates.balancing_settings_component import get_balancing_settings_styles, get_balancing_settings_javascript, get_balancing_settings_html

def get_dashboard_template():
    """Return the complete HTML template for the dashboard"""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plex GPU Balancer Dashboard</title>
    <style>
        {get_base_styles()}
        {get_plex_styles()}
        {get_gpu_styles()}
        {get_intel_gpu_styles()}
        {get_nvidia_gpu_styles()}
        {get_balancing_settings_styles()}
        
        /* Main Title Container */
        .main-title-container {{
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.05) 100%);
            border-left: 3px solid #fff;
            box-shadow: 0 0 15px rgba(255, 255, 255, 0.1);
            margin-bottom: 20px;
            text-align: center;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        
        .main-title-container .card-title {{
            font-size: 18px;
            font-weight: 500;
            margin: 0;
            color: #fff;
        }}
        
        /* Toast Notification Styles */
        .toast-container {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
            max-width: 350px;
        }}
        
        .toast {{
            background: linear-gradient(135deg, rgba(0, 0, 0, 0.9) 0%, rgba(40, 40, 40, 0.95) 100%);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 10px;
            color: #fff;
            font-size: 13px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
            transform: translateX(400px);
            opacity: 0;
            transition: all 0.3s ease;
            border-left: 4px solid #0096FF;
        }}
        
        .toast.show {{
            transform: translateX(0);
            opacity: 1;
        }}
        
        .toast.success {{
            border-left-color: #00ff41;
        }}
        
        .toast.warning {{
            border-left-color: #ffff00;
        }}
        
        .toast.error {{
            border-left-color: #ff4757;
        }}
        
        .toast-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 4px;
        }}
        
        .toast-title {{
            font-weight: 600;
            font-size: 12px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        
        .toast-time {{
            font-size: 10px;
            color: #999;
        }}
        
        .toast-body {{
            font-size: 11px;
            line-height: 1.4;
            color: #ddd;
        }}
        
        .toast-details {{
            margin-top: 4px;
            font-size: 10px;
            color: #bbb;
            font-style: italic;
        }}

        /* Mobile Responsive Design for Toast and Title */
        @media (max-width: 1024px) {{
            .main-title-container {{
                margin-bottom: 15px;
            }}
            
            .main-title-container .card-title {{
                font-size: 16px;
            }}
            
            .toast-container {{
                bottom: 15px;
                right: 15px;
                max-width: 300px;
            }}
            
            .toast {{
                padding: 10px 12px;
                margin-bottom: 8px;
                font-size: 12px;
            }}
            
            .toast-title {{
                font-size: 11px;
                gap: 5px;
            }}
            
            .toast-time {{
                font-size: 9px;
            }}
            
            .toast-body {{
                font-size: 10px;
            }}
            
            .toast-details {{
                font-size: 9px;
                margin-top: 3px;
            }}
        }}
        
        @media (max-width: 768px) {{
            .main-title-container {{
                margin-bottom: 12px;
            }}
            
            .main-title-container .card-title {{
                font-size: 14px;
            }}
            
            .toast-container {{
                bottom: 10px;
                right: 10px;
                left: 10px;
                max-width: none;
            }}
            
            .toast {{
                padding: 8px 10px;
                margin-bottom: 6px;
                font-size: 11px;
            }}
            
            .toast-title {{
                font-size: 10px;
                gap: 4px;
            }}
            
            .toast-time {{
                font-size: 8px;
            }}
            
            .toast-body {{
                font-size: 9px;
            }}
            
            .toast-details {{
                font-size: 8px;
                margin-top: 2px;
            }}
        }}
        
        @media (max-width: 480px) {{
            .main-title-container {{
                margin-bottom: 10px;
            }}
            
            .main-title-container .card-title {{
                font-size: 13px;
            }}
            
            .toast-container {{
                bottom: 8px;
                right: 8px;
                left: 8px;
            }}
            
            .toast {{
                padding: 6px 8px;
                margin-bottom: 5px;
                font-size: 10px;
            }}
            
            .toast-title {{
                font-size: 9px;
                gap: 3px;
            }}
            
            .toast-time {{
                font-size: 7px;
            }}
            
            .toast-body {{
                font-size: 8px;
            }}
            
            .toast-details {{
                font-size: 7px;
                margin-top: 2px;
            }}
        }}

        /* New Layout Styles */
        .main-layout {{
            display: flex;
            gap: 20px;
            align-items: flex-start;
            min-height: calc(100vh - 200px);
        }}
        
        .plex-section {{
            flex: 1;
            min-width: 0;
        }}
        
        .gpu-section {{
            flex: 2;
            min-width: 0;
            max-width: 66.667%;
        }}
        
        /* Mobile override for GPU section */
        @media (max-width: 1024px) {{
            .gpu-section {{
                flex: none;
                width: 100%;
                max-width: none;
            }}
        }}
        
        /* Ensure device ID is fixed to bottom */
        .gpu-device-card {{
            padding-bottom: 45px; /* Make room for device ID */
        }}
        
        .device-id {{
            position: absolute;
            bottom: 15px;
            left: 15px;
            right: 15px;
        }}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <main class="dashboard-content">
            <!-- Connection Lost Modal -->
            <div id="connection-lost-modal" class="modal-overlay">
                <div class="modal-content">
                    <div class="modal-icon">❌</div>
                    <h2>Connection Lost</h2>
                    <p>Unable to connect to the Plex GPU Balancer service.<br>Please check if the service is running.</p>
                    <div class="modal-actions">
                        <button onclick="retryConnection()" class="retry-btn">Retry Connection</button>
                    </div>
                </div>
            </div>
            
            <!-- Main Title Container -->
            <div class="status-card main-title-container">
                <div class="card-title">Plex GPU Balancer</div>
            </div>
            
            <div class="main-layout">
                <!-- Plex Section (1/3) -->
                <div class="plex-section">
                    {get_plex_html()}
                    {get_balancing_settings_html()}
                </div>
                
                <!-- GPU Section (2/3) -->
                <div class="gpu-section">
                    {get_gpu_html()}
                </div>
            </div>
        </main>
        
        <!-- Toast Notifications Container -->
        <div id="toast-container" class="toast-container"></div>
        
        <footer class="dashboard-footer">
            <div class="footer-content">
                <div class="last-refresh">Last refresh: <span id="last-refresh-time">Never</span></div>
                <div class="blame-text">blame Kotysoft</div>
            </div>
        </footer>
    </div>
    
    <script>
        {get_base_javascript()}
        {get_plex_javascript()}
        {get_gpu_javascript()}
        {get_intel_gpu_javascript()}
        {get_nvidia_gpu_javascript()}
        {get_balancing_settings_javascript()}
        
        // Main initialization
        function loadInitialData() {{
            loadPlexContainer();
            loadGPUDevices();
            loadBalancingSettings();
            updateLastRefresh();
        }}
        
        function switchToDevice(deviceId) {{
            if (!deviceId) {{
                showToast('GPU Switch Error', 'No device ID available', 'error');
                return;
            }}
            
            // Get device name for toast
            const deviceCards = document.querySelectorAll('.gpu-device-card');
            let deviceName = deviceId;
            
            deviceCards.forEach(card => {{
                if (card.getAttribute('data-device-id') === deviceId) {{
                    const nameElement = card.querySelector('.gpu-device-name');
                    if (nameElement) {{
                        deviceName = nameElement.textContent.trim();
                    }}
                }}
            }});
            
            // Immediate UI feedback - disable all buttons during switch
            const allButtons = document.querySelectorAll('.gpu-switch-btn');
            allButtons.forEach(btn => {{
                btn.disabled = true;
                btn.textContent = 'SWITCHING...';
            }});
            
            fetch('/switch-device/' + encodeURIComponent(deviceId), {{method: 'POST'}})
                .then(response => response.json())
                .then(data => {{
                    if (data.status === 'success') {{
                        // Show toast notification for manual switch
                        showGPUSwitchToast(deviceName, deviceId, 'Manual', 'User initiated switch');
                        
                        // Update active device status immediately for better UX
                        updateActiveDeviceStatus(deviceId);
                        
                        // Then refresh all data to confirm the switch
                        setTimeout(() => {{
                            loadInitialData();
                        }}, 1000);  // Increased delay for Plex to process the change
                    }} else {{
                        showToast('GPU Switch Failed', data.message || 'Unknown error occurred', 'error');
                        // Restore button states on failure
                        loadInitialData();
                    }}
                }})
                .catch(error => {{
                    showToast('Network Error', error.message || 'Failed to communicate with server', 'error');
                    // Restore button states on error
                    loadInitialData();
                }});
        }}
        
        // Initialize dashboard
        window.onload = function() {{
            loadInitialData();
            // Auto-refresh GPU metrics every 1000ms (1 second) - optimized from 500ms
            setInterval(refreshGPUMetrics, 1000);
            // Auto-refresh historical data every 1000ms (1 second) - optimized from 500ms
            setInterval(refreshHistoricalData, 1000);
            // Auto-refresh Plex sessions every 2000ms (2 seconds)
            setInterval(refreshPlexSessions, 2000);
            // Track active device changes for toast notifications every 2000ms (2 seconds)
            setInterval(trackActiveDeviceChanges, 2000);
            // Load initial historical data after a short delay
            setTimeout(refreshHistoricalData, 2000);
            // Initialize active device tracking after initial load
            setTimeout(trackActiveDeviceChanges, 3000);
        }};
    </script>
</body>
</html>'''
