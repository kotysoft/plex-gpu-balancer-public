#!/usr/bin/env python3
"""Plex component template"""

def get_plex_styles():
    """Return the Plex-specific CSS styles"""
    return '''
        /* Plex Server Status */
        .plex-container {
            background: linear-gradient(135deg, rgba(255, 140, 0, 0.03) 0%, rgba(255, 255, 255, 0.05) 100%);
            border-left: 3px solid #FF8C00;
            box-shadow: 0 0 15px rgba(255, 140, 0, 0.2);
        }
        
        .plex-status-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .plex-status-icon {
            font-size: 32px;
        }
        
        .plex-status-info h2 {
            font-size: 18px;
            margin: 0;
            color: #fff;
        }
        
        .plex-status-info .subtitle {
            font-size: 12px;
            color: #a0a0a0;
            margin-top: 2px;
        }
        
        .plex-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
        }
        
        .plex-section h3 {
            font-size: 14px;
            color: #fff;
            margin-bottom: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding-bottom: 5px;
        }
        
        .sessions-list {
            display: flex;
            flex-direction: column;
            gap: 4px;
            max-height: 150px;
            overflow-y: auto;
        }
        
        .session-item {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 3px;
            padding: 6px 8px;
            font-size: 11px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .session-info {
            flex: 0 0 40%;
            min-width: 0;
        }
        
        .session-device {
            flex: 0 0 40%;
            min-width: 0;
            text-align: center;
        }
        
        .session-indicators {
            flex: 0 0 15%;
            display: flex;
            gap: 2px;
            justify-content: right;
            align-items: center;
        }
        
        .session-user {
            font-weight: bold;
            color: #fff;
            font-size: 11px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .session-title {
            color: #a0a0a0;
            font-size: 10px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-top: 1px;
        }
        
        .session-device-name {
            color: #ccc;
            font-size: 10px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .transcode-icon {
            font-size: 14px;
            opacity: 0.3;
            color: #666;
        }
        
        .transcode-icon.video-transcoding {
            color: #ff6b6b;
            opacity: 1;
        }
        
        .transcode-icon.audio-transcoding {
            color: #ffa726;
            opacity: 1;
        }
        
        .no-sessions {
            color: #666;
            font-style: italic;
            text-align: center;
            padding: 15px;
            font-size: 11px;
        }
        
        /* Mobile Responsive Design for Plex Component */
        @media (max-width: 1024px) {
            .plex-status-header {
                gap: 10px;
                margin-bottom: 15px;
            }
            
            .plex-status-icon {
                font-size: 24px;
            }
            
            .plex-status-info h2 {
                font-size: 16px;
            }
            
            .plex-status-info .subtitle {
                font-size: 11px;
            }
            
            .plex-grid {
                gap: 15px;
            }
            
            .plex-section h3 {
                font-size: 13px;
                margin-bottom: 8px;
                padding-bottom: 4px;
            }
            
            .sessions-list {
                gap: 3px;
                max-height: 120px;
            }
            
            .session-item {
                padding: 5px 6px;
                font-size: 10px;
            }
            
            .session-user {
                font-size: 10px;
            }
            
            .session-title {
                font-size: 9px;
            }
            
            .session-device-name {
                font-size: 9px;
            }
            
            .transcode-icon {
                font-size: 12px;
            }
            
            .no-sessions {
                padding: 10px;
                font-size: 10px;
            }
        }
        
        @media (max-width: 768px) {
            .plex-status-header {
                gap: 8px;
                margin-bottom: 12px;
            }
            
            .plex-status-icon {
                font-size: 20px;
            }
            
            .plex-status-info h2 {
                font-size: 14px;
            }
            
            .plex-status-info .subtitle {
                font-size: 10px;
            }
            
            .plex-grid {
                gap: 10px;
            }
            
            .plex-section h3 {
                font-size: 12px;
                margin-bottom: 6px;
                padding-bottom: 3px;
            }
            
            .sessions-list {
                gap: 2px;
                max-height: 100px;
            }
            
            .session-item {
                padding: 4px 5px;
                font-size: 9px;
                gap: 6px;
            }
            
            .session-user {
                font-size: 9px;
            }
            
            .session-title {
                font-size: 8px;
            }
            
            .session-device-name {
                font-size: 8px;
            }
            
            .transcode-icon {
                font-size: 11px;
            }
            
            .no-sessions {
                padding: 8px;
                font-size: 9px;
            }
        }
        
        @media (max-width: 480px) {
            .plex-status-header {
                gap: 6px;
                margin-bottom: 10px;
            }
            
            .plex-status-icon {
                font-size: 18px;
            }
            
            .plex-status-info h2 {
                font-size: 13px;
            }
            
            .plex-status-info .subtitle {
                font-size: 9px;
            }
            
            .plex-grid {
                gap: 8px;
            }
            
            .plex-section h3 {
                font-size: 11px;
                margin-bottom: 5px;
                padding-bottom: 2px;
            }
            
            .sessions-list {
                gap: 1px;
                max-height: 80px;
            }
            
            .session-item {
                padding: 3px 4px;
                font-size: 8px;
                gap: 4px;
            }
            
            .session-user {
                font-size: 8px;
            }
            
            .session-title {
                font-size: 7px;
            }
            
            .session-device-name {
                font-size: 7px;
            }
            
            .transcode-icon {
                font-size: 10px;
            }
            
            .no-sessions {
                padding: 6px;
                font-size: 8px;
            }
        }
    '''

def get_plex_javascript():
    """Return the Plex component JavaScript"""
    return '''
        function loadPlexContainer() {
            Promise.all([
                fetchWithTimeout('/api/status'),
                fetchWithTimeout('/api/plex-settings'),
                fetchWithTimeout('/api/plex-sessions')
            ])
                .then(responses => Promise.all(responses.map(r => r.json())))
                .then(([statusData, settingsData, sessionsData]) => {
                    // Connection restored if it was lost
                    if (connectionLost) {
                        hideConnectionLostModal();
                    }
                    
                    const plex = statusData.plex;
                    const statusColor = plex.status === 'online' ? '#00ff41' : '#ff4757';
                    
                    // Use friendly name as Plex container title
                    const plexTitle = (settingsData.status === 'success' && settingsData.friendly_name) ? 
                        settingsData.friendly_name : 'Plex Media Server';
                    
                    let html = `
                        <div class="card-title">${plexTitle}</div>
                        <div class="plex-grid">
                    `;
                    
                    // Add Active Sessions section (above server status)
                    if (sessionsData.status === 'success') {
                        html += `
                            <div class="plex-section">
                                <h3>Active Sessions (${sessionsData.count})</h3>
                                <div id="sessions-container">
                        `;
                        
                        if (sessionsData.sessions && sessionsData.sessions.length > 0) {
                            html += '<div class="sessions-list">';
                            sessionsData.sessions.forEach(session => {
                                const videoIconClass = session.video_transcoding ? 'video-transcoding' : '';
                                const audioIconClass = session.audio_transcoding ? 'audio-transcoding' : '';
                                
                                html += `
                                    <div class="session-item">
                                        <div class="session-info">
                                            <div class="session-user">${session.user}</div>
                                            <div class="session-title">${session.title}</div>
                                        </div>
                                        <div class="session-device">
                                            <div class="session-device-name">${session.device}</div>
                                        </div>
                                        <div class="session-indicators">
                                            <span class="transcode-icon ${videoIconClass}" title="Video ${session.video_transcoding ? 'Transcoding' : 'Direct Play'}">🎬</span>
                                            <span class="transcode-icon ${audioIconClass}" title="Audio ${session.audio_transcoding ? 'Transcoding' : 'Direct Play'}">🔊</span>
                                        </div>
                                    </div>
                                `;
                            });
                            html += '</div>';
                        } else {
                            html += '<div class="no-sessions">No active sessions</div>';
                        }
                        
                        html += `
                                </div>
                            </div>
                        `;
                    }
                    
                    // Add Server Status section
                    html += `
                            <div class="plex-section">
                                <h3>Server Status</h3>
                                <div class="info-row">
                                    <span class="info-label">Status:</span>
                                    <span class="info-value" id="plex-status" style="color: ${statusColor};">${plex.status.toUpperCase()}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">Transcoding Sessions:</span>
                                    <span class="info-value" id="plex-sessions" style="color: ${plex.sessions > 0 ? '#00ff41' : '#a0a0a0'};">${plex.sessions}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">Server Name:</span>
                                    <span class="info-value">${plex.server_name || 'Unknown Server'}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">Server Address:</span>
                                    <span class="info-value" style="">${statusData.plex_server || 'Loading...'}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">Version:</span>
                                    <span class="info-value">${plex.version || 'Unknown'}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">Platform:</span>
                                    <span class="info-value">${plex.platform || 'Unknown'}</span>
                                </div>
                            </div>
                    `;
                    
                    if (settingsData.status === 'success') {
                        html += `
                            <div class="plex-section">
                                <h3>Transcoding Settings</h3>
                                <div class="info-row">
                                    <span class="info-label">Throttle Buffer:</span>
                                    <span class="info-value">${settingsData.transcoder_throttle_buffer}s</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">H264 Preset:</span>
                                    <span class="info-value">${settingsData.transcoder_h264_preset}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">H264 BG Preset:</span>
                                    <span class="info-value">${settingsData.transcoder_h264_background_preset}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">Transcode Limit:</span>
                                    <span class="info-value" style="color: ${settingsData.transcode_count_limit === 'Unlimited' ? '#ffff00' : '#ffffff'};">${settingsData.transcode_count_limit}</span>
                                </div>
                            </div>
                        `;
                    } else {
                        html += `
                            <div class="plex-section">
                                <h3>❌ Settings Error</h3>
                                <div class="info-value" style="color: #ff4757;">Failed to load settings</div>
                            </div>
                        `;
                    }
                    
                    html += '</div>';
                    
                    const container = document.getElementById('plex-container');
                    container.innerHTML = html;
                })
                .catch(error => {
                    handleAPIError(error, 'loadPlexContainer');
                    document.getElementById('plex-container').innerHTML = 
                        '<div class="info-value" style="color: #ff4757;">❌ Connection Error</div>';
                });
        }
        
        function refreshPlexSessions() {
            Promise.all([
                fetchWithTimeout('/api/status'),
                fetchWithTimeout('/api/plex-sessions')
            ])
                .then(responses => Promise.all(responses.map(r => r.json())))
                .then(([statusData, sessionsData]) => {
                    // Connection restored if it was lost
                    if (connectionLost) {
                        hideConnectionLostModal();
                    }
                    
                    const plex = statusData.plex;
                    const statusColor = plex.status === 'online' ? '#00ff41' : '#ff4757';
                    
                    // Update status and sessions count elements
                    const statusElement = document.getElementById('plex-status');
                    const sessionsElement = document.getElementById('plex-sessions');
                    
                    if (statusElement) {
                        statusElement.textContent = plex.status.toUpperCase();
                        statusElement.style.color = statusColor;
                    }
                    
                    if (sessionsElement) {
                        sessionsElement.textContent = plex.sessions;
                        sessionsElement.style.color = plex.sessions > 0 ? '#00ff41' : '#a0a0a0';
                    }
                    
                    // Update active sessions list
                    const sessionsContainer = document.getElementById('sessions-container');
                    if (sessionsContainer && sessionsData.status === 'success') {
                        let sessionsHtml = '';
                        
                        if (sessionsData.sessions && sessionsData.sessions.length > 0) {
                            sessionsHtml = '<div class="sessions-list">';
                            sessionsData.sessions.forEach(session => {
                                const videoIconClass = session.video_transcoding ? 'video-transcoding' : '';
                                const audioIconClass = session.audio_transcoding ? 'audio-transcoding' : '';
                                
                                sessionsHtml += `
                                    <div class="session-item">
                                        <div class="session-info">
                                            <div class="session-user">${session.user}</div>
                                            <div class="session-title">${session.title}</div>
                                        </div>
                                        <div class="session-device">
                                            <div class="session-device-name">${session.device}</div>
                                        </div>
                                        <div class="session-indicators">
                                            <span class="transcode-icon ${videoIconClass}" title="Video ${session.video_transcoding ? 'Transcoding' : 'Direct Play'}">🎬</span>
                                            <span class="transcode-icon ${audioIconClass}" title="Audio ${session.audio_transcoding ? 'Transcoding' : 'Direct Play'}">🔊</span>
                                        </div>
                                    </div>
                                `;
                            });
                            sessionsHtml += '</div>';
                        } else {
                            sessionsHtml = '<div class="no-sessions">No active sessions</div>';
                        }
                        
                        sessionsContainer.innerHTML = sessionsHtml;
                        
                        // Update sessions count in header
                        const sessionHeader = sessionsContainer.parentElement.querySelector('h3');
                        if (sessionHeader) {
                            sessionHeader.textContent = `Active Sessions (${sessionsData.count})`;
                        }
                    }
                })
                .catch(error => {
                    // Silently handle errors for periodic refresh to avoid spam
                    console.log('Plex sessions refresh error:', error.message);
                });
        }
    '''

def get_plex_html():
    """Return the Plex component HTML structure"""
    return '''
        <div id="plex-container" class="status-card plex-container">
            <div class="loading"></div>
        </div>
    '''
