#!/usr/bin/env python3
"""Balancing Settings component template"""

def get_balancing_settings_styles():
    """Return the Balancing Settings-specific CSS styles"""
    return '''
        /* Balancing Settings Container */
        .balancing-settings-container {
            background: linear-gradient(135deg, rgba(0, 150, 255, 0.03) 0%, rgba(255, 255, 255, 0.05) 100%);
            border-left: 3px solid #0096FF;
            box-shadow: 0 0 15px rgba(0, 150, 255, 0.2);
            margin-top: 20px;
        }
        
        .balancing-settings-container * {
            box-sizing: border-box;
        }
        
        /* All form inputs and selects */
        .balancing-settings-container input,
        .balancing-settings-container select {
            padding: 4px 6px;
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 3px;
            color: #fff !important;
            font-size: 11px;
            font-family: inherit;
            transition: all 0.2s ease;
            margin: 0;
            text-align: center;
        }
        
        .balancing-settings-container input:focus,
        .balancing-settings-container select:focus {
            outline: none !important;
            border-color: #0096FF !important;
            box-shadow: 0 0 8px rgba(0, 150, 255, 0.3) !important;
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.08) 100%) !important;
        }
        
        /* Dropdown options */
        .balancing-settings-container select option {
            background: #1a1a1a !important;
            color: #fff !important;
            font-size: 11px !important;
            padding: 4px 8px !important;
        }
        
        .balancing-settings-container select option:hover {
            background: #333 !important;
        }
        
        .balancing-settings-container select option.selected {
            background: #333 !important;
            color: #999 !important;
        }
        
        /* Layout */
        .settings-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 8px;
        }
        
        .form-group {
            margin-bottom: 6px;
        }
        
        .form-group label {
            display: block;
            color: #fff;
            font-size: 11px;
            margin-bottom: 2px;
            font-weight: normal;
        }
        
        .settings-section h3 {
            font-size: 11px;
            color: #fff;
            margin: 8px 0 4px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding-bottom: 2px;
            padding-top: 15px;
            font-weight: bold;
        }
        
        /* GPU Order Styling */
        .order-list {
            display: flex;
            flex-direction: column;
            gap: 4px;
            margin-top: 10px;
        }
        
        .order-item {
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        .order-badge {
            background: linear-gradient(135deg, #0096FF 0%, #0077CC 100%);
            color: white;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            font-weight: bold;
            flex-shrink: 0;
            box-shadow: 0 1px 2px rgba(0, 150, 255, 0.3);
        }
        
        .order-item select {
            flex: 1;
        }
        
        /* Device Session Styling */
        .device-session-list {
            display: flex;
            flex-direction: column;
            gap: 4px;
            margin-top: 10px;
        }
        
        .device-session-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 6px;
        }
        
        .device-name {
            color: #fff;
            font-size: 11px;
            flex: 1;
            font-weight: normal;
        }
        
        .device-session-item input {
            width: 50px;
            flex: none;
        }
        
        /* Threshold Inputs */
        .threshold-inputs {
            display: flex;
            gap: 6px;
            align-items: end;
            margin-top: 10px;
        }
        
        .threshold-input-group {
            flex: 1;
        }
        
        .threshold-input-group label {
            font-size: 11px;
            margin-bottom: 2px;
            font-weight: normal;
        }
        
        /* Method Description */
        .method-description {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 3px;
            padding: 8px;
            margin: 6px 0 12px 0;
            font-size: 10px;
            color: #ccc;
            line-height: 1.3;
        }
        
        /* Global Toggle Styles */
        .global-toggle-container {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 3px;
            padding: 8px;
            margin-bottom: 3px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .toggle-label {
            color: #fff;
            font-size: 11px;
            font-weight: bold;
        }
        
        .toggle-switch {
            position: relative;
            width: 40px;
            height: 20px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            cursor: pointer;
            transition: background 0.3s ease;
        }
        
        .toggle-switch.active {
            background: rgba(0, 150, 255, 0.8);
        }
        
        .toggle-slider {
            position: absolute;
            top: 2px;
            left: 2px;
            width: 16px;
            height: 16px;
            background: #fff;
            border-radius: 50%;
            transition: transform 0.3s ease;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
        }
        
        .toggle-switch.active .toggle-slider {
            transform: translateX(20px);
        }
        
        /* Save Button */
        .save-restart-btn {
            background: rgba(0, 150, 255, 0.8);
            color: #fff;
            border: none;
            padding: 6px 20px;
            border-radius: 3px;
            font-size: 10px;
            font-weight: 500;
            cursor: pointer;
            width: auto;
            margin: 25px auto 0 auto;
            display: block;
            min-width: 70px;
        }
        
        .save-restart-btn:hover {
            background: rgba(0, 150, 255, 1);
        }
        
        .hidden {
            display: none;
        }
        
        /* Mobile Responsive Design for Balancing Settings */
        @media (max-width: 1024px) {
            .balancing-settings-container {
                margin-top: 15px;
            }
            
            .settings-section h3 {
                font-size: 10px;
                margin: 6px 0 3px 0;
                padding-top: 12px;
                padding-bottom: 2px;
            }
            
            .form-group label {
                font-size: 10px;
                margin-bottom: 2px;
            }
            
            .balancing-settings-container input,
            .balancing-settings-container select {
                padding: 3px 5px;
                font-size: 10px;
            }
            
            .global-toggle-container {
                padding: 6px;
                margin-bottom: 2px;
            }
            
            .toggle-label {
                font-size: 10px;
            }
            
            .toggle-switch {
                width: 35px;
                height: 18px;
            }
            
            .toggle-slider {
                width: 14px;
                height: 14px;
            }
            
            .toggle-switch.active .toggle-slider {
                transform: translateX(17px);
            }
            
            .method-description {
                padding: 6px;
                margin: 4px 0 10px 0;
                font-size: 9px;
            }
            
            .order-list {
                gap: 3px;
                margin-top: 8px;
            }
            
            .order-item {
                gap: 5px;
            }
            
            .order-badge {
                width: 16px;
                height: 16px;
                font-size: 9px;
            }
            
            .device-session-list {
                gap: 3px;
                margin-top: 8px;
            }
            
            .device-session-item {
                gap: 5px;
            }
            
            .device-name {
                font-size: 10px;
            }
            
            .device-session-item input {
                width: 45px;
            }
            
            .threshold-inputs {
                gap: 5px;
                margin-top: 8px;
            }
            
            .threshold-input-group label {
                font-size: 10px;
            }
            
            .save-restart-btn {
                padding: 5px 15px;
                font-size: 9px;
                margin: 20px auto 0 auto;
                min-width: 60px;
            }
        }
        
        @media (max-width: 768px) {
            .balancing-settings-container {
                margin-top: 12px;
            }
            
            .settings-section h3 {
                font-size: 9px;
                margin: 5px 0 2px 0;
                padding-top: 10px;
                padding-bottom: 1px;
            }
            
            .form-group label {
                font-size: 9px;
                margin-bottom: 1px;
            }
            
            .balancing-settings-container input,
            .balancing-settings-container select {
                padding: 2px 4px;
                font-size: 9px;
            }
            
            .global-toggle-container {
                padding: 5px;
                margin-bottom: 2px;
            }
            
            .toggle-label {
                font-size: 9px;
            }
            
            .toggle-switch {
                width: 30px;
                height: 16px;
            }
            
            .toggle-slider {
                width: 12px;
                height: 12px;
            }
            
            .toggle-switch.active .toggle-slider {
                transform: translateX(14px);
            }
            
            .method-description {
                padding: 5px;
                margin: 3px 0 8px 0;
                font-size: 8px;
            }
            
            .order-list {
                gap: 2px;
                margin-top: 6px;
            }
            
            .order-item {
                gap: 4px;
            }
            
            .order-badge {
                width: 14px;
                height: 14px;
                font-size: 8px;
            }
            
            .device-session-list {
                gap: 2px;
                margin-top: 6px;
            }
            
            .device-session-item {
                gap: 4px;
            }
            
            .device-name {
                font-size: 9px;
            }
            
            .device-session-item input {
                width: 40px;
            }
            
            .threshold-inputs {
                gap: 4px;
                margin-top: 6px;
            }
            
            .threshold-input-group label {
                font-size: 9px;
            }
            
            .save-restart-btn {
                padding: 4px 12px;
                font-size: 8px;
                margin: 15px auto 0 auto;
                min-width: 50px;
            }
        }
        
        @media (max-width: 480px) {
            .balancing-settings-container {
                margin-top: 10px;
            }
            
            .settings-section h3 {
                font-size: 8px;
                margin: 4px 0 2px 0;
                padding-top: 8px;
                padding-bottom: 1px;
            }
            
            .form-group label {
                font-size: 8px;
                margin-bottom: 1px;
            }
            
            .balancing-settings-container input,
            .balancing-settings-container select {
                padding: 2px 3px;
                font-size: 8px;
            }
            
            .global-toggle-container {
                padding: 4px;
                margin-bottom: 1px;
            }
            
            .toggle-label {
                font-size: 8px;
            }
            
            .toggle-switch {
                width: 28px;
                height: 14px;
            }
            
            .toggle-slider {
                width: 10px;
                height: 10px;
            }
            
            .toggle-switch.active .toggle-slider {
                transform: translateX(14px);
            }
            
            .method-description {
                padding: 4px;
                margin: 2px 0 6px 0;
                font-size: 7px;
            }
            
            .order-list {
                gap: 2px;
                margin-top: 5px;
            }
            
            .order-item {
                gap: 3px;
            }
            
            .order-badge {
                width: 12px;
                height: 12px;
                font-size: 7px;
            }
            
            .device-session-list {
                gap: 2px;
                margin-top: 5px;
            }
            
            .device-session-item {
                gap: 3px;
            }
            
            .device-name {
                font-size: 8px;
            }
            
            .device-session-item input {
                width: 35px;
            }
            
            .threshold-inputs {
                gap: 3px;
                margin-top: 5px;
            }
            
            .threshold-input-group label {
                font-size: 8px;
            }
            
            .save-restart-btn {
                padding: 3px 10px;
                font-size: 7px;
                margin: 12px auto 0 auto;
                min-width: 45px;
            }
        }
    '''

def get_balancing_settings_javascript():
    """Return the Balancing Settings component JavaScript"""
    return '''
        let gpuDevices = [];
        let gpuDevicesMapping = {};
        let currentSettings = {};
        let gpuSelections = {};
        let isUpdating = false;
        
        function getMethodDescription(method) {
            if (method === 'preferred-order') {
                return 'Transcoding sessions start and "fill up" the GPUs in the specified order one after another. A GPU is considered "full" if any limits are reached.';
            } else {
                return 'Every new transcoding process starts on a different GPU. It will stop using a specific GPU if any limits are reached.';
            }
        }
        
        function loadBalancingSettings() {
            // Load both GPU devices and current balance settings
            Promise.all([
                fetch('/api/gpu-devices').then(r => r.json()),
                fetch('/api/balance-settings').then(r => r.json())
            ])
            .then(([devicesData, settingsData]) => {
                if (devicesData.status === 'success') {
                    gpuDevices = devicesData.devices;
                }
                
                if (settingsData.status === 'success') {
                    currentSettings = settingsData.settings;
                    gpuDevicesMapping = currentSettings.gpu_devices || {};
                }
                
                // Initialize selections
                gpuSelections = {};
                for (let i = 0; i < gpuDevices.length; i++) {
                    gpuSelections[i] = '';
                }
                
                initializeBalancingSettings();
            })
            .catch(error => {
                console.error('Error loading balancing settings:', error);
                showErrorMessage('Failed to load balancing settings');
            });
        }
        
        function initializeBalancingSettings() {
            const container = document.getElementById('balancing-settings-container');
            
            // Get current method from settings
            const currentMethod = currentSettings.method || 'preferred-order';
            
            // Get current threshold values
            const prefOrder = currentSettings.preferred_order || {};
            const splitSessions = currentSettings.split_sessions || {};
            
            // Get auto-balancing enabled state
            const systemSettings = currentSettings.system || {};
            const autoBalancingEnabled = systemSettings.auto_balancing_enabled !== false;
            
            // Get rate limiting settings
            const rateLimiting = currentSettings.rate_limiting || {};
            const rateLimitingEnabled = rateLimiting.enabled !== false;
            const minSwitchInterval = rateLimiting.min_switch_interval_seconds || 10;
            
            let html = `
                <div class="card-title">BALANCING SETTINGS</div>
                <div class="global-toggle-container">
                    <div class="toggle-label">Auto GPU Balancing</div>
                    <div class="toggle-switch ${autoBalancingEnabled ? 'active' : ''}" onclick="toggleAutoBalancing()">
                        <div class="toggle-slider"></div>
                    </div>
                </div>
                
                <div class="global-toggle-container">
                    <div class="toggle-label">Rate Limiting</div>
                    <div class="toggle-switch ${rateLimitingEnabled ? 'active' : ''}" onclick="toggleRateLimiting()">
                        <div class="toggle-slider"></div>
                    </div>
                </div>
                
                <div id="rate-limiting-settings" class="${rateLimitingEnabled ? '' : 'hidden'}">
                    <div class="threshold-inputs" style="margin-top: 8px; margin-bottom: 15px;">
                        <div class="threshold-input-group">
                            <label>Min switch interval (seconds)</label>
                            <input id="min-switch-interval" type="number" min="1" max="300" value="${minSwitchInterval}">
                        </div>
                    </div>
                </div>
                
                <div class="settings-grid">
                    <div class="settings-section">
                        <div class="form-group">
                            <select id="method-select" onchange="toggleMethodSettings()">
                                <option value="preferred-order" ${currentMethod === 'preferred-order' ? 'selected' : ''}>Preferred GPU order</option>
                                <option value="split-sessions" ${currentMethod === 'split-sessions' ? 'selected' : ''}>Split sessions</option>
                            </select>
                        </div>
                        
                        <div id="method-description" class="method-description">
                            ${getMethodDescription(currentMethod)}
                        </div>
                        
                        <h3>GPU Order Priority</h3>
                        <div class="order-list">
                            ${generateGPUOrderList()}
                        </div>
                        
                        <div id="preferred-order-settings" class="method-settings ${currentMethod !== 'preferred-order' ? 'hidden' : ''}">
                            <h3>Max Session Numbers</h3>
                            <div class="device-session-list">
                                ${generateDeviceSessionInputs('preferred')}
                            </div>
                            
                            <h3>Load Average Threshold</h3>
                            <div class="threshold-inputs">
                                <div class="threshold-input-group">
                                    <label>Percentage</label>
                                    <input id="preferred-threshold-percentage" type="number" min="20" max="95" value="${prefOrder.load_threshold_percentage || 80}">
                                </div>
                                <div class="threshold-input-group">
                                    <label>Sampling timeframe (s)</label>
                                    <input id="preferred-threshold-seconds" type="number" min="0" max="600" value="${prefOrder.load_threshold_seconds || 30}">
                                </div>
                            </div>
                        </div>
                        
                        <div id="split-sessions-settings" class="method-settings ${currentMethod !== 'split-sessions' ? 'hidden' : ''}">
                            <h3>Max Session Numbers</h3>
                            <div class="device-session-list">
                                ${generateDeviceSessionInputs('split')}
                            </div>
                            
                            <h3>Load Average Limits</h3>
                            <div class="threshold-inputs">
                                <div class="threshold-input-group">
                                    <label>Percentage</label>
                                    <input id="split-limit-percentage" type="number" min="20" max="95" value="${splitSessions.load_limit_percentage || 75}">
                                </div>
                                <div class="threshold-input-group">
                                    <label>Sampling timeframe (s)</label>
                                    <input id="split-limit-seconds" type="number" min="0" max="600" value="${splitSessions.load_limit_seconds || 60}">
                                </div>
                            </div>
                        </div>
                        
                        <button class="save-restart-btn" onclick="saveAndRestart()">
                            SAVE & RESTART
                        </button>
                    </div>
                </div>
            `;
            
            container.innerHTML = html;
            
            // Set initial method description
            const methodDescription = document.getElementById('method-description');
            if (methodDescription) {
                methodDescription.innerHTML = getMethodDescription(currentMethod);
            }
            
            populateAllDropdowns();
            loadCurrentPriorities();
        }
        
        function generateGPUOrderList() {
            let html = '';
            for (let i = 0; i < gpuDevices.length; i++) {
                html += `
                    <div class="order-item">
                        <div class="order-badge">${i + 1}</div>
                        <select id="gpu-order-${i}" onchange="handleDropdownChange(${i})">
                            <option value="">Select GPU...</option>
                        </select>
                    </div>
                `;
            }
            return html;
        }
        
        function generateDeviceSessionInputs(mode) {
            let html = '';
            const maxSessions = currentSettings.max_sessions || {};
            
            // Create reverse mapping from device_id to gpu key
            const deviceToGpuKey = {};
            Object.keys(gpuDevicesMapping).forEach(gpuKey => {
                const deviceId = gpuDevicesMapping[gpuKey];
                deviceToGpuKey[deviceId] = gpuKey;
            });
            
            gpuDevices.forEach((device, index) => {
                const deviceName = device.name || device.id || `Device ${index + 1}`;
                const gpuKey = deviceToGpuKey[device.id] || `gpu${index + 1}`;
                const sessionKey = `${gpuKey}_max_sessions`;
                const sessionValue = maxSessions[sessionKey] || 5;
                
                html += `
                    <div class="device-session-item">
                        <div class="device-name">${deviceName}</div>
                        <input id="sessions-${mode}-${index}" type="number" min="0" max="50" value="${sessionValue}">
                    </div>
                `;
            });
            return html;
        }
        
        function loadCurrentPriorities() {
            // Load priorities from the global gpu_priorities section
            const priorities = currentSettings.gpu_priorities || {};
            
            if (Object.keys(priorities).length === 0) {
                return;
            }
            
            // Create reverse mapping from gpu key to device_id
            const gpuToDeviceId = {};
            Object.keys(gpuDevicesMapping).forEach(gpuKey => {
                gpuToDeviceId[gpuKey] = gpuDevicesMapping[gpuKey];
            });
            
            // Load current priority selections
            Object.keys(priorities).forEach(priorityKey => {
                const gpuKey = priorities[priorityKey];
                if (gpuKey && gpuToDeviceId[gpuKey]) {
                    const deviceId = gpuToDeviceId[gpuKey];
                    const priorityIndex = parseInt(priorityKey.replace('priority_', '')) - 1;
                    
                    if (priorityIndex >= 0 && priorityIndex < gpuDevices.length) {
                        gpuSelections[priorityIndex] = deviceId;
                    }
                }
            });
            
            // Update dropdowns with loaded selections
            updateAllDropdowns();
        }
        
        function showErrorMessage(message) {
            console.error(message);
            // You could add a toast notification here if available
        }
        
        function showSuccessMessage(message) {
            console.log(message);
            // You could add a toast notification here if available
        }
        
        function handleDropdownChange(dropdownIndex) {
            if (isUpdating) return;
            
            const select = document.getElementById(`gpu-order-${dropdownIndex}`);
            if (select) {
                gpuSelections[dropdownIndex] = select.value;
                updateAllDropdowns();
            }
        }
        
        function populateAllDropdowns() {
            if (isUpdating) return;
            isUpdating = true;
            
            for (let i = 0; i < gpuDevices.length; i++) {
                const select = document.getElementById(`gpu-order-${i}`);
                if (!select) continue;
                
                const currentValue = gpuSelections[i] || '';
                
                select.innerHTML = '<option value="">Select GPU...</option>';
                
                gpuDevices.forEach(device => {
                    const option = document.createElement('option');
                    option.value = device.id; // Fixed: use device.id instead of device.device_id
                    option.textContent = device.name || device.id;
                    select.appendChild(option);
                });
                
                select.value = currentValue;
                gpuSelections[i] = currentValue;
            }
            
            updateAllDropdowns();
            isUpdating = false;
        }
        
        function updateAllDropdowns() {
            if (isUpdating) return;
            isUpdating = true;
            
            const selectedValues = Object.values(gpuSelections).filter(val => val !== '');
            
            for (let i = 0; i < gpuDevices.length; i++) {
                const select = document.getElementById(`gpu-order-${i}`);
                if (!select) continue;
                
                const currentSelection = gpuSelections[i] || '';
                
                Array.from(select.options).forEach(option => {
                    if (option.value === '') return;
                    
                    option.style.color = '#fff';
                    option.style.background = '#1a1a1a';
                    option.className = '';
                    
                    if (selectedValues.includes(option.value) && option.value !== currentSelection) {
                        option.style.color = '#999';
                        option.style.background = '#333';
                        option.className = 'selected';
                    }
                });
                
                if (select.value !== currentSelection) {
                    select.value = currentSelection;
                }
            }
            
            isUpdating = false;
        }
        
        function toggleAutoBalancing() {
            const toggleSwitch = document.querySelector('.toggle-switch');
            const isCurrentlyActive = toggleSwitch.classList.contains('active');
            
            if (isCurrentlyActive) {
                toggleSwitch.classList.remove('active');
            } else {
                toggleSwitch.classList.add('active');
            }
        }
        
        function toggleRateLimiting() {
            const toggleSwitches = document.querySelectorAll('.toggle-switch');
            const rateLimitingToggle = toggleSwitches[1]; // Second toggle is rate limiting
            const rateLimitingSettings = document.getElementById('rate-limiting-settings');
            
            const isCurrentlyActive = rateLimitingToggle.classList.contains('active');
            
            if (isCurrentlyActive) {
                rateLimitingToggle.classList.remove('active');
                rateLimitingSettings.classList.add('hidden');
            } else {
                rateLimitingToggle.classList.add('active');
                rateLimitingSettings.classList.remove('hidden');
            }
        }
        
        function toggleMethodSettings() {
            const methodSelect = document.getElementById('method-select');
            const preferredSettings = document.getElementById('preferred-order-settings');
            const splitSettings = document.getElementById('split-sessions-settings');
            const methodDescription = document.getElementById('method-description');
            
            if (methodSelect.value === 'preferred-order') {
                preferredSettings.classList.remove('hidden');
                splitSettings.classList.add('hidden');
            } else {
                preferredSettings.classList.add('hidden');
                splitSettings.classList.remove('hidden');
            }
            
            // Update method description
            if (methodDescription) {
                methodDescription.innerHTML = getMethodDescription(methodSelect.value);
            }
        }
        
        function saveAndRestart() {
            const saveButton = document.querySelector('.save-restart-btn');
            saveButton.disabled = true;
            saveButton.textContent = 'SAVING...';
            
            try {
                const settingsData = collectCurrentSettings();
                
                fetch('/api/balance-settings', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(settingsData)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        showSuccessMessage('Balance settings saved successfully!');
                        saveButton.textContent = 'SAVED!';
                        setTimeout(() => {
                            saveButton.textContent = 'SAVE & RESTART';
                            saveButton.disabled = false;
                        }, 2000);
                    } else {
                        throw new Error(data.message || 'Failed to save settings');
                    }
                })
                .catch(error => {
                    console.error('Error saving settings:', error);
                    showErrorMessage('Failed to save settings: ' + error.message);
                    saveButton.textContent = 'SAVE & RESTART';
                    saveButton.disabled = false;
                });
                
            } catch (error) {
                console.error('Error collecting settings:', error);
                showErrorMessage('Error collecting settings: ' + error.message);
                saveButton.textContent = 'SAVE & RESTART';
                saveButton.disabled = false;
            }
        }
        
        function collectCurrentSettings() {
            const method = document.getElementById('method-select').value;
            console.log('🔧 Collecting settings, method:', method);
            
            const settingsData = {
                method: method
            };
            
            // Always collect GPU priorities (applies to both methods)
            const priorities = {};
            
            console.log('🔧 GPU Devices:', gpuDevices);
            console.log('🔧 GPU Devices Mapping:', gpuDevicesMapping);
            
            // Collect GPU priorities by reading dropdown values directly
            for (let i = 0; i < gpuDevices.length; i++) {
                const select = document.getElementById(`gpu-order-${i}`);
                console.log(`🔧 Dropdown ${i}:`, select ? select.value : 'NOT FOUND');
                
                if (select) {
                    const selectedOption = select.options[select.selectedIndex];
                    const deviceId = selectedOption ? selectedOption.value : '';
                    console.log(`🔧 Selected option for ${i}:`, selectedOption, 'value:', deviceId);
                    
                    if (deviceId && deviceId !== '') {
                        console.log(`🔧 Device ID for priority ${i + 1}:`, deviceId);
                        
                        const gpuKey = findGpuKeyByDeviceId(deviceId);
                        console.log(`🔧 GPU Key for ${deviceId}:`, gpuKey);
                        
                        if (gpuKey) {
                            const priorityKey = `priority_${i + 1}`;
                            priorities[priorityKey] = gpuKey;
                            console.log(`🔧 Set ${priorityKey} = ${gpuKey}`);
                        }
                    }
                }
            }
            
            console.log('🔧 Final priorities:', priorities);
            
            // Collect method-specific settings
            if (method === 'preferred-order') {
                settingsData.preferred_order = {
                    load_threshold_percentage: parseInt(document.getElementById('preferred-threshold-percentage').value),
                    load_threshold_seconds: parseInt(document.getElementById('preferred-threshold-seconds').value),
                    priorities: priorities
                };
            } else {
                // Split sessions settings
                settingsData.split_sessions = {
                    load_limit_percentage: parseInt(document.getElementById('split-limit-percentage').value),
                    load_limit_seconds: parseInt(document.getElementById('split-limit-seconds').value),
                    priorities: priorities
                };
            }
            
            // Collect max sessions for all devices
            settingsData.max_sessions = {};
            const deviceToGpuKey = {};
            Object.keys(gpuDevicesMapping).forEach(gpuKey => {
                const deviceId = gpuDevicesMapping[gpuKey];
                deviceToGpuKey[deviceId] = gpuKey;
            });
            
            gpuDevices.forEach((device, index) => {
                const gpuKey = deviceToGpuKey[device.id] || `gpu${index + 1}`;
                const sessionKey = `${gpuKey}_max_sessions`;
                
                const inputId = method === 'preferred-order' ? 
                    `sessions-preferred-${index}` : 
                    `sessions-split-${index}`;
                    
                const input = document.getElementById(inputId);
                if (input) {
                    settingsData.max_sessions[sessionKey] = parseInt(input.value);
                }
            });
            
            // Collect rate limiting settings
            const toggleSwitches = document.querySelectorAll('.toggle-switch');
            const rateLimitingToggle = toggleSwitches[1]; // Second toggle is rate limiting
            const rateLimitingEnabled = rateLimitingToggle && rateLimitingToggle.classList.contains('active');
            const minSwitchIntervalInput = document.getElementById('min-switch-interval');
            
            settingsData.rate_limiting = {
                enabled: rateLimitingEnabled,
                min_switch_interval_seconds: minSwitchIntervalInput ? parseInt(minSwitchIntervalInput.value) : 10
            };
            
            // Collect system settings (auto-balancing toggle)
            const toggleSwitch = document.querySelector('.toggle-switch');
            const autoBalancingEnabled = toggleSwitch && toggleSwitch.classList.contains('active');
            settingsData.system = {
                auto_balancing_enabled: autoBalancingEnabled
            };
            
            console.log('🔧 Complete settings data:', settingsData);
            return settingsData;
        }
        
        function findGpuKeyByDeviceId(deviceId) {
            for (const gpuKey in gpuDevicesMapping) {
                if (gpuDevicesMapping[gpuKey] === deviceId) {
                    return gpuKey;
                }
            }
            return null;
        }
    '''

def get_balancing_settings_html():
    """Return the Balancing Settings component HTML structure"""
    return '''
        <div id="balancing-settings-container" class="status-card balancing-settings-container">
            <div class="loading"></div>
        </div>
    '''
