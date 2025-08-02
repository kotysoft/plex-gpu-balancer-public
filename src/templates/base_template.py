#!/usr/bin/env python3
"""Base template with shared styles and layout structure"""

def get_base_styles():
    """Return the shared CSS styles"""
    return '''
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%);
            color: #e0e0e0;
            font-size: 13px;
            line-height: 1.4;
        }
        
        .dashboard-container { 
            max-width: 1400px; 
            margin: 0 auto; 
            padding: 15px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .dashboard-header {
            text-align: center;
            margin-bottom: 20px;
        }
        
        .dashboard-content {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        
        .dashboard-footer {
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .footer-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
            color: #666;
        }
        
        .blame-text {
            color: #666;
            font-size: 11px;
        }
        
        .section-title {
            font-size: 18px;
            font-weight: 600;
            color: #fff;
            margin-bottom: 15px;
        }
        
        h1 { 
            color: #ffffff; 
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        /* Modal Overlay */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(5px);
            z-index: 9999;
            display: none;
            align-items: center;
            justify-content: center;
        }
        
        .modal-content {
            background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
            border: 2px solid #ff4757;
            border-radius: 12px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(255, 71, 87, 0.3);
            max-width: 400px;
            width: 90%;
        }
        
        .modal-icon {
            font-size: 48px;
            color: #ff4757;
            margin-bottom: 15px;
        }
        
        .modal-actions {
            margin-top: 20px;
        }
        
        .retry-btn {
            background: #ff4757;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .retry-btn:hover {
            background: #ff3742;
            transform: translateY(-1px);
        }
        
        .main-layout {
            display: flex;
            gap: 20px;
            align-items: flex-start;
            height: 100%;
        }
        
        .plex-section {
            flex: 0 0 33.333%;
            min-width: 0;
        }
        
        .gpu-section {
            flex: 0 0 66.667%;
            min-width: 0;
            max-width: 66.667%;
        }
        
        /* Mobile Responsive Design */
        @media (max-width: 1024px) {
            .main-layout {
                flex-direction: column;
                gap: 12px;
            }
            
            .plex-section,
            .gpu-section {
                flex: none;
                width: 100%;
                max-width: none;
            }
            
            .dashboard-container {
                padding: 10px;
            }
            
            .status-card {
                padding: 10px;
                margin-bottom: 10px;
            }
            
            .card-title {
                font-size: 14px;
                margin-bottom: 10px;
            }
            
            .info-row {
                margin: 6px 0;
                font-size: 11px;
            }
            
            .dashboard-footer {
                margin-top: 15px;
                padding-top: 10px;
            }
        }
        
        @media (max-width: 768px) {
            body {
                font-size: 12px;
            }
            
            .dashboard-container {
                padding: 8px;
            }
            
            .main-layout {
                gap: 8px;
            }
            
            .status-card {
                padding: 8px;
                margin-bottom: 8px;
            }
            
            .card-title {
                font-size: 13px;
                margin-bottom: 8px;
            }
            
            .info-row {
                margin: 4px 0;
                font-size: 10px;
            }
            
            .info-label,
            .info-value {
                font-size: 10px;
            }
            
            h1 {
                font-size: 20px;
                margin-bottom: 8px;
            }
            
            .footer-content {
                font-size: 10px;
            }
            
            .timestamp {
                font-size: 9px;
                margin-top: 10px;
                padding-top: 8px;
            }
        }
        
        @media (max-width: 480px) {
            .dashboard-container {
                padding: 6px;
            }
            
            .main-layout {
                gap: 6px;
            }
            
            .status-card {
                padding: 6px;
                margin-bottom: 6px;
            }
            
            .card-title {
                font-size: 12px;
                margin-bottom: 6px;
            }
            
            .info-row {
                margin: 3px 0;
                font-size: 9px;
            }
            
            .info-label,
            .info-value {
                font-size: 9px;
            }
        }
        
        .status-card { 
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }
        
        .card-title { 
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 15px;
            color: #fff;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
        }
        
        .info-row {
            display: flex;
            justify-content: space-between;
            margin: 8px 0;
            font-size: 12px;
        }
        
        .info-label { 
            color: #a0a0a0; 
            font-weight: 400;
        }
        
        .info-value { 
            color: #ffffff; 
            font-weight: 500;
        }
        
        .timestamp { 
            text-align: center;
            color: #666; 
            font-size: 10px;
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .loading {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            border-top-color: #667eea;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .no-devices {
            text-align: center;
            color: #a0a0a0;
            font-style: italic;
            padding: 40px;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 8px;
            border: 1px dashed rgba(255, 255, 255, 0.1);
        }
        
        /* Connection Lost Modal */
        .connection-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(5px);
            z-index: 9999;
            display: none;
            align-items: center;
            justify-content: center;
        }
        
        .connection-modal.show {
            display: flex;
            animation: fadeIn 0.3s ease-in;
        }
        
        .connection-modal-content {
            background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
            border: 2px solid #ff4757;
            border-radius: 12px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(255, 71, 87, 0.3);
            max-width: 400px;
            width: 90%;
        }
        
        .connection-modal-icon {
            font-size: 48px;
            color: #ff4757;
            margin-bottom: 15px;
        }
        
        .connection-modal-title {
            font-size: 20px;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 10px;
        }
        
        .connection-modal-message {
            font-size: 14px;
            color: #a0a0a0;
            margin-bottom: 25px;
            line-height: 1.5;
        }
        
        .connection-modal-reconnect {
            background: #ff4757;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .connection-modal-reconnect:hover {
            background: #ff3742;
            transform: translateY(-1px);
        }
        
        .screen-fade {
            transition: opacity 0.5s ease;
        }
        
        .screen-fade.faded {
            opacity: 0.3;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: scale(0.9); }
            to { opacity: 1; transform: scale(1); }
        }
    '''

def get_base_javascript():
    """Return the shared JavaScript functionality"""
    return '''
        // Connection status tracking
        let connectionLost = false;
        let connectionModal = null;
        let mainContainer = null;
        
        function updateLastRefresh() {
            const now = new Date();
            const timeString = now.toLocaleTimeString();
            const element = document.getElementById('last-refresh-time');
            if (element) {
                element.textContent = timeString;
            }
        }
        
        // Timeout wrapper for fetch requests
        function fetchWithTimeout(url, options = {}, timeout = 3000) {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeout);
            
            return fetch(url, {
                ...options,
                signal: controller.signal
            }).finally(() => {
                clearTimeout(timeoutId);
            });
        }
        
        // Show connection lost modal
        function showConnectionLostModal() {
            if (connectionLost) return; // Prevent multiple modals
            
            connectionLost = true;
            connectionModal = document.getElementById('connection-lost-modal');
            mainContainer = document.querySelector('.dashboard-container');
            
            // Show the modal
            if (connectionModal) {
                connectionModal.style.display = 'flex';
            }
            
            console.warn('API connection lost - timeout after 3 seconds');
        }
        
        // Hide connection lost modal
        function hideConnectionLostModal() {
            if (!connectionLost) return;
            
            connectionLost = false;
            
            // Hide the modal
            if (connectionModal) {
                connectionModal.style.display = 'none';
            }
            
            console.log('API connection restored');
        }
        
        // Reconnect function called by modal button
        function retryConnection() {
            console.log('Manual reconnection attempt...');
            hideConnectionLostModal();
            
            // Try to reload initial data
            loadInitialData();
        }
        
        // Handle API errors and timeouts
        function handleAPIError(error, context = '') {
            console.error(`API Error in ${context}:`, error);
            
            // Check if it's a timeout or network error
            if (error.name === 'AbortError' || error.message.includes('timeout') || 
                error.message.includes('NetworkError') || error.message.includes('Failed to fetch')) {
                showConnectionLostModal();
            }
        }
        
        function switchToDevice(deviceId) {
            if (!deviceId) {
                alert('No device ID available');
                return;
            }
            
            fetch('/switch-device/' + encodeURIComponent(deviceId), {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        // Reload initial data after GPU switch to update active device
                        setTimeout(loadInitialData, 500);
                    } else {
                        alert('GPU switch failed: ' + data.message);
                    }
                })
                .catch(error => {
                    alert('Network error: ' + error.message);
                });
        }
        
        // Toast Notification System
        let lastActiveDevice = null;
        
        function showToast(title, message, type = 'info', details = null, duration = 5000) {
            const container = document.getElementById('toast-container');
            if (!container) return;
            
            const toast = document.createElement('div');
            toast.className = `toast ${type}`;
            
            const timeString = new Date().toLocaleTimeString();
            const icon = type === 'success' ? '✅' : type === 'warning' ? '⚠️' : type === 'error' ? '❌' : 'ℹ️';
            
            toast.innerHTML = `
                <div class="toast-header">
                    <div class="toast-title">${icon} ${title}</div>
                    <div class="toast-time">${timeString}</div>
                </div>
                <div class="toast-body">${message}</div>
                ${details ? `<div class="toast-details">${details}</div>` : ''}
            `;
            
            container.appendChild(toast);
            
            // Show toast with animation
            setTimeout(() => {
                toast.classList.add('show');
            }, 100);
            
            // Auto remove after duration
            setTimeout(() => {
                removeToast(toast);
            }, duration);
            
            // Click to dismiss
            toast.addEventListener('click', () => removeToast(toast));
        }
        
        function removeToast(toast) {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }
        
        function showGPUSwitchToast(deviceName, deviceId, triggerType, reason) {
            const title = `GPU Switch: ${deviceName}`;
            const message = `Active GPU changed to ${deviceName}`;
            const details = `Trigger: ${triggerType} • Reason: ${reason}`;
            
            showToast(title, message, 'success', details, 6000);
        }
        
        function trackActiveDeviceChanges() {
            // Get current active device
            fetch('/api/gpu-devices')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success' && data.active_device) {
                        const currentActiveDevice = data.active_device;
                        
                        // Check if active device changed
                        if (lastActiveDevice && lastActiveDevice !== currentActiveDevice) {
                            // Find device name
                            const device = data.devices.find(d => d.id === currentActiveDevice);
                            const deviceName = device ? device.name : currentActiveDevice;
                            
                            // Show toast notification
                            showGPUSwitchToast(deviceName, currentActiveDevice, 'Auto-Balancer', 'Load balancing triggered');
                        }
                        
                        lastActiveDevice = currentActiveDevice;
                    }
                })
                .catch(error => {
                    // Silently handle errors for background tracking
                    console.debug('Error tracking active device changes:', error);
                });
        }
    '''

def get_connection_modal_html():
    """Return the connection lost modal HTML"""
    return '''
        <!-- Connection Lost Modal -->
        <div id="connection-modal" class="connection-modal">
            <div class="connection-modal-content">
                <div class="connection-modal-icon">⚠️</div>
                <div class="connection-modal-title">API CONNECTION LOST</div>
                <div class="connection-modal-message">
                    Failed to connect to the backend API within 3 seconds.<br>
                    Please check your network connection or server status.
                </div>
                <button class="connection-modal-reconnect" onclick="reconnectAPI()">
                    Try Reconnect
                </button>
            </div>
        </div>
    '''
