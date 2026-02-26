import React, { useEffect, useState, useRef } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { realtimeApi, RealtimeWebSocket } from '../services/api';
import { Radio, Trash2, Download, RefreshCw } from 'lucide-react';

interface RealtimeEvent {
  event_type: string;
  timestamp: number;
  data: any;
  metadata?: any;
}

interface Summary {
  thread_id: string;
  event_count: number;
  first_event_time?: number;
  last_event_time?: number;
  event_types: Record<string, number>;
}

export const RealtimeMonitor: React.FC = () => {
  const { t } = useLanguage();
  const [activeThreads, setActiveThreads] = useState<string[]>([]);
  const [selectedThread, setSelectedThread] = useState<string | null>(null);
  const [events, setEvents] = useState<RealtimeEvent[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<RealtimeWebSocket | null>(null);
  const eventsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadActiveThreads();
    const interval = setInterval(loadActiveThreads, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedThread) {
      connectToThread(selectedThread);
      loadThreadData(selectedThread);
    }
    return () => {
      if (wsRef.current) {
        wsRef.current.disconnect();
      }
    };
  }, [selectedThread]);

  useEffect(() => {
    eventsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [events]);

  const loadActiveThreads = async () => {
    try {
      const response = await realtimeApi.listActiveThreads();
      setActiveThreads(response.data.threads);
      setLoading(false);
    } catch (err: any) {
      setError(err.message || 'Failed to load active threads');
      setLoading(false);
    }
  };

  const loadThreadData = async (threadId: string) => {
    try {
      const [eventsRes, summaryRes] = await Promise.all([
        realtimeApi.getThreadEvents(threadId, { limit: 100 }),
        realtimeApi.getThreadSummary(threadId),
      ]);
      setEvents(eventsRes.data.events);
      setSummary(summaryRes.data);
    } catch (err: any) {
      console.error('Failed to load thread data:', err);
    }
  };

  const connectToThread = (threadId: string) => {
    if (wsRef.current) {
      wsRef.current.disconnect();
    }

    const ws = new RealtimeWebSocket(threadId);
    ws.connect(
      (message) => {
        if (message.type === 'event') {
          setEvents((prev) => [...prev, message.data]);
        } else if (message.type === 'buffered_events') {
          setEvents((prev) => [...prev, ...message.events]);
        } else if (message.type === 'connection') {
          setConnected(true);
        }
      },
      (error) => {
        console.error('WebSocket error:', error);
        setConnected(false);
      }
    );

    wsRef.current = ws;
  };

  const handleClearEvents = async () => {
    if (!selectedThread) return;
    try {
      await realtimeApi.clearThreadEvents(selectedThread);
      setEvents([]);
      setSummary(null);
    } catch (err: any) {
      alert('Failed to clear events: ' + err.message);
    }
  };

  const handleExport = async () => {
    if (!selectedThread) return;
    try {
      const response = await realtimeApi.exportThreadEvents(selectedThread, 'json');
      const blob = new Blob([response.data.data], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${selectedThread}-events.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err: any) {
      alert('Failed to export events: ' + err.message);
    }
  };

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleTimeString();
  };

  if (loading) {
    return (
      <div className="realtime-monitor">
        <div className="loading">{t('realtime.loading')}</div>
      </div>
    );
  }

  return (
    <div className="realtime-monitor">
      <div className="page-header">
        <div>
          <h1>{t('realtime.title')}</h1>
          <p>{t('realtime.subtitle')}</p>
        </div>
        <div className="connection-status">
          <div className={`status-indicator ${connected ? 'connected' : 'disconnected'}`} />
          <span>{connected ? t('realtime.connected') : t('realtime.disconnected')}</span>
        </div>
      </div>

      <div className="monitor-layout">
        <div className="thread-selector">
          <div className="selector-header">
            <h2>{t('realtime.activeThreads')}</h2>
            <button onClick={loadActiveThreads} className="icon-btn" title={t('realtime.refresh')}>
              <RefreshCw size={16} />
            </button>
          </div>

          {activeThreads.length === 0 ? (
            <div className="empty-state">
              <p>{t('realtime.noActiveThreads')}</p>
              <p className="hint">{t('realtime.hint')}</p>
            </div>
          ) : (
            <div className="thread-list">
              {activeThreads.map((threadId) => (
                <div
                  key={threadId}
                  className={`thread-item ${selectedThread === threadId ? 'selected' : ''}`}
                  onClick={() => setSelectedThread(threadId)}
                >
                  <Radio size={16} className={selectedThread === threadId ? 'active' : ''} />
                  <span className="thread-id">{threadId}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="event-viewer">
          {!selectedThread ? (
            <div className="empty-state">
              <p>{t('realtime.selectThread')}</p>
            </div>
          ) : (
            <>
              <div className="viewer-header">
                <h2>{t('realtime.events')}: {selectedThread}</h2>
                <div className="viewer-actions">
                  <button onClick={handleExport} className="btn-secondary" title={t('realtime.export')}>
                    <Download size={16} />
                    {t('realtime.export')}
                  </button>
                  <button onClick={handleClearEvents} className="btn-danger" title={t('realtime.clear')}>
                    <Trash2 size={16} />
                    {t('realtime.clear')}
                  </button>
                </div>
              </div>

              {summary && (
                <div className="event-summary">
                  <div className="summary-item">
                    <span className="label">{t('realtime.totalEvents')}:</span>
                    <span className="value">{summary.event_count}</span>
                  </div>
                  {Object.entries(summary.event_types).map(([type, count]) => (
                    <div key={type} className="summary-item">
                      <span className="label">{type}:</span>
                      <span className="value">{count}</span>
                    </div>
                  ))}
                </div>
              )}

              <div className="events-container">
                {events.length === 0 ? (
                  <div className="empty-state">
                    <p>{t('realtime.noEvents')}</p>
                  </div>
                ) : (
                  <div className="events-list">
                    {events.map((event, idx) => (
                      <div key={idx} className="event-item">
                        <div className="event-header">
                          <span className="event-type">{event.event_type}</span>
                          <span className="event-time">{formatTimestamp(event.timestamp)}</span>
                        </div>
                        <div className="event-data">
                          <pre>{JSON.stringify(event.data, null, 2)}</pre>
                        </div>
                        {event.metadata && (
                          <div className="event-metadata">
                            <details>
                              <summary>{t('realtime.metadata')}</summary>
                              <pre>{JSON.stringify(event.metadata, null, 2)}</pre>
                            </details>
                          </div>
                        )}
                      </div>
                    ))}
                    <div ref={eventsEndRef} />
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default RealtimeMonitor;
