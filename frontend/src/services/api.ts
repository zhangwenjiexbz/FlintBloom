import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Offline Analysis API
export const offlineApi = {
  // Threads
  listThreads: (params?: { limit?: number; offset?: number }) =>
    apiClient.get('/offline/threads', { params }),

  // Checkpoints
  listCheckpoints: (threadId: string, params?: { limit?: number; offset?: number }) =>
    apiClient.get(`/offline/threads/${threadId}/checkpoints`, { params }),

  // Trace
  getTrace: (threadId: string, checkpointId: string, includeBlobs = false) =>
    apiClient.get(`/offline/threads/${threadId}/checkpoints/${checkpointId}/trace`, {
      params: { include_blobs: includeBlobs },
    }),

  // Analysis
  analyzeThread: (threadId: string) =>
    apiClient.get(`/offline/threads/${threadId}/analysis`),

  // Timeline
  getTimeline: (threadId: string, limit = 100) =>
    apiClient.get(`/offline/threads/${threadId}/timeline`, { params: { limit } }),

  // Compare
  compareCheckpoints: (threadId: string, checkpointId1: string, checkpointId2: string) =>
    apiClient.get(`/offline/threads/${threadId}/compare`, {
      params: { checkpoint_id_1: checkpointId1, checkpoint_id_2: checkpointId2 },
    }),

  // Database info
  getDatabaseInfo: () =>
    apiClient.get('/offline/database/info'),
};

// Real-time Tracking API
export const realtimeApi = {
  // Threads
  listActiveThreads: () =>
    apiClient.get('/realtime/threads'),

  // Events
  getThreadEvents: (threadId: string, params?: { limit?: number; offset?: number }) =>
    apiClient.get(`/realtime/threads/${threadId}/events`, { params }),

  // Summary
  getThreadSummary: (threadId: string) =>
    apiClient.get(`/realtime/threads/${threadId}/summary`),

  // Clear events
  clearThreadEvents: (threadId: string) =>
    apiClient.delete(`/realtime/threads/${threadId}/events`),

  // Export
  exportThreadEvents: (threadId: string, format: 'json' | 'jsonl' = 'json') =>
    apiClient.get(`/realtime/threads/${threadId}/export`, { params: { format } }),

  // WebSocket URL
  getWebSocketUrl: (threadId: string) =>
    `ws://localhost:8000/api/v1/realtime/ws/${threadId}`,
};

// WebSocket helper
export class RealtimeWebSocket {
  private ws: WebSocket | null = null;
  private threadId: string;
  private onEvent?: (event: any) => void;
  private onError?: (error: Event) => void;

  constructor(threadId: string) {
    this.threadId = threadId;
  }

  connect(onEvent: (event: any) => void, onError?: (error: Event) => void) {
    this.onEvent = onEvent;
    this.onError = onError;

    const url = realtimeApi.getWebSocketUrl(this.threadId);
    this.ws = new WebSocket(url);

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (this.onEvent) {
        this.onEvent(data);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (this.onError) {
        this.onError(error);
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket closed');
    };
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export default apiClient;
