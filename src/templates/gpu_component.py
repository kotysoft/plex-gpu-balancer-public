#!/usr/bin/env python3
"""Main GPU component template"""

def get_gpu_styles():
    """Return the GPU-specific CSS styles"""
    return '''
        /* GPU Device Containers */
        .gpu-devices-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        /* Invisible parent container for each GPU */
        .gpu-device-container {
            display: flex;
            gap: 15px;
            align-items: flex-start;
        }
        
        .gpu-device-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 15px 15px 45px 15px;
            transition: all 0.3s ease;
            position: relative;
            flex: 1;
            min-width: 0;
        }
        
        /* Historical data container */
        .gpu-historical-container {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 8px;
            padding: 15px 12px 45px 12px;
            width: 280px;
            flex-shrink: 0;
            height: 100%;
            display: flex;
            flex-direction: column;
        }
        
        .gpu-historical-title {
            font-size: 12px;
            font-weight: 600;
            color: #fff;
            margin-bottom: 10px;
            text-align: center;
            flex-shrink: 0;
        }
        
        .historical-matrix {
            display: grid;
            grid-template-columns: 80px repeat(4, 1fr);
            gap: 2px;
            font-size: 9px;
            flex: 1;
        }
        
        .matrix-header {
            background: rgba(255, 255, 255, 0.1);
            padding: 4px 2px;
            text-align: center;
            font-weight: 600;
            color: #ccc;
            border-radius: 2px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .matrix-row-label {
            background: rgba(255, 255, 255, 0.08);
            padding: 4px 6px;
            font-weight: 500;
            color: #ddd;
            font-size: 8px;
            display: flex;
            align-items: center;
            justify-content: flex-end;
        }
        
        .matrix-cell {
            background: rgba(255, 255, 255, 0.05);
            padding: 4px 2px;
            text-align: center;
            color: #fff;
            font-weight: 500;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .matrix-cell.no-data {
            color: #666;
        }
        
        .matrix-cell.low { background: rgba(0, 255, 65, 0.15); }
        .matrix-cell.medium { background: rgba(255, 255, 0, 0.15); }
        .matrix-cell.high { background: rgba(255, 71, 87, 0.15); }
        
        .gpu-device-card.unknown-active {
            border-left: 3px solid #666666;
            background: linear-gradient(135deg, rgba(102, 102, 102, 0.08) 0%, rgba(255, 255, 255, 0.05) 100%);
        }
        
        .gpu-device-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 15px;
        }
        
        .gpu-device-name {
            font-size: 16px;
            font-weight: 600;
            color: #fff;
        }
        
        .gpu-switch-btn {
            background: #404040;
            color: #e0e0e0;
            border: 1px solid #606060;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .gpu-switch-btn:hover {
            background: #505050;
            border-color: #707070;
        }
        
        .gpu-switch-btn.active {
            background: #2a5934;
            color: #90c695;
            cursor: not-allowed;
            border-color: #4a7954;
        }
        
        .device-id {
            font-size: 9px;
            color: #666;
            font-family: monospace;
            margin-top: 15px;
            padding-top: 8px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            word-break: break-all;
            position: absolute;
            bottom: 15px;
            left: 15px;
            right: 15px;
        }
        
        /* Large GPU Load Bar */
        .large-gpu-bar {
            margin: 15px 0;
        }
        
        .large-bar-container {
            width: 100%;
            height: 24px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            overflow: hidden;
            position: relative;
        }
        
        .large-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ff41 0%, #ffff00 50%, #ff4757 100%);
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
            color: #000;
        }
        
        .large-bar-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 12px;
            font-weight: bold;
            color: #fff;
            z-index: 2;
        }
        
        /* Mobile Responsive Design for GPU Component */
        @media (max-width: 1024px) {
            .gpu-device-container {
                flex-direction: column;
                gap: 10px;
            }
            
            .gpu-device-card {
                width: 100%;
                max-width: none;
            }
            
            .gpu-historical-container {
                width: 100%;
                max-width: none;
                flex-shrink: 1;
                padding: 10px 8px 35px 8px;
            }
            
            .gpu-device-card {
                padding: 10px 10px 35px 10px;
            }
            
            .gpu-device-header {
                margin-bottom: 12px;
            }
            
            .gpu-device-name {
                font-size: 14px;
            }
            
            .gpu-switch-btn {
                padding: 5px 10px;
                font-size: 10px;
            }
            
            .large-gpu-bar {
                margin: 12px 0;
            }
            
            .large-bar-container {
                height: 20px;
            }
            
            .large-bar-text {
                font-size: 11px;
            }
            
            .device-id {
                font-size: 8px;
                bottom: 10px;
                left: 10px;
                right: 10px;
            }
            
            .gpu-historical-title {
                font-size: 11px;
                margin-bottom: 8px;
            }
            
            .historical-matrix {
                font-size: 8px;
                gap: 1px;
            }
            
            .matrix-header {
                padding: 3px 2px;
            }
            
            .matrix-row-label {
                padding: 3px 4px;
                font-size: 7px;
            }
            
            .matrix-cell {
                padding: 3px 2px;
            }
        }
        
        @media (max-width: 768px) {
            .gpu-devices-grid {
                gap: 10px;
            }
            
            .gpu-device-container {
                gap: 8px;
            }
            
            .gpu-historical-container {
                padding: 8px 6px 30px 6px;
            }
            
            .gpu-device-card {
                padding: 8px 8px 30px 8px;
            }
            
            .gpu-device-header {
                margin-bottom: 10px;
            }
            
            .gpu-device-name {
                font-size: 13px;
            }
            
            .gpu-switch-btn {
                padding: 4px 8px;
                font-size: 9px;
            }
            
            .large-gpu-bar {
                margin: 10px 0;
            }
            
            .large-bar-container {
                height: 18px;
            }
            
            .large-bar-text {
                font-size: 10px;
            }
            
            .device-id {
                font-size: 7px;
                bottom: 8px;
                left: 8px;
                right: 8px;
            }
            
            .gpu-historical-title {
                font-size: 10px;
                margin-bottom: 6px;
            }
            
            .historical-matrix {
                font-size: 7px;
                gap: 1px;
            }
            
            .matrix-header {
                padding: 2px 1px;
            }
            
            .matrix-row-label {
                padding: 2px 3px;
                font-size: 6px;
            }
            
            .matrix-cell {
                padding: 2px 1px;
            }
        }
        
        @media (max-width: 480px) {
            .gpu-devices-grid {
                gap: 8px;
            }
            
            .gpu-device-container {
                gap: 6px;
            }
            
            .gpu-historical-container {
                padding: 6px 4px 25px 4px;
            }
            
            .gpu-device-card {
                padding: 6px 6px 25px 6px;
            }
            
            .gpu-device-header {
                margin-bottom: 8px;
            }
            
            .gpu-device-name {
                font-size: 12px;
            }
            
            .gpu-switch-btn {
                padding: 3px 6px;
                font-size: 8px;
            }
            
            .large-gpu-bar {
                margin: 8px 0;
            }
            
            .large-bar-container {
                height: 16px;
            }
            
            .large-bar-text {
                font-size: 9px;
            }
            
            .device-id {
                font-size: 6px;
                bottom: 6px;
                left: 6px;
                right: 6px;
            }
            
            .gpu-historical-title {
                font-size: 9px;
                margin-bottom: 5px;
            }
            
            .historical-matrix {
                font-size: 6px;
                gap: 1px;
                grid-template-columns: 60px repeat(4, 1fr);
            }
            
            .matrix-header {
                padding: 2px 1px;
            }
            
            .matrix-row-label {
                padding: 2px 2px;
                font-size: 5px;
            }
            
            .matrix-cell {
                padding: 2px 1px;
            }
        }
    '''

def get_gpu_javascript():
    """Return the GPU component JavaScript"""
    return '''
        function loadGPUDevices() {
            Promise.all([
                fetchWithTimeout('/api/gpu-devices'),
                fetchWithTimeout('/api/all-gpu-metrics')
            ])
                .then(responses => Promise.all(responses.map(r => r.json())))
                .then(([devicesData, allMetricsData]) => {
                    // Connection restored if it was lost
                    if (connectionLost) {
                        hideConnectionLostModal();
                    }
                    
                    const container = document.getElementById('gpu-devices-container');
                    
                    if (devicesData.status !== 'success' || !devicesData.devices || devicesData.devices.length === 0) {
                        container.innerHTML = `
                            <div class="no-devices">
                                <div style="font-size: 24px; margin-bottom: 10px;">❌</div>
                                <div>No GPU devices found</div>
                            </div>
                        `;
                        return;
                    }
                    
                    let html = '';
                    
                    devicesData.devices.forEach(device => {
                        const isActive = device.id === devicesData.active_device;
                        
                        // Get device-specific metrics from the unified system
                        const deviceMetrics = allMetricsData.devices?.[device.id];
                        
                        // Wrap each GPU card in a container with historical data
                        html += '<div class="gpu-device-container">';
                        
                        // Use specific GPU component renderers based on device type
                        if (device.type === 'intel') {
                            html += renderIntelGPUCard(device, deviceMetrics, isActive);
                        } else if (device.type === 'nvidia') {
                            html += renderNvidiaGPUCard(device, deviceMetrics, isActive);
                        } else {
                            // Generic GPU card for unknown types
                            html += renderGenericGPUCard(device, deviceMetrics, isActive);
                        }
                        
                        // Add historical data container
                        html += renderHistoricalDataContainer(device.id, device.type);
                        html += '</div>';
                    });
                    
                    container.innerHTML = html;
                })
                .catch(error => {
                    handleAPIError(error, 'loadGPUDevices');
                    document.getElementById('gpu-devices-container').innerHTML = `
                        <div class="no-devices">
                            <div style="font-size: 24px; margin-bottom: 10px;">❌</div>
                            <div>Error loading GPU devices</div>
                        </div>
                    `;
                });
        }
        
        function renderGenericGPUCard(device, deviceMetrics, isActive) {
            const activeClass = isActive ? 'unknown-active' : '';
            
            let utilization = 0;
            let temperature = 0;
            let power = 0;
            let processCount = 0;
            
            if (deviceMetrics && deviceMetrics.status === 'success') {
                utilization = deviceMetrics.utilization_percent || 0;
                temperature = deviceMetrics.temperature_celsius || 0;
                power = deviceMetrics.power_watts || 0;
                processCount = deviceMetrics.process_count || 0;
            }
            
            let html = `
                <div class="gpu-device-card ${activeClass}" data-device-id="${device.id}">
                    <div class="gpu-device-header">
                        <div class="gpu-device-name">${device.name}</div>
                        <button class="gpu-switch-btn ${isActive ? 'active' : ''}" 
                                onclick="switchToDevice('${device.id}')"
                                ${isActive ? 'disabled' : ''}
                                title="Switch to ${device.name} (ID: ${device.id})">
                            ${isActive ? 'ACTIVE' : 'ACTIVATE'}
                        </button>
                    </div>
                    
                    <div class="large-gpu-bar">
                        <div class="large-bar-container">
                            <div class="large-bar-fill" style="width: ${utilization}%"></div>
                            <div class="large-bar-text">${utilization.toFixed(1)}%</div>
                        </div>
                    </div>
                    
                    <div class="info-row">
                        <span class="info-label">Temperature:</span>
                        <span class="info-value">${temperature.toFixed(1)}°C</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Power:</span>
                        <span class="info-value">${power.toFixed(1)}W</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Processes:</span>
                        <span class="info-value" style="color: ${processCount > 0 ? '#00ff41' : '#a0a0a0'};">${processCount}</span>
                    </div>
                    
                    <div class="device-id">Device ID: ${device.id}</div>
                </div>
            `;
            
            return html;
        }
        
        function refreshGPUMetrics() {
            // Refresh both metrics AND active device status to detect balancer changes
            Promise.all([
                fetchWithTimeout('/api/all-gpu-metrics'),
                fetchWithTimeout('/api/gpu-devices')
            ])
                .then(responses => Promise.all(responses.map(r => r.json())))
                .then(([allMetricsData, devicesData]) => {
                    // Connection restored if it was lost
                    if (connectionLost) {
                        hideConnectionLostModal();
                    }
                    
                    // Update metrics
                    updateGPUDevicesWithMetrics(allMetricsData);
                    
                    // Update active device status if it changed
                    if (devicesData.status === 'success') {
                        updateActiveDeviceStatus(devicesData.active_device);
                    }
                    
                    updateLastRefresh();
                })
                .catch(error => {
                    // Only show connection error for timeout/network issues
                    // Don't spam the modal for regular refresh errors during normal operation
                    if (error.name === 'AbortError' || error.message.includes('Failed to fetch')) {
                        handleAPIError(error, 'refreshGPUMetrics');
                    } else {
                        console.error('Error refreshing GPU metrics:', error);
                    }
                });
        }
        
        function updateGPUDevicesWithMetrics(allMetricsData) {
            // Update only the metrics in existing GPU device containers
            const container = document.getElementById('gpu-devices-container');
            const deviceCards = container.querySelectorAll('.gpu-device-card');
            
            deviceCards.forEach(card => {
                const deviceId = card.getAttribute('data-device-id');
                if (!deviceId) return;
                
                const deviceMetrics = allMetricsData.devices?.[deviceId];
                if (!deviceMetrics) return;
                
                // Use specific update functions based on device type
                if (deviceMetrics.device_type === 'intel') {
                    updateIntelGPUMetrics(card, deviceMetrics);
                } else if (deviceMetrics.device_type === 'nvidia') {
                    updateNvidiaGPUMetrics(card, deviceMetrics);
                } else {
                    updateGenericGPUMetrics(card, deviceMetrics);
                }
            });
            
            // Note: Historical data is updated separately by refreshHistoricalData()
        }
        
        function updateGenericGPUMetrics(card, deviceMetrics) {
            // Update utilization bar
            const barFill = card.querySelector('.large-bar-fill');
            const barText = card.querySelector('.large-bar-text');
            if (barFill && barText) {
                const utilization = deviceMetrics.utilization_percent || 0;
                barFill.style.width = utilization + '%';
                barText.textContent = utilization.toFixed(1) + '% Load';
            }
            
            // Update info values
            const updateInfoValue = (label, value, unit = '') => {
                const rows = card.querySelectorAll('.info-row');
                rows.forEach(row => {
                    const labelEl = row.querySelector('.info-label');
                    const valueEl = row.querySelector('.info-value');
                    if (labelEl && valueEl && labelEl.textContent === label + ':') {
                        valueEl.textContent = value + unit;
                    }
                });
            };
            
            updateInfoValue('Temperature', (deviceMetrics.temperature_celsius || 0).toFixed(1), '°C');
            updateInfoValue('Power', (deviceMetrics.power_watts || 0).toFixed(1), 'W');
            updateInfoValue('Processes', deviceMetrics.process_count || 0);
        }
        
        function updateActiveDeviceStatus(currentActiveDevice) {
            // Update all GPU cards to reflect the current active device
            const container = document.getElementById('gpu-devices-container');
            const deviceCards = container.querySelectorAll('.gpu-device-card');
            
            deviceCards.forEach(card => {
                const deviceId = card.getAttribute('data-device-id');
                if (!deviceId) return;
                
                const switchBtn = card.querySelector('.gpu-switch-btn');
                const isActive = deviceId === currentActiveDevice;
                
                // Update button state and text
                if (switchBtn) {
                    if (isActive) {
                        switchBtn.textContent = 'ACTIVE';
                        switchBtn.classList.add('active');
                        switchBtn.disabled = true;
                    } else {
                        switchBtn.textContent = 'ACTIVATE';
                        switchBtn.classList.remove('active');
                        switchBtn.disabled = false;
                    }
                }
                
                // Update card styling for Intel/NVIDIA active states
                // Remove all active classes first
                card.classList.remove('intel-active', 'nvidia-active', 'unknown-active');
                
                // Add appropriate active class
                if (isActive) {
                    // Determine device type from data or device ID
                    if (deviceId.includes('8086')) {
                        card.classList.add('intel-active');
                    } else if (deviceId.includes('10de')) {
                        card.classList.add('nvidia-active');
                    } else {
                        card.classList.add('unknown-active');
                    }
                }
            });
        }
        
        function renderHistoricalDataContainer(deviceId, deviceType) {
            const title = 'Load averages';
            
            let rows = '';
            if (deviceType === 'nvidia') {
                rows = `
                    <div class="matrix-row-label">Main Load %</div>
                    <div class="matrix-cell" data-metric="main_load" data-timeframe="10s">-</div>
                    <div class="matrix-cell" data-metric="main_load" data-timeframe="30s">-</div>
                    <div class="matrix-cell" data-metric="main_load" data-timeframe="1m">-</div>
                    <div class="matrix-cell" data-metric="main_load" data-timeframe="5m">-</div>
                    
                    <div class="matrix-row-label">GPU Util %</div>
                    <div class="matrix-cell" data-metric="gpu_util" data-timeframe="10s">-</div>
                    <div class="matrix-cell" data-metric="gpu_util" data-timeframe="30s">-</div>
                    <div class="matrix-cell" data-metric="gpu_util" data-timeframe="1m">-</div>
                    <div class="matrix-cell" data-metric="gpu_util" data-timeframe="5m">-</div>
                    
                    <div class="matrix-row-label">Memory %</div>
                    <div class="matrix-cell" data-metric="memory_util" data-timeframe="10s">-</div>
                    <div class="matrix-cell" data-metric="memory_util" data-timeframe="30s">-</div>
                    <div class="matrix-cell" data-metric="memory_util" data-timeframe="1m">-</div>
                    <div class="matrix-cell" data-metric="memory_util" data-timeframe="5m">-</div>
                    
                    <div class="matrix-row-label">Encoder %</div>
                    <div class="matrix-cell" data-metric="encoder_util" data-timeframe="10s">-</div>
                    <div class="matrix-cell" data-metric="encoder_util" data-timeframe="30s">-</div>
                    <div class="matrix-cell" data-metric="encoder_util" data-timeframe="1m">-</div>
                    <div class="matrix-cell" data-metric="encoder_util" data-timeframe="5m">-</div>
                    
                    <div class="matrix-row-label">Decoder %</div>
                    <div class="matrix-cell" data-metric="decoder_util" data-timeframe="10s">-</div>
                    <div class="matrix-cell" data-metric="decoder_util" data-timeframe="30s">-</div>
                    <div class="matrix-cell" data-metric="decoder_util" data-timeframe="1m">-</div>
                    <div class="matrix-cell" data-metric="decoder_util" data-timeframe="5m">-</div>
                    
                    <div class="matrix-row-label">Highest %</div>
                    <div class="matrix-cell" data-metric="highest" data-timeframe="10s">-</div>
                    <div class="matrix-cell" data-metric="highest" data-timeframe="30s">-</div>
                    <div class="matrix-cell" data-metric="highest" data-timeframe="1m">-</div>
                    <div class="matrix-cell" data-metric="highest" data-timeframe="5m">-</div>
                `;
            } else if (deviceType === 'intel') {
                rows = `
                    <div class="matrix-row-label">Main Load %</div>
                    <div class="matrix-cell" data-metric="main_load" data-timeframe="10s">-</div>
                    <div class="matrix-cell" data-metric="main_load" data-timeframe="30s">-</div>
                    <div class="matrix-cell" data-metric="main_load" data-timeframe="1m">-</div>
                    <div class="matrix-cell" data-metric="main_load" data-timeframe="5m">-</div>
                    
                    <div class="matrix-row-label">Render/3D %</div>
                    <div class="matrix-cell" data-metric="render_util" data-timeframe="10s">-</div>
                    <div class="matrix-cell" data-metric="render_util" data-timeframe="30s">-</div>
                    <div class="matrix-cell" data-metric="render_util" data-timeframe="1m">-</div>
                    <div class="matrix-cell" data-metric="render_util" data-timeframe="5m">-</div>
                    
                    <div class="matrix-row-label">Video %</div>
                    <div class="matrix-cell" data-metric="video_util" data-timeframe="10s">-</div>
                    <div class="matrix-cell" data-metric="video_util" data-timeframe="30s">-</div>
                    <div class="matrix-cell" data-metric="video_util" data-timeframe="1m">-</div>
                    <div class="matrix-cell" data-metric="video_util" data-timeframe="5m">-</div>
                    
                    <div class="matrix-row-label">VideoEnh %</div>
                    <div class="matrix-cell" data-metric="video_enhance_util" data-timeframe="10s">-</div>
                    <div class="matrix-cell" data-metric="video_enhance_util" data-timeframe="30s">-</div>
                    <div class="matrix-cell" data-metric="video_enhance_util" data-timeframe="1m">-</div>
                    <div class="matrix-cell" data-metric="video_enhance_util" data-timeframe="5m">-</div>
                    
                    <div class="matrix-row-label">Highest %</div>
                    <div class="matrix-cell" data-metric="highest" data-timeframe="10s">-</div>
                    <div class="matrix-cell" data-metric="highest" data-timeframe="30s">-</div>
                    <div class="matrix-cell" data-metric="highest" data-timeframe="1m">-</div>
                    <div class="matrix-cell" data-metric="highest" data-timeframe="5m">-</div>
                `;
            }
            
            return `
                <div class="gpu-historical-container" data-device-id="${deviceId}">
                    <div class="gpu-historical-title">${title}</div>
                    <div class="historical-matrix">
                        <div class="matrix-header"></div>
                        <div class="matrix-header">10s</div>
                        <div class="matrix-header">30s</div>
                        <div class="matrix-header">1m</div>
                        <div class="matrix-header">5m</div>
                        ${rows}
                    </div>
                </div>
            `;
        }
        
        function refreshHistoricalData() {
            // Use the same host as the dashboard but port 8081 for historical data
            const collectorUrl = `http://${window.location.hostname}:8081/api/historical-data`;
            
            fetch(collectorUrl)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}`);
                    }
                    return response.json();
                })
                .then(historicalData => {
                    updateHistoricalDataContainers(historicalData);
                })
                .catch(error => {
                    // Silently handle historical data errors since it's not critical
                    // and data might not be available yet after startup
                    console.log('Historical data not available yet:', error.message);
                });
        }
        
        function updateHistoricalDataContainers(historicalData) {
            const containers = document.querySelectorAll('.gpu-historical-container');
            
            containers.forEach(container => {
                const deviceId = container.getAttribute('data-device-id');
                if (!deviceId || !historicalData[deviceId]) return;
                
                const deviceHistoricalData = historicalData[deviceId];
                
                // Update each matrix cell
                const cells = container.querySelectorAll('.matrix-cell');
                cells.forEach(cell => {
                    const metric = cell.getAttribute('data-metric');
                    const timeframe = cell.getAttribute('data-timeframe');
                    
                    if (!metric || !timeframe) return;
                    
                    const timeframeData = deviceHistoricalData[timeframe];
                    if (!timeframeData || timeframeData[metric] === undefined) {
                        cell.textContent = '-';
                        cell.className = 'matrix-cell no-data';
                        return;
                    }
                    
                    const value = timeframeData[metric];
                    cell.textContent = value.toFixed(1);
                    
                    // Apply color coding based on value
                    cell.className = 'matrix-cell';
                    if (value < 30) {
                        cell.classList.add('low');
                    } else if (value < 70) {
                        cell.classList.add('medium');
                    } else {
                        cell.classList.add('high');
                    }
                });
            });
        }
    '''

def get_gpu_html():
    """Return the GPU component HTML structure"""
    return '''
        <div id="gpu-devices-container" class="gpu-devices-grid">
            <div class="no-devices">
                <div class="loading"></div>
                <div style="margin-top: 10px;">Loading GPU devices...</div>
            </div>
        </div>
    '''
