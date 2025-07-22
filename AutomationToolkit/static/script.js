// Progressive Desktop Automation Challenge System - JavaScript

class AutomationDashboard {
    constructor() {
        this.challenges = [];
        this.logs = [];
        this.updateInterval = null;
        this.init();
    }

    async init() {
        console.log('Initializing Automation Dashboard...');
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Start periodic updates
        this.startPeriodicUpdates();
        
        // Initial data load
        await this.loadChallenges();
        await this.loadLogs();
        await this.loadSystemInfo();
        
        console.log('Dashboard initialized successfully');
    }

    setupEventListeners() {
        // Global controls
        document.addEventListener('DOMContentLoaded', () => {
            this.bindGlobalControls();
        });

        // Auto-refresh toggle
        const autoRefreshToggle = document.getElementById('auto-refresh');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.startPeriodicUpdates();
                } else {
                    this.stopPeriodicUpdates();
                }
            });
        }

        // Screenshot button
        const screenshotBtn = document.getElementById('take-screenshot');
        if (screenshotBtn) {
            screenshotBtn.addEventListener('click', () => this.takeScreenshot());
        }

        // Clear logs button
        const clearLogsBtn = document.getElementById('clear-logs');
        if (clearLogsBtn) {
            clearLogsBtn.addEventListener('click', () => this.clearLogs());
        }

        // Configuration settings button
        const configBtn = document.getElementById('config-settings');
        if (configBtn) {
            configBtn.addEventListener('click', () => openConfigModal());
        }
    }

    bindGlobalControls() {
        // Run all challenges button
        const runAllBtn = document.getElementById('run-all-challenges');
        if (runAllBtn) {
            runAllBtn.addEventListener('click', () => this.runAllChallenges());
        }

        // Stop all challenges button
        const stopAllBtn = document.getElementById('stop-all-challenges');
        if (stopAllBtn) {
            stopAllBtn.addEventListener('click', () => this.stopAllChallenges());
        }

        // Refresh data button
        const refreshBtn = document.getElementById('refresh-data');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshAllData());
        }
    }

    startPeriodicUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }

        this.updateInterval = setInterval(async () => {
            try {
                await this.loadChallenges();
                await this.loadLogs();
            } catch (error) {
                console.error('Error during periodic update:', error);
            }
        }, 3000); // Update every 3 seconds
    }

    stopPeriodicUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    async loadChallenges() {
        try {
            const response = await fetch('/api/challenges');
            const data = await response.json();

            if (data.success) {
                this.challenges = data.challenges;
                this.renderChallenges();
                this.updateOverallProgress();
            } else {
                this.showAlert('Error loading challenges: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Error loading challenges:', error);
            this.showAlert('Failed to load challenges: ' + error.message, 'error');
        }
    }

    async loadLogs() {
        try {
            const response = await fetch('/api/logs');
            const data = await response.json();

            if (data.success) {
                const newLogs = data.logs;
                
                // Check for new log entries
                const existingLogCount = this.logs.length;
                this.logs = newLogs;
                
                this.renderLogs();
                
                // Scroll to bottom if new logs were added
                if (newLogs.length > existingLogCount) {
                    this.scrollLogsToBottom();
                }
            } else {
                console.error('Error loading logs:', data.error);
            }
        } catch (error) {
            console.error('Error loading logs:', error);
        }
    }

    async loadSystemInfo() {
        try {
            const response = await fetch('/api/system/info');
            const data = await response.json();

            if (data.success) {
                this.renderSystemInfo(data.system_info);
            } else {
                console.error('Error loading system info:', data.error);
            }
        } catch (error) {
            console.error('Error loading system info:', error);
        }
    }

    renderChallenges() {
        const container = document.getElementById('challenges-container');
        if (!container) return;

        container.innerHTML = '';

        this.challenges.forEach(challenge => {
            const challengeElement = this.createChallengeElement(challenge);
            container.appendChild(challengeElement);
        });
    }

    createChallengeElement(challenge) {
        const div = document.createElement('div');
        div.className = `challenge-item ${challenge.status}`;
        div.setAttribute('data-level', challenge.level);

        // Determine prerequisites status
        const prerequisitesText = challenge.prerequisites.length > 0 
            ? `Requires: Level ${challenge.prerequisites.join(', ')}`
            : 'No prerequisites';

        // Format last run time
        const lastRun = challenge.last_run 
            ? new Date(challenge.last_run * 1000).toLocaleString()
            : 'Never';

        div.innerHTML = `
            <div class="challenge-header">
                <div class="challenge-title">
                    Level ${challenge.level}: ${challenge.name}
                </div>
                <div class="challenge-status status-${challenge.status}">
                    ${challenge.status.replace('_', ' ')}
                </div>
            </div>
            
            <div class="challenge-description">
                ${challenge.description}
            </div>
            
            <div class="challenge-progress">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${(challenge.progress || 0) * 100}%"></div>
                </div>
                <div class="progress-text">
                    ${challenge.current_step || 0}/${challenge.total_steps || 0} steps
                    (${Math.round((challenge.progress || 0) * 100)}%)
                </div>
            </div>
            
            <div class="challenge-meta">
                <span class="prerequisites">${prerequisitesText}</span>
                <span class="last-run">Last run: ${lastRun}</span>
            </div>
            
            <div class="challenge-stats">
                <span class="success-count">✓ ${challenge.success_count}</span>
                <span class="failure-count">✗ ${challenge.failure_count}</span>
            </div>
            
            <div class="challenge-actions">
                ${this.createChallengeActionButtons(challenge)}
            </div>
        `;

        return div;
    }

    createChallengeActionButtons(challenge) {
        const canRun = challenge.status !== 'running';
        const hasError = challenge.status === 'failed' || challenge.status === 'error';
        
        let buttons = '';

        // Start/Run button
        if (canRun) {
            buttons += `
                <button class="btn btn-primary" 
                        onclick="dashboard.startChallenge(${challenge.level})"
                        ${challenge.status === 'running' ? 'disabled' : ''}>
                    <span class="icon">▶</span>
                    ${challenge.status === 'completed' ? 'Rerun' : 'Start'}
                </button>
            `;
        } else {
            buttons += `
                <button class="btn btn-secondary" disabled>
                    <span class="loading"></span>
                    Running...
                </button>
            `;
        }

        // Status button
        buttons += `
            <button class="btn btn-secondary" 
                    onclick="dashboard.showChallengeStatus(${challenge.level})">
                <span class="icon">ℹ</span>
                Status
            </button>
        `;

        // Reset button (if failed or completed)
        if (challenge.status === 'failed' || challenge.status === 'completed') {
            buttons += `
                <button class="btn btn-warning" 
                        onclick="dashboard.resetChallenge(${challenge.level})">
                    <span class="icon">↻</span>
                    Reset
                </button>
            `;
        }

        return buttons;
    }

    renderLogs() {
        const container = document.getElementById('logs-container');
        if (!container) return;

        // Keep only recent logs for performance
        const recentLogs = this.logs.slice(-100);
        
        container.innerHTML = '';

        recentLogs.forEach(log => {
            const logElement = this.createLogElement(log);
            container.appendChild(logElement);
        });
    }

    createLogElement(log) {
        const div = document.createElement('div');
        div.className = `log-entry log-${log.event_type || 'info'}`;

        const timestamp = new Date(log.timestamp * 1000).toLocaleTimeString();
        
        div.innerHTML = `
            <span class="log-timestamp">[${timestamp}]</span>
            <span class="log-level">Level ${log.level}:</span>
            <span class="log-message">${this.escapeHtml(log.message)}</span>
        `;

        return div;
    }

    renderSystemInfo(systemInfo) {
        const container = document.getElementById('system-info-container');
        if (!container) return;

        // Update system status indicator
        this.updateSystemStatus(systemInfo);

        container.innerHTML = `
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Platform</div>
                    <div class="info-value">${systemInfo.platform?.system || 'Unknown'} ${systemInfo.platform?.release || ''}</div>
                </div>
                
                <div class="info-item">
                    <div class="info-label">Architecture</div>
                    <div class="info-value">${systemInfo.platform?.machine || 'Unknown'}</div>
                </div>
                
                <div class="info-item">
                    <div class="info-label">Installed Software</div>
                    <div class="info-value">${systemInfo.installed_software?.length || 0} applications detected</div>
                </div>
                
                <div class="info-item">
                    <div class="info-label">Project Directory</div>
                    <div class="info-value">${systemInfo.system_paths?.desktop || 'Not configured'}</div>
                </div>
            </div>
            
            <div class="installed-software">
                <h4>Detected Software:</h4>
                <div class="software-list">
                    ${this.renderInstalledSoftware(systemInfo.installed_software || [])}
                </div>
            </div>
        `;
    }

    renderInstalledSoftware(softwareList) {
        if (softwareList.length === 0) {
            return '<p class="no-software">No software detected</p>';
        }

        return softwareList.map(software => `
            <div class="software-item">
                <strong>${software.name}</strong>
                <span class="software-details">${software.details}</span>
            </div>
        `).join('');
    }

    updateSystemStatus(systemInfo) {
        const statusElement = document.querySelector('.system-status');
        if (!statusElement) return;

        const hasKiCad = systemInfo.installed_software?.some(s => 
            s.name.toLowerCase().includes('kicad')
        );

        if (hasKiCad) {
            statusElement.className = 'system-status';
            statusElement.innerHTML = '<span class="icon">✓</span> System Ready';
        } else {
            statusElement.className = 'system-status error';
            statusElement.innerHTML = '<span class="icon">⚠</span> KiCad Not Detected';
        }
    }

    updateOverallProgress() {
        const completedChallenges = this.challenges.filter(c => c.status === 'completed').length;
        const totalChallenges = this.challenges.length;
        const progressPercentage = totalChallenges > 0 ? (completedChallenges / totalChallenges) * 100 : 0;

        // Update progress bar
        const progressFill = document.querySelector('.overall-progress-fill');
        if (progressFill) {
            progressFill.style.width = `${progressPercentage}%`;
        }

        // Update progress text
        const progressText = document.querySelector('.progress-text');
        if (progressText) {
            progressText.textContent = `${completedChallenges}/${totalChallenges} Challenges (${Math.round(progressPercentage)}%)`;
        }

        // Update challenge statistics
        const runningChallenges = this.challenges.filter(c => c.status === 'running').length;
        const failedChallenges = this.challenges.filter(c => c.status === 'failed').length;

        const statsContainer = document.getElementById('challenge-stats');
        if (statsContainer) {
            statsContainer.innerHTML = `
                <div class="stat-item">
                    <div class="stat-value">${completedChallenges}</div>
                    <div class="stat-label">Completed</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${runningChallenges}</div>
                    <div class="stat-label">Running</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${failedChallenges}</div>
                    <div class="stat-label">Failed</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${Math.round(progressPercentage)}%</div>
                    <div class="stat-label">Progress</div>
                </div>
            `;
        }
    }

    async startChallenge(level) {
        try {
            const response = await fetch(`/api/challenge/${level}/start`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showAlert(`Started challenge level ${level}`, 'success');
                // Refresh challenges to show updated status
                setTimeout(() => this.loadChallenges(), 1000);
            } else {
                this.showAlert(`Failed to start challenge: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Error starting challenge:', error);
            this.showAlert(`Error starting challenge: ${error.message}`, 'error');
        }
    }

    async showChallengeStatus(level) {
        try {
            const response = await fetch(`/api/challenge/${level}/status`);
            const data = await response.json();
            
            if (data.success) {
                const status = data.status;
                const statusText = `
                    Challenge Level ${status.level}: ${status.name}
                    Status: ${status.status}
                    Progress: ${status.current_step}/${status.total_steps} steps
                    Last Error: ${status.last_error || 'None'}
                    Execution Time: ${status.execution_time ? status.execution_time.toFixed(2) + 's' : 'N/A'}
                `;
                
                alert(statusText);
            } else {
                this.showAlert(`Failed to get status: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Error getting challenge status:', error);
            this.showAlert(`Error getting status: ${error.message}`, 'error');
        }
    }

    async resetChallenge(level) {
        if (!confirm(`Are you sure you want to reset Challenge Level ${level}?`)) {
            return;
        }

        try {
            // Note: This would require implementing a reset endpoint
            this.showAlert(`Reset functionality not yet implemented for level ${level}`, 'warning');
        } catch (error) {
            console.error('Error resetting challenge:', error);
            this.showAlert(`Error resetting challenge: ${error.message}`, 'error');
        }
    }

    async runAllChallenges() {
        if (!confirm('Are you sure you want to run all challenges sequentially?')) {
            return;
        }

        this.showAlert('Starting all challenges sequentially...', 'info');
        
        // Sort challenges by level
        const sortedChallenges = [...this.challenges].sort((a, b) => a.level - b.level);
        
        for (const challenge of sortedChallenges) {
            if (challenge.status !== 'running') {
                await this.startChallenge(challenge.level);
                // Wait a bit before starting next challenge
                await this.sleep(2000);
            }
        }
    }

    async stopAllChallenges() {
        this.showAlert('Stop functionality not yet implemented', 'warning');
    }

    async takeScreenshot() {
        const button = document.getElementById('take-screenshot');
        if (button) {
            button.disabled = true;
            button.innerHTML = '<span class="loading"></span> Taking Screenshot...';
        }

        try {
            const response = await fetch('/api/system/screenshot');
            const data = await response.json();
            
            if (data.success) {
                this.displayScreenshot(data.screenshot);
                this.showAlert('Screenshot captured successfully', 'success');
            } else {
                this.showAlert(`Failed to take screenshot: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Error taking screenshot:', error);
            this.showAlert(`Error taking screenshot: ${error.message}`, 'error');
        } finally {
            if (button) {
                button.disabled = false;
                button.innerHTML = '<span class="icon">📷</span> Take Screenshot';
            }
        }
    }

    displayScreenshot(screenshotData) {
        const container = document.getElementById('screenshot-container');
        if (!container) return;

        container.innerHTML = `
            <img src="${screenshotData}" 
                 alt="Desktop Screenshot" 
                 class="screenshot-image"
                 onclick="this.style.maxWidth = this.style.maxWidth === '100%' ? 'none' : '100%'">
            <p class="screenshot-info">Click image to toggle full size</p>
        `;
    }

    clearLogs() {
        this.logs = [];
        this.renderLogs();
        this.showAlert('Logs cleared', 'info');
    }

    async refreshAllData() {
        this.showAlert('Refreshing all data...', 'info');
        
        try {
            await Promise.all([
                this.loadChallenges(),
                this.loadLogs(),
                this.loadSystemInfo()
            ]);
            
            this.showAlert('Data refreshed successfully', 'success');
        } catch (error) {
            console.error('Error refreshing data:', error);
            this.showAlert(`Error refreshing data: ${error.message}`, 'error');
        }
    }

    showAlert(message, type = 'info') {
        // Create alert element
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.textContent = message;

        // Add to alerts container or create one
        let alertsContainer = document.getElementById('alerts-container');
        if (!alertsContainer) {
            alertsContainer = document.createElement('div');
            alertsContainer.id = 'alerts-container';
            alertsContainer.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
                max-width: 400px;
            `;
            document.body.appendChild(alertsContainer);
        }

        alertsContainer.appendChild(alert);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 5000);
    }

    scrollLogsToBottom() {
        const container = document.getElementById('logs-container');
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize dashboard when page loads
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new AutomationDashboard();
});

// Global keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl+R: Refresh data
    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        if (dashboard) {
            dashboard.refreshAllData();
        }
    }
    
    // Ctrl+S: Take screenshot
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        if (dashboard) {
            dashboard.takeScreenshot();
        }
    }
    
    // Escape: Clear alerts
    if (e.key === 'Escape') {
        const alertsContainer = document.getElementById('alerts-container');
        if (alertsContainer) {
            alertsContainer.innerHTML = '';
        }
    }
});

// Handle page visibility changes to pause/resume updates
document.addEventListener('visibilitychange', () => {
    if (dashboard) {
        if (document.hidden) {
            dashboard.stopPeriodicUpdates();
        } else {
            const autoRefreshToggle = document.getElementById('auto-refresh');
            if (!autoRefreshToggle || autoRefreshToggle.checked) {
                dashboard.startPeriodicUpdates();
            }
        }
    }
});

// Export for global access
window.dashboard = dashboard;
