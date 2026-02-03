import axios, { AxiosInstance } from 'axios';
import { getToken } from '../utils/auth';

const API_BASE_URL = 'http://localhost:5000';

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// API methods
export const api = {
  // Auth
  login: (username: string, password: string) =>
    apiClient.post('/api/auth/login', { username, password }),

  // Health
  getHealth: () => apiClient.get('/health'),
  getInfo: () => apiClient.get('/info'),

  // Config
  getConfig: () => apiClient.get('/api/config'),
  updateConfig: (config: any) => apiClient.post('/api/config', config),
  getAdaptersConfig: () => apiClient.get('/api/config/adapters'),
  updateAdapterConfig: (name: string, config: any) =>
    apiClient.post(`/api/config/adapters/${name}`, config),
  getDeliveryConfig: () => apiClient.get('/api/config/delivery'),
  updateDeliveryConfig: (config: any) => apiClient.post('/api/config/delivery', config),
  getSchedulerConfig: () => apiClient.get('/api/config/scheduler'),
  updateSchedulerConfig: (config: any) => apiClient.post('/api/config/scheduler', config),
  getLoggingConfig: () => apiClient.get('/api/config/logging'),
  updateLoggingConfig: (config: any) => apiClient.post('/api/config/logging', config),

  // Pipeline
  runPipeline: (deliver: boolean = false) =>
    apiClient.post('/api/pipeline/run', { deliver }),

  // Scheduler
  getSchedulerStatus: () => apiClient.get('/api/scheduler/status'),
  startScheduler: (deliver: boolean = true, hour: number = 6, minute: number = 0) =>
    apiClient.post('/api/scheduler/start', { deliver, hour, minute }),
  stopScheduler: () => apiClient.post('/api/scheduler/stop'),

  // Digests
  listDigests: (limit: number = 10, offset: number = 0, days?: number) =>
    apiClient.get('/api/digests', { params: { limit, offset, days } }),
  getDigest: (id: string) => apiClient.get(`/api/digests/${id}`),
  deleteDigest: (id: string) => apiClient.delete(`/api/digests/${id}`),

  // Webhooks
  listWebhooks: () => apiClient.get('/api/webhooks'),
  createWebhook: (webhook: any) => apiClient.post('/api/webhooks', webhook),
  getWebhook: (id: string) => apiClient.get(`/api/webhooks/${id}`),
  updateWebhook: (id: string, webhook: any) => apiClient.put(`/api/webhooks/${id}`, webhook),
  deleteWebhook: (id: string) => apiClient.delete(`/api/webhooks/${id}`),
  testWebhook: (id: string) => apiClient.post(`/api/webhooks/${id}/test`),
};

export default apiClient;
