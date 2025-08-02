#!/usr/bin/env python3
"""NVIDIA GPU component template"""

def get_nvidia_gpu_styles():
    """Return NVIDIA GPU-specific CSS styles"""
    return '''
        .gpu-device-card.nvidia-active {
            border-left: 3px solid #76b900;
            background: linear-gradient(135deg, rgba(118, 185, 0, 0.08) 0%, rgba(255, 255, 255, 0.05) 100%);
        }
        
        /* Memory Usage Bar */
        .memory-usage-bar {
            margin-top: 10px;
            margin-bottom: 10px;
        }
        
        .memory-bar-container {
            width: 100%;
            height: 16px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            overflow: hidden;
            position: relative;
        }
        
        .memory-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #76b900 0%, #a0c334 100%);
            transition: width 0.3s ease;
        }
        
        .memory-bar-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 10px;
            font-weight: bold;
            color: #fff;
            z-index: 2;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
        }
        
        .memory-bar-text-left {
            position: absolute;
            top: 50%;
            left: 8px;
            transform: translateY(-50%);
            font-size: 10px;
            font-weight: normal;
            color: #fff;
            z-index: 2;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
        }
        
        .memory-bar-text-right {
            position: absolute;
            top: 50%;
            right: 8px;
            transform: translateY(-50%);
            font-size: 10px;
            font-weight: normal;
            color: #fff;
            z-index: 2;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
        }
        
        /* Utilization Breakdown Bars */
        .nvidia-utilization-breakdown {
            margin-top: 12px;
        }
        
        .nvidia-breakdown-row {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr 1fr;
            gap: 6px;
            margin-bottom: 6px;
        }
        
        .nvidia-util-item {
            text-align: center;
        }
        
        .nvidia-util-label {
            font-size: 9px;
            color: #a0a0a0;
            margin-bottom: 3px;
        }
        
        .nvidia-util-bar {
            width: 100%;
            height: 12px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
            overflow: hidden;
            position: relative;
        }
        
        .nvidia-util-bar-fill {
            height: 100%;
            transition: width 0.3s ease;
        }
        
        .nvidia-util-bar-fill.gpu { background: #76b900; }
        .nvidia-util-bar-fill.memory { background: #00ff41; }
        .nvidia-util-bar-fill.encoder { background: #ffff00; }
        .nvidia-util-bar-fill.decoder { background: #ff8c00; }
        
        .nvidia-util-value {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 8px;
            font-weight: bold;
            color: #fff;
            z-index: 2;
            text-shadow: 1px 1px 1px rgba(0, 0, 0, 0.8);
        }
    '''

def get_nvidia_gpu_javascript():
    """Return NVIDIA GPU-specific JavaScript"""
    return '''
        function renderNvidiaGPUCard(device, deviceMetrics, isActive) {
            const activeClass = isActive ? 'nvidia-active' : '';
            
            let utilization = 0;
            let temperature = 0;
            let power = 0;
            let processCount = 0;
            let memoryUsedPercent = 0;
            let memoryFreeMB = 0;
            let memoryUtilization = 0;
            let encoderUtilization = 0;
            let decoderUtilization = 0;
            
            if (deviceMetrics && deviceMetrics.status === 'success') {
                utilization = deviceMetrics.utilization_percent || 0;
                temperature = deviceMetrics.temperature_celsius || 0;
                power = deviceMetrics.power_watts || 0;
                processCount = deviceMetrics.process_count || 0;
                memoryUsedPercent = deviceMetrics.memory_used_percent || 0;
                memoryFreeMB = deviceMetrics.memory_free_mb || 0;
                memoryUtilization = deviceMetrics.memory_utilization_percent || 0;
                encoderUtilization = deviceMetrics.vendor_specific?.encoder_utilization_percent || 0;
                decoderUtilization = deviceMetrics.vendor_specific?.decoder_utilization_percent || 0;
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
                    
                    <div class="memory-usage-bar">
                        <div class="memory-bar-container">
                            <div class="memory-bar-fill" style="width: ${memoryUsedPercent}%"></div>
                            <div class="memory-bar-text">VRAM</div>
                            <div class="memory-bar-text-left">${memoryUsedPercent > 0 && memoryUsedPercent < 100 ? Math.round((memoryFreeMB / (1 - memoryUsedPercent/100)) - memoryFreeMB) : 0} MByte used</div>
                            <div class="memory-bar-text-right">${memoryUsedPercent > 0 && memoryUsedPercent < 100 ? Math.round(memoryFreeMB / (1 - memoryUsedPercent/100)) : memoryFreeMB} MByte total</div>
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
                    
                    <div class="nvidia-utilization-breakdown">
                        <div class="nvidia-breakdown-row">
                            <div class="nvidia-util-item">
                                <div class="nvidia-util-label">GPU</div>
                                <div class="nvidia-util-bar">
                                    <div class="nvidia-util-bar-fill gpu" style="width: ${utilization}%"></div>
                                    <div class="nvidia-util-value">${utilization.toFixed(0)}%</div>
                                </div>
                            </div>
                            <div class="nvidia-util-item">
                                <div class="nvidia-util-label">MEMORY</div>
                                <div class="nvidia-util-bar">
                                    <div class="nvidia-util-bar-fill memory" style="width: ${memoryUtilization}%"></div>
                                    <div class="nvidia-util-value">${memoryUtilization.toFixed(0)}%</div>
                                </div>
                            </div>
                            <div class="nvidia-util-item">
                                <div class="nvidia-util-label">ENCODER</div>
                                <div class="nvidia-util-bar">
                                    <div class="nvidia-util-bar-fill encoder" style="width: ${encoderUtilization}%"></div>
                                    <div class="nvidia-util-value">${encoderUtilization.toFixed(0)}%</div>
                                </div>
                            </div>
                            <div class="nvidia-util-item">
                                <div class="nvidia-util-label">DECODER</div>
                                <div class="nvidia-util-bar">
                                    <div class="nvidia-util-bar-fill decoder" style="width: ${decoderUtilization}%"></div>
                                    <div class="nvidia-util-value">${decoderUtilization.toFixed(0)}%</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="device-id">Device ID: ${device.id}</div>
                </div>
            `;
            
            return html;
        }
        
        function updateNvidiaGPUMetrics(card, deviceMetrics) {
            // Update utilization bar
            const barFill = card.querySelector('.large-bar-fill');
            const barText = card.querySelector('.large-bar-text');
            if (barFill && barText) {
                const utilization = deviceMetrics.utilization_percent || 0;
                barFill.style.width = utilization + '%';
                barText.textContent = utilization.toFixed(1) + '%';
            }
            
            // Update memory bar
            const memoryBarFill = card.querySelector('.memory-bar-fill');
            const memoryBarTextLeft = card.querySelector('.memory-bar-text-left');
            const memoryBarTextRight = card.querySelector('.memory-bar-text-right');
            if (memoryBarFill && memoryBarTextLeft && memoryBarTextRight) {
                const memoryUsedPercent = deviceMetrics.memory_used_percent || 0;
                const memoryFreeMB = deviceMetrics.memory_free_mb || 0;
                const memoryTotalMB = memoryUsedPercent > 0 && memoryUsedPercent < 100 ? 
                    Math.round(memoryFreeMB / (1 - memoryUsedPercent/100)) : 
                    Math.round(memoryFreeMB);
                const memoryUsedMB = memoryUsedPercent > 0 && memoryUsedPercent < 100 ? 
                    Math.round(memoryTotalMB - memoryFreeMB) : 0;
                memoryBarFill.style.width = memoryUsedPercent + '%';
                memoryBarTextLeft.textContent = `${memoryUsedMB} MByte used`;
                memoryBarTextRight.textContent = `${memoryTotalMB} MByte total`;
            }
            
            // Update utilization breakdown bars
            const updateUtilBar = (className, percent) => {
                const utilBar = card.querySelector('.nvidia-util-bar-fill.' + className);
                const utilValue = utilBar?.parentElement.querySelector('.nvidia-util-value');
                if (utilBar && utilValue) {
                    utilBar.style.width = percent + '%';
                    utilValue.textContent = percent.toFixed(0) + '%';
                }
            };
            
            updateUtilBar('gpu', deviceMetrics.utilization_percent || 0);
            updateUtilBar('memory', deviceMetrics.memory_utilization_percent || 0);
            updateUtilBar('encoder', deviceMetrics.vendor_specific?.encoder_utilization_percent || 0);
            updateUtilBar('decoder', deviceMetrics.vendor_specific?.decoder_utilization_percent || 0);
            
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
        }
    '''
