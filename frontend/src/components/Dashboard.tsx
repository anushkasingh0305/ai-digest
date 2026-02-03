import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { getUser } from '../utils/auth';
import './Dashboard.css';

interface DashboardProps {
  onLogout: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ onLogout }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [status, setStatus] = useState<any>(null);
  const [digests, setDigests] = useState<any[]>([]);
  const [webhooks, setWebhooks] = useState<any[]>([]);
  const username = getUser();

  useEffect(() => {
    loadStatus();
    loadDigests();
    if (activeTab === 'webhooks') {
      loadWebhooks();
    }
  }, [activeTab]);

  const loadStatus = async () => {
    try {
      const [healthRes, infoRes] = await Promise.all([
        api.getHealth(),
        api.getInfo()
      ]);
      setStatus({ health: healthRes.data, info: infoRes.data });
    } catch (error) {
      console.error('Failed to load status:', error);
    }
  };

  const loadDigests = async () => {
    try {
      const response = await api.listDigests(20);
      setDigests(response.data);
    } catch (error) {
      console.error('Failed to load digests:', error);
    }
  };

  const loadWebhooks = async () => {
    try {
      const response = await api.listWebhooks();
      setWebhooks(response.data);
    } catch (error) {
      console.error('Failed to load webhooks:', error);
    }
  };

  const handleRunPipeline = async () => {
    try {
      const response = await api.runPipeline(false);
      const data = response.data;
      let message = `Pipeline completed! Created digest with ${data.item_count} items.`;
      if (data.telegram_sent) {
        message += '\n\n✅ Telegram notification sent successfully!';
      } else if (data.telegram_error) {
        message += `\n\n⚠️ Telegram error: ${data.telegram_error}`;
      }
      alert(message);
      // Reload digests after pipeline runs
      loadDigests();
    } catch (error) {
      alert('Failed to run pipeline');
    }
  };

  const tabs = [
    { id: 'overview', name: 'Overview' },
    { id: 'pipeline', name: 'Pipeline' },
    { id: 'digests', name: 'Digests' },
    { id: 'webhooks', name: 'Webhooks' },
    { id: 'scheduler', name: 'Scheduler' },
    { id: 'config', name: 'Configuration' },
  ];

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-left">
          <h1>🤖 AI Digest</h1>
          <span className="status-badge">
            {status?.health?.status || 'Loading...'}
          </span>
        </div>
        <div className="header-right">
          <span className="username">👤 {username}</span>
          <button onClick={onLogout} className="logout-btn">Logout</button>
        </div>
      </header>

      <div className="dashboard-content">
        <nav className="tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.name}
            </button>
          ))}
        </nav>

        <main className="tab-content">
          {activeTab === 'overview' && (
            <div className="overview">
              <h2>System Overview</h2>
              <div className="stats-grid">
                <div className="stat-card">
                  <h3>Service Status</h3>
                  <p className="stat-value">{status?.health?.status || 'N/A'}</p>
                </div>
                <div className="stat-card">
                  <h3>Version</h3>
                  <p className="stat-value">{status?.info?.version || 'N/A'}</p>
                </div>
                <div className="stat-card">
                  <h3>Total Digests</h3>
                  <p className="stat-value">{digests.length}</p>
                </div>
                <div className="stat-card">
                  <h3>Service</h3>
                  <p className="stat-value">{status?.info?.name || 'AI Digest'}</p>
                </div>
              </div>
              <div style={{marginTop: '2rem'}}>
                <h3>Quick Actions</h3>
                <button onClick={handleRunPipeline} className="primary-btn">
                  🚀 Run Pipeline Now
                </button>
              </div>
            </div>
          )}

          {activeTab === 'pipeline' && (
            <div className="pipeline">
              <h2>Pipeline Management</h2>
              <p>Run the AI digest pipeline to collect and process content.</p>
              <button onClick={handleRunPipeline} className="primary-btn">
                Run Pipeline
              </button>
            </div>
          )}

          {activeTab === 'digests' && (
            <div className="digests">
              <h2>Recent Digests</h2>
              <button onClick={loadDigests} className="secondary-btn" style={{marginBottom: '1rem'}}>
                🔄 Refresh
              </button>
              {digests.length > 0 ? (
                <div className="list">
                  {digests.map((digest: any, index: number) => (
                    <div key={digest.id || index} className="list-item">
                      <span><strong>ID:</strong> {digest.id?.slice(0, 8) || 'N/A'}...</span>
                      <span><strong>Date:</strong> {digest.created_at ? new Date(digest.created_at).toLocaleString() : 'N/A'}</span>
                      <span><strong>Items:</strong> {digest.item_count || 0}</span>
                      <span className={`badge ${digest.status === 'completed' ? 'success' : 'warning'}`}>
                        {digest.status || 'Unknown'}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="empty-state">No digests found. Run the pipeline to create one!</p>
              )}
            </div>
          )}

          {activeTab === 'webhooks' && (
            <div className="webhooks">
              <h2>Webhooks</h2>
              {webhooks.length > 0 ? (
                <div className="list">
                  {webhooks.map((webhook: any) => (
                    <div key={webhook.id} className="list-item">
                      <span>{webhook.name || 'Unnamed'}</span>
                      <span className={`badge ${webhook.enabled ? 'success' : 'danger'}`}>
                        {webhook.enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="empty-state">No webhooks configured</p>
              )}
            </div>
          )}

          {activeTab === 'scheduler' && (
            <div className="scheduler">
              <h2>Scheduler Configuration</h2>
              <p>Configure automatic digest generation schedule.</p>
              <div className="form-group">
                <label>Schedule Time (Coming soon)</label>
              </div>
            </div>
          )}

          {activeTab === 'config' && (
            <div className="config">
              <h2>System Configuration</h2>
              <p>Manage system settings and adapters.</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default Dashboard;
