#!/usr/bin/env python3
"""Intel GPU component template"""

def get_intel_gpu_styles():
    """Return Intel GPU-specific CSS styles"""
    return '''
        .gpu-device-card.intel-active {
            border-left: 3px solid #0071c5;
            background: linear-gradient(135deg, rgba(0, 113, 197, 0.08) 0%, rgba(255, 255, 255, 0.05) 100%);
        }
        
        /* Engine Breakdown Bars */
        .engine-breakdown {
            margin-top: 15px;
        }
        
        .breakdown-row {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 10px;
            margin-top: 8px;
        }
        
        .engine-item {
            text-align: center;
        }
        
        .engine-label {
            font-size: 10px;
            color: #a0a0a0;
            margin-bottom: 4px;
        }
        
        .engine-bar {
            width: 100%;
            height: 14px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
            overflow: hidden;
            position: relative;
        }
        
        .engine-bar-fill {
            height: 100%;
            transition: width 0.3s ease;
        }
        
        .engine-bar-fill.render { background: #0071c5; }
        .engine-bar-fill.video { background: #00ff41; }
        .engine-bar-fill.video-enhance { background: #ffff00; }
        
        .engine-value {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 9px;
            font-weight: bold;
            color: #fff;
            z-index: 2;
        }
    '''

def get_intel_gpu_javascript():
    """Return Intel GPU-specific JavaScript"""
    return '''
        function renderIntelGPUCard(device, deviceMetrics, isActive) {
            const activeClass = isActive ? 'intel-active' : '';
            
            let utilization = 0;
            let power = 0;
            let processCount = 0;
            let showEngineBreakdown = false;
            let engineData = null;
            let frequency = 0;
            
            if (deviceMetrics && deviceMetrics.status === 'success') {
                utilization = deviceMetrics.utilization_percent || 0;
                power = deviceMetrics.power_watts || 0;
                processCount = deviceMetrics.process_count || 0;
                
                // Intel-specific frequency
                if (deviceMetrics.vendor_specific?.frequency_mhz) {
                    frequency = deviceMetrics.vendor_specific.frequency_mhz;
                }
                
                // Intel engine breakdown
                if (deviceMetrics.vendor_specific?.engines) {
                    showEngineBreakdown = true;
                    engineData = deviceMetrics.vendor_specific.engines;
                }
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
            `;
            
            // Intel-specific frequency display
            if (frequency > 0) {
                html += `
                    <div class="info-row">
                        <span class="info-label">Frequency:</span>
                        <span class="info-value">${frequency.toFixed(0)} MHz</span>
                    </div>
                `;
            }
            
            html += `
                <div class="info-row">
                    <span class="info-label">Power:</span>
                    <span class="info-value">${power.toFixed(1)}W</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Processes:</span>
                    <span class="info-value" style="color: ${processCount > 0 ? '#00ff41' : '#a0a0a0'};">${processCount}</span>
                </div>
            `;
            
            // Intel engine breakdown
            if (showEngineBreakdown && engineData) {
                html += `
                    <div class="engine-breakdown">
                        <div class="breakdown-row">
                            <div class="engine-item">
                                <div class="engine-label">Render/3D</div>
                                <div class="engine-bar">
                                    <div class="engine-bar-fill render" style="width: ${engineData.render_3d_percent || 0}%"></div>
                                    <div class="engine-value">${(engineData.render_3d_percent || 0).toFixed(1)}%</div>
                                </div>
                            </div>
                            <div class="engine-item">
                                <div class="engine-label">Video</div>
                                <div class="engine-bar">
                                    <div class="engine-bar-fill video" style="width: ${engineData.video_percent || 0}%"></div>
                                    <div class="engine-value">${(engineData.video_percent || 0).toFixed(1)}%</div>
                                </div>
                            </div>
                            <div class="engine-item">
                                <div class="engine-label">VideoEnhance</div>
                                <div class="engine-bar">
                                    <div class="engine-bar-fill video-enhance" style="width: ${engineData.video_enhance_percent || 0}%"></div>
                                    <div class="engine-value">${(engineData.video_enhance_percent || 0).toFixed(1)}%</div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }
            
            html += `
                <div class="device-id">Device ID: ${device.id}</div>
                </div>
            `;
            
            return html;
        }
        
        function updateIntelGPUMetrics(card, deviceMetrics) {
            // Update utilization bar
            const barFill = card.querySelector('.large-bar-fill');
            const barText = card.querySelector('.large-bar-text');
            if (barFill && barText) {
                const utilization = deviceMetrics.utilization_percent || 0;
                barFill.style.width = utilization + '%';
                barText.textContent = utilization.toFixed(1) + '%';
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
            
            // Update frequency
            if (deviceMetrics.vendor_specific?.frequency_mhz) {
                updateInfoValue('Frequency', deviceMetrics.vendor_specific.frequency_mhz.toFixed(0), ' MHz');
            }
            
            updateInfoValue('Power', (deviceMetrics.power_watts || 0).toFixed(1), 'W');
            
            // Update process count with color
            const processCount = deviceMetrics.process_count || 0;
            const rows = card.querySelectorAll('.info-row');
            rows.forEach(row => {
                const labelEl = row.querySelector('.info-label');
                const valueEl = row.querySelector('.info-value');
                if (labelEl && valueEl && labelEl.textContent === 'Processes:') {
                    valueEl.textContent = processCount;
                    valueEl.style.color = processCount > 0 ? '#00ff41' : '#a0a0a0';
                }
            });
            
            // Update Intel engine bars
            if (deviceMetrics.vendor_specific?.engines) {
                const engines = deviceMetrics.vendor_specific.engines;
                
                const updateEngineBar = (className, percent) => {
                    const engineBar = card.querySelector('.engine-bar-fill.' + className);
                    const engineValue = engineBar?.parentElement.querySelector('.engine-value');
                    if (engineBar && engineValue) {
                        engineBar.style.width = percent + '%';
                        engineValue.textContent = percent.toFixed(1) + '%';
                    }
                };
                
                updateEngineBar('render', engines.render_3d_percent || 0);
                updateEngineBar('video', engines.video_percent || 0);
                updateEngineBar('video-enhance', engines.video_enhance_percent || 0);
            }
        }
    '''
