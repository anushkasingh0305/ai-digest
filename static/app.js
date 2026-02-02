/**
 * AI Digest Dashboard Application
 * Provides REST API integration and UI management with JWT authentication
 */

// Authentication State
let authState = {
    token: localStorage.getItem('auth_token'),
    username: localStorage.getItem('auth_user'),

    setToken(token, username) {
        this.token = token;
        this.username = username;
        localStorage.setItem('auth_token', token);
        localStorage.setItem('auth_user', username);
    },

    clearToken() {
        this.token = null;
        this.username = null;
        localStorage.removeItem('auth_token');
        localStorage.removeItem('auth_user');
    },

    isAuthenticated() {
        return !!this.token;
    }
};

// API Client
const API = {
    BASE_URL: window.location.origin,

    async get(endpoint) {
        try {
            const response = await fetch(`${this.BASE_URL}${endpoint}`, {
                headers: this._getAuthHeaders()
            });
            if (response.status === 401) {
                authState.clearToken();
                window.location.reload();
                throw new Error('Unauthorized');
            }
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`GET ${endpoint}:`, error);
            throw error;
        }
    },

    async post(endpoint, data = {}) {
        try {
            const response = await fetch(`${this.BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...this._getAuthHeaders()
                },
                body: JSON.stringify(data)
            });
            if (response.status === 401) {
                authState.clearToken();
                window.location.reload();
                throw new Error('Unauthorized');
            }
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`POST ${endpoint}:`, error);
            throw error;
        }
    },

    async put(endpoint, data = {}) {
        try {
            const response = await fetch(`${this.BASE_URL}${endpoint}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    ...this._getAuthHeaders()
                },
                body: JSON.stringify(data)
            });
            if (response.status === 401) {
                authState.clearToken();
                window.location.reload();
                throw new Error('Unauthorized');
            }
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`PUT ${endpoint}:`, error);
            throw error;
        }
    },

    async delete(endpoint) {
        try {
            const response = await fetch(`${this.BASE_URL}${endpoint}`, {
                method: 'DELETE',
                headers: this._getAuthHeaders()
            });
            if (response.status === 401) {
                authState.clearToken();
                window.location.reload();
                throw new Error('Unauthorized');
            }
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`DELETE ${endpoint}:`, error);
            throw error;
        }
    },

    _getAuthHeaders() {
        if (authState.token) {
            return { 'Authorization': `Bearer ${authState.token}` };
        }
        return {};
    },

    // Authentication
    login(username, password) { 
        return fetch(`${this.BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        }).then(r => r.json());
    },

    // Health & Info
    getHealth() { return this.get('/health'); },
    getInfo() { return this.get('/info'); },

    // Configuration
    getConfig() { return this.get('/api/config'); },
    updateConfig(config) { return this.post('/api/config', config); },
    getAdaptersConfig() { return this.get('/api/config/adapters'); },
    updateAdapterConfig(name, config) { return this.post(`/api/config/adapters/${name}`, config); },
    getDeliveryConfig() { return this.get('/api/config/delivery'); },
    updateDeliveryConfig(config) { return this.post('/api/config/delivery', config); },
    getSchedulerConfig() { return this.get('/api/config/scheduler'); },
    updateSchedulerConfig(config) { return this.post('/api/config/scheduler', config); },
    getLoggingConfig() { return this.get('/api/config/logging'); },
    updateLoggingConfig(config) { return this.post('/api/config/logging', config); },

    // Pipeline
    runPipeline(deliver = false) { return this.post('/api/pipeline/run', { deliver }); },

    // Scheduler
    getSchedulerStatus() { return this.get('/api/scheduler/status'); },
    startScheduler(deliver = true, hour = 6, minute = 0) {
        return this.post('/api/scheduler/start', { deliver, hour, minute });
    },
    stopScheduler() { return this.post('/api/scheduler/stop'); },

    // Digests
    listDigests(limit = 10, offset = 0, days = null) {
        let url = `/api/digests?limit=${limit}&offset=${offset}`;
        if (days) url += `&days=${days}`;
        return this.get(url);
    },
    getDigest(id) { return this.get(`/api/digests/${id}`); },
    deleteDigest(id) { return this.delete(`/api/digests/${id}`); },

    // Webhooks
    getWebhooks() { return this.get('/api/webhooks'); },
    createWebhook(data) { return this.post('/api/webhooks', data); },
    updateWebhook(id, data) { return this.put(`/api/webhooks/${id}`, data); },
    deleteWebhook(id) { return this.delete(`/api/webhooks/${id}`); },
    toggleWebhook(id) { return this.post(`/api/webhooks/${id}/toggle`, {}); },
    testWebhook(id) { return this.post(`/api/webhooks/${id}/test`, {}); },
};

// State Management
const State = {
    activityLog: [],

    addActivity(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        this.activityLog.unshift({ timestamp, message, type });
        if (this.activityLog.length > 50) this.activityLog.pop();
        this.updateActivityDisplay();
    },

    updateActivityDisplay() {
        const container = document.getElementById('activity-log');
        if (!container) return;

        if (this.activityLog.length === 0) {
            container.innerHTML = '<p class="empty">No activity yet</p>';
            return;
        }

        container.innerHTML = this.activityLog
            .map(entry => `<div class="log-entry ${entry.type}"><strong>${entry.timestamp}</strong>: ${entry.message}</div>`)
            .join('');
    }
};

// UI Manager
const UI = {
    showMessage(elementId, message, type = 'info') {
        const element = document.getElementById(elementId);
        if (!element) return;

        element.textContent = message;
        element.className = `status-message ${type}`;
        setTimeout(() => {
            element.className = 'status-message';
        }, 5000);
    },

    async setLoading(elementId, loading = true) {
        const element = document.getElementById(elementId);
        if (!element) return;

        if (loading) {
            element.innerHTML = '<div class="spinner"></div> Loading...';
        }
    },

    async updateStatus() {
        try {
            const health = await API.getHealth();
            const statusDot = document.getElementById('status-indicator');
            const statusText = document.getElementById('status-text');

            statusDot.className = 'status-dot ok';
            statusText.textContent = 'System OK';
            State.addActivity('System status: OK', 'info');
        } catch (error) {
            const statusDot = document.getElementById('status-indicator');
            const statusText = document.getElementById('status-text');

            statusDot.className = 'status-dot error';
            statusText.textContent = 'System Error';
            State.addActivity('System status: Error', 'error');
        }
    }
};

// Tab Management
class TabManager {
    constructor() {
        this.webhooksCache = {};
        this.setupTabListeners();
    }

    setupTabListeners() {
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });
    }

    switchTab(tabName) {
        // Hide all tabs
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });

        // Deactivate all buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });

        // Show selected tab
        const tabElement = document.getElementById(`${tabName}-tab`);
        if (tabElement) {
            tabElement.classList.add('active');
            document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
            this.loadTabContent(tabName);
        }
    }

    async loadTabContent(tabName) {
        switch (tabName) {
            case 'overview':
                await this.loadOverview();
                break;
            case 'schedule':
                await this.loadSchedule();
                break;
            case 'delivery':
                await this.loadDelivery();
                break;
            case 'adapters':
                await this.loadAdapters();
                break;
            case 'logging':
                await this.loadLogging();
                break;
            case 'digests':
                await this.loadDigests();
                break;
            case 'webhooks':
                await this.loadWebhooks();
                break;
        }
    }

    async loadOverview() {
        try {
            const config = await API.getConfig();
            const scheduler = await API.getSchedulerStatus();

            const html = `
                <p><strong>Scheduler Status:</strong> ${scheduler.running ? '✅ Running' : '⏸ Stopped'}</p>
                <p><strong>Active Jobs:</strong> ${scheduler.job_count}</p>
                <p><strong>Delivery Enabled:</strong> ${config.scheduler.delivery_enabled ? '✅' : '❌'}</p>
                <p><strong>Log Level:</strong> ${config.logging.level}</p>
            `;
            document.getElementById('overview-status').innerHTML = html;
        } catch (error) {
            document.getElementById('overview-status').innerHTML = `<p class="empty">Error loading status</p>`;
        }
    }

    async loadSchedule() {
        try {
            const config = await API.getSchedulerConfig();
            const scheduler = await API.getSchedulerStatus();

            document.getElementById('schedule-hour').value = config.hour;
            document.getElementById('schedule-minute').value = config.minute;
            document.getElementById('schedule-deliver').checked = config.delivery_enabled;

            const statusHtml = `
                <p><strong>Status:</strong> ${scheduler.running ? '✅ Running' : '⏸ Stopped'}</p>
                <p><strong>Current Schedule:</strong> ${config.hour.toString().padStart(2, '0')}:${config.minute.toString().padStart(2, '0')} UTC</p>
                <p><strong>Active Jobs:</strong> ${scheduler.job_count}</p>
            `;
            document.getElementById('scheduler-status').innerHTML = statusHtml;
        } catch (error) {
            console.error('Error loading schedule:', error);
        }
    }

    async loadDelivery() {
        try {
            const config = await API.getDeliveryConfig();

            document.getElementById('delivery-email-enabled').checked = config.email_enabled;
            document.getElementById('delivery-email-address').value = config.email_address || '';
            document.getElementById('delivery-telegram-enabled').checked = config.telegram_enabled;
            document.getElementById('delivery-telegram-chat-id').value = config.telegram_chat_id || '';
        } catch (error) {
            console.error('Error loading delivery config:', error);
        }
    }

    async loadAdapters() {
        try {
            const config = await API.getAdaptersConfig();
            const container = document.getElementById('adapters-list');

            if (Object.keys(config.adapters).length === 0) {
                container.innerHTML = '<p class="empty">No adapters configured</p>';
                return;
            }

            container.innerHTML = Object.entries(config.adapters).map(([name, adapter]) => `
                <div class="adapter-card ${adapter.enabled ? 'enabled' : 'disabled'}">
                    <div class="adapter-header">
                        <span class="adapter-name">${name}</span>
                        <div class="adapter-toggle ${adapter.enabled ? 'on' : ''}" data-adapter="${name}"></div>
                    </div>
                    <div class="adapter-settings">
                        <p><strong>Status:</strong> ${adapter.enabled ? '✅ Enabled' : '⏸ Disabled'}</p>
                        ${Object.keys(adapter.settings).length > 0 ? `
                            <p><strong>Settings:</strong></p>
                            <pre>${JSON.stringify(adapter.settings, null, 2)}</pre>
                        ` : ''}
                    </div>
                </div>
            `).join('');

            // Add toggle listeners
            document.querySelectorAll('.adapter-toggle').forEach(toggle => {
                toggle.addEventListener('click', (e) => this.toggleAdapter(toggle.dataset.adapter));
            });
        } catch (error) {
            console.error('Error loading adapters:', error);
        }
    }

    async toggleAdapter(name) {
        try {
            const config = await API.getAdaptersConfig();
            const adapter = config.adapters[name];
            if (!adapter) return;

            adapter.enabled = !adapter.enabled;
            await API.updateAdapterConfig(name, adapter);

            State.addActivity(`Adapter '${name}' ${adapter.enabled ? 'enabled' : 'disabled'}`, 'success');
            await this.loadAdapters();
        } catch (error) {
            State.addActivity(`Error updating adapter '${name}'`, 'error');
        }
    }

    async loadLogging() {
        try {
            const config = await API.getLoggingConfig();

            document.getElementById('logging-level').value = config.level;
            document.getElementById('logging-file-enabled').checked = config.file_enabled;
            document.getElementById('logging-console-enabled').checked = config.console_enabled;

            const infoHtml = `
                <p><strong>Log Level:</strong> ${config.level}</p>
                <p><strong>File Output:</strong> ${config.file_enabled ? '✅' : '❌'}</p>
                <p><strong>File Path:</strong> ${config.file_path}</p>
                <p><strong>Console Output:</strong> ${config.console_enabled ? '✅' : '❌'}</p>
            `;
            document.getElementById('logging-info').innerHTML = infoHtml;
        } catch (error) {
            console.error('Error loading logging config:', error);
        }
    }

    async loadDigests() {
        try {
            const limit = parseInt(document.getElementById('digests-limit').value) || 10;
            const offset = parseInt(document.getElementById('digests-offset').value) || 0;

            const response = await API.listDigests(limit, offset);
            const container = document.getElementById('digests-list');

            if (response.digests.length === 0) {
                container.innerHTML = '<p class="empty">No digests found</p>';
                return;
            }

            container.innerHTML = response.digests.map(digest => `
                <div class="digest-item">
                    <div class="digest-info">
                        <div class="digest-id">${digest.id}</div>
                        <div class="digest-meta">
                            Generated: ${new Date(digest.created_at).toLocaleString()} |
                            Duration: ${digest.duration_seconds}s
                        </div>
                    </div>
                    <div class="digest-actions">
                        <button class="btn btn-secondary" onclick="tabManager.viewDigest('${digest.id}')">View</button>
                        <button class="btn btn-danger" onclick="tabManager.deleteDigest('${digest.id}')">Delete</button>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading digests:', error);
        }
    }

    async loadWebhooks() {
        try {
            const webhooks = await API.getWebhooks();
            const container = document.getElementById('webhooks-list');

            this.webhooksCache = {};
            webhooks.forEach(w => {
                this.webhooksCache[w.id] = w;
            });

            if (!webhooks || webhooks.length === 0) {
                container.innerHTML = '<p class="empty">No webhooks configured</p>';
                return;
            }

            container.innerHTML = webhooks.map(w => `
                <div class="webhook-item" id="webhook-${w.id}">
                    <div class="webhook-info">
                        <div class="webhook-name">${w.name} <span class="muted">(${w.id})</span></div>
                        <div class="webhook-meta">Type: ${w.type} • URL: ${w.url}</div>
                    </div>
                    <div class="webhook-actions">
                        <button class="btn btn-secondary" data-action="edit" data-id="${w.id}">Edit</button>
                        <button class="btn btn-secondary" data-action="test" data-id="${w.id}">Test</button>
                        <button class="btn btn-secondary" data-action="toggle" data-id="${w.id}">${w.enabled ? 'Disable' : 'Enable'}</button>
                        <button class="btn btn-danger" data-action="delete" data-id="${w.id}">Delete</button>
                    </div>
                </div>
            `).join('');

            // Attach actions
            container.querySelectorAll('.webhook-actions button').forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    const action = btn.dataset.action;
                    const id = btn.dataset.id;
                    try {
                        if (action === 'edit') {
                            this.enterWebhookEditMode(id);
                        } else if (action === 'test') {
                            await API.testWebhook(id);
                            State.addActivity(`Webhook ${id} test sent`, 'success');
                            UI.showMessage('webhook-message', 'Test notification sent', 'success');
                        } else if (action === 'toggle') {
                            await API.toggleWebhook(id);
                            State.addActivity(`Webhook ${id} toggled`, 'success');
                            tabManager.loadWebhooks();
                        } else if (action === 'delete') {
                            if (!confirm('Delete webhook?')) return;
                            await API.deleteWebhook(id);
                            State.addActivity(`Webhook ${id} deleted`, 'success');
                            tabManager.loadWebhooks();
                        }
                    } catch (err) {
                        State.addActivity(`Webhook action failed: ${err.message}`, 'error');
                        UI.showMessage('webhook-message', 'Action failed: ' + err.message, 'error');
                    }
                });

                enterWebhookEditMode(id) {
                    const webhook = this.webhooksCache[id];
                    if (!webhook) return;

                    editingWebhookId = id;
                    document.getElementById('webhook-id').value = webhook.id;
                    document.getElementById('webhook-id').disabled = true;
                    document.getElementById('webhook-name').value = webhook.name;
                    document.getElementById('webhook-type').value = webhook.type;
                    document.getElementById('webhook-url').value = webhook.url;
                    document.getElementById('webhook-headers').value = webhook.headers ? JSON.stringify(webhook.headers) : '';
                    document.getElementById('webhook-payload').value = webhook.payload_template || '';

                    document.getElementById('webhook-mode').textContent = `Editing: ${webhook.id}`;
                    document.getElementById('btn-create-webhook').classList.add('hidden');
                    document.getElementById('btn-save-webhook').classList.remove('hidden');
                    document.getElementById('btn-cancel-webhook').classList.remove('hidden');
                }

                exitWebhookEditMode() {
                    editingWebhookId = null;
                    document.getElementById('webhook-id').value = '';
                    document.getElementById('webhook-id').disabled = false;
                    document.getElementById('webhook-name').value = '';
                    document.getElementById('webhook-type').value = 'slack';
                    document.getElementById('webhook-url').value = '';
                    document.getElementById('webhook-headers').value = '';
                    document.getElementById('webhook-payload').value = '';
                    document.getElementById('webhook-mode').textContent = 'Create new webhook';
                    document.getElementById('btn-create-webhook').classList.remove('hidden');
                    document.getElementById('btn-save-webhook').classList.add('hidden');
                    document.getElementById('btn-cancel-webhook').classList.add('hidden');
                }
            });
        } catch (error) {
            console.error('Error loading webhooks:', error);
            document.getElementById('webhooks-list').innerHTML = '<p class="empty">Error loading webhooks</p>';
        }
    }

    async deleteDigest(id) {
        if (!confirm('Are you sure you want to delete this digest?')) return;

        try {
            await API.deleteDigest(id);
            State.addActivity(`Digest '${id}' deleted`, 'success');
            await this.loadDigests();
        } catch (error) {
            State.addActivity(`Error deleting digest`, 'error');
        }
    }

    async viewDigest(id) {
        try {
            const digest = await API.getDigest(id);
            console.log('Digest content:', digest);
            // Could open a modal or new page here
            alert(`Digest: ${id}\n\nCheck browser console for full content.`);
        } catch (error) {
            State.addActivity(`Error loading digest`, 'error');
        }
    }
};

// Event Handlers
function setupEventListeners() {
    // Overview
    document.getElementById('btn-run-pipeline')?.addEventListener('click', handleRunPipeline);
    document.getElementById('btn-refresh')?.addEventListener('click', () => UI.updateStatus());

    // Pipeline
    document.getElementById('btn-run-pipeline-exec')?.addEventListener('click', handleRunPipeline);

    // Schedule
    document.getElementById('btn-update-schedule')?.addEventListener('click', handleUpdateSchedule);
    document.getElementById('btn-start-scheduler')?.addEventListener('click', handleStartScheduler);
    document.getElementById('btn-stop-scheduler')?.addEventListener('click', handleStopScheduler);

    // Delivery
    document.getElementById('btn-update-delivery')?.addEventListener('click', handleUpdateDelivery);

    // Logging
    document.getElementById('btn-update-logging')?.addEventListener('click', handleUpdateLogging);

    // Digests
    document.getElementById('btn-load-digests')?.addEventListener('click', () => tabManager.loadDigests());
    // Webhooks
    document.getElementById('btn-create-webhook')?.addEventListener('click', async (e) => {
        e.preventDefault();
        const id = document.getElementById('webhook-id').value.trim();
        const name = document.getElementById('webhook-name').value.trim();
        const type = document.getElementById('webhook-type').value;
        const url = document.getElementById('webhook-url').value.trim();
        const headersRaw = document.getElementById('webhook-headers').value.trim();
        const payloadRaw = document.getElementById('webhook-payload').value.trim();

        let headers = {};
        let payload_template = null;
        try {
            if (headersRaw) headers = JSON.parse(headersRaw);
        } catch (err) {
            UI.showMessage('webhook-message', 'Invalid headers JSON', 'error');
            return;
        }
        try {
            if (payloadRaw) payload_template = payloadRaw;
        } catch (err) {
            UI.showMessage('webhook-message', 'Invalid payload template', 'error');
            return;
        }

        if (!id || !name || !type || !url) {
            UI.showMessage('webhook-message', 'Missing required fields', 'error');
            return;
        }

        try {
            await API.createWebhook({ id, name, type, url, headers, payload_template });
            UI.showMessage('webhook-message', 'Webhook created', 'success');
            State.addActivity(`Webhook ${id} created`, 'success');
            // Clear form
            document.getElementById('webhook-id').value = '';
            document.getElementById('webhook-name').value = '';
            document.getElementById('webhook-url').value = '';
            document.getElementById('webhook-headers').value = '';
            document.getElementById('webhook-payload').value = '';
            tabManager.loadWebhooks();
        } catch (err) {
            UI.showMessage('webhook-message', 'Create failed: ' + (err.message || err), 'error');
        }
    });

    document.getElementById('btn-save-webhook')?.addEventListener('click', async (e) => {
        e.preventDefault();
        if (!editingWebhookId) return;

        const name = document.getElementById('webhook-name').value.trim();
        const type = document.getElementById('webhook-type').value;
        const url = document.getElementById('webhook-url').value.trim();
        const headersRaw = document.getElementById('webhook-headers').value.trim();
        const payloadRaw = document.getElementById('webhook-payload').value.trim();

        let headers = {};
        let payload_template = null;
        try {
            if (headersRaw) headers = JSON.parse(headersRaw);
        } catch (err) {
            UI.showMessage('webhook-message', 'Invalid headers JSON', 'error');
            return;
        }
        if (payloadRaw) payload_template = payloadRaw;

        try {
            await API.updateWebhook(editingWebhookId, { name, type, url, headers, payload_template });
            UI.showMessage('webhook-message', 'Webhook updated', 'success');
            State.addActivity(`Webhook ${editingWebhookId} updated`, 'success');
            tabManager.exitWebhookEditMode();
            tabManager.loadWebhooks();
        } catch (err) {
            UI.showMessage('webhook-message', 'Update failed: ' + (err.message || err), 'error');
        }
    });

    document.getElementById('btn-cancel-webhook')?.addEventListener('click', (e) => {
        e.preventDefault();
        tabManager.exitWebhookEditMode();
    });
}

async function handleRunPipeline() {
    const deliver = document.getElementById('pipeline-deliver')?.checked || false;

    try {
        const btn = event.target;
        btn.disabled = true;
        btn.textContent = '⏳ Running...';

        const result = await API.runPipeline(deliver);

        UI.showMessage('pipeline-status', 'Pipeline started successfully!', 'success');
        State.addActivity(`Pipeline execution started (deliver: ${deliver})`, 'success');

        btn.disabled = false;
        btn.textContent = '▶ Execute Pipeline Now';
    } catch (error) {
        UI.showMessage('pipeline-status', 'Failed to start pipeline: ' + error.message, 'error');
        State.addActivity('Pipeline execution failed', 'error');

        const btn = event.target;
        btn.disabled = false;
        btn.textContent = '▶ Execute Pipeline Now';
    }
}

async function handleUpdateSchedule() {
    const hour = parseInt(document.getElementById('schedule-hour').value);
    const minute = parseInt(document.getElementById('schedule-minute').value);
    const delivery_enabled = document.getElementById('schedule-deliver').checked;

    if (hour < 0 || hour > 23 || minute < 0 || minute > 59) {
        UI.showMessage('schedule-message', 'Invalid time values', 'error');
        return;
    }

    try {
        await API.updateSchedulerConfig({ enabled: true, hour, minute, delivery_enabled });
        UI.showMessage('schedule-message', 'Schedule updated successfully!', 'success');
        State.addActivity(`Schedule updated to ${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')} UTC`, 'success');
    } catch (error) {
        UI.showMessage('schedule-message', 'Failed to update schedule: ' + error.message, 'error');
    }
}

async function handleStartScheduler() {
    try {
        const hour = parseInt(document.getElementById('schedule-hour').value) || 6;
        const minute = parseInt(document.getElementById('schedule-minute').value) || 0;

        await API.startScheduler(true, hour, minute);
        State.addActivity('Scheduler started', 'success');
        setTimeout(() => tabManager.loadSchedule(), 500);
    } catch (error) {
        State.addActivity('Failed to start scheduler', 'error');
    }
}

async function handleStopScheduler() {
    try {
        await API.stopScheduler();
        State.addActivity('Scheduler stopped', 'success');
        setTimeout(() => tabManager.loadSchedule(), 500);
    } catch (error) {
        State.addActivity('Failed to stop scheduler', 'error');
    }
}

async function handleUpdateDelivery() {
    const config = {
        email_enabled: document.getElementById('delivery-email-enabled').checked,
        email_address: document.getElementById('delivery-email-address').value || null,
        telegram_enabled: document.getElementById('delivery-telegram-enabled').checked,
        telegram_chat_id: document.getElementById('delivery-telegram-chat-id').value || null
    };

    try {
        await API.updateDeliveryConfig(config);
        UI.showMessage('delivery-message', 'Delivery settings updated!', 'success');
        State.addActivity('Delivery configuration updated', 'success');
    } catch (error) {
        UI.showMessage('delivery-message', 'Failed to update delivery: ' + error.message, 'error');
    }
}

async function handleUpdateLogging() {
    const config = {
        level: document.getElementById('logging-level').value,
        file_enabled: document.getElementById('logging-file-enabled').checked,
        console_enabled: document.getElementById('logging-console-enabled').checked,
        file_path: 'logs/ai_digest.log'
    };

    try {
        await API.updateLoggingConfig(config);
        UI.showMessage('logging-message', 'Logging settings updated!', 'success');
        State.addActivity('Logging configuration updated', 'success');
    } catch (error) {
        UI.showMessage('logging-message', 'Failed to update logging: ' + error.message, 'error');
    }
}

// Initialize
let tabManager;
let editingWebhookId = null;
document.addEventListener('DOMContentLoaded', () => {
    // Check authentication
    if (!authState.isAuthenticated()) {
        // Show login page
        document.getElementById('login-page').style.display = 'flex';
        document.getElementById('dashboard-page').style.display = 'none';
        setupLoginHandlers();
        return;
    }

    // Show dashboard
    document.getElementById('login-page').style.display = 'none';
    document.getElementById('dashboard-page').style.display = 'block';

    tabManager = new TabManager();
    setupEventListeners();
    UI.updateStatus();

    // Auto-update status every 30 seconds
    setInterval(() => UI.updateStatus(), 30000);

    // Load initial overview
    tabManager.loadOverview();

    // Logout button
    document.getElementById('btn-logout').addEventListener('click', () => {
        authState.clearToken();
        location.reload();
    });
});

function setupLoginHandlers() {
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const errorDiv = document.getElementById('login-error');

        try {
            const response = await API.login(username, password);

            if (response.error) {
                errorDiv.textContent = response.error;
                return;
            }

            // Store token and reload
            authState.setToken(response.token, response.user);
            location.reload();
        } catch (error) {
            errorDiv.textContent = 'Login failed: ' + error.message;
        }
    });
}
