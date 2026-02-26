import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';
import { offlineApi } from '../services/api';
import { ArrowLeft, Clock, DollarSign, Layers } from 'lucide-react';

interface TraceData {
  trace: any;
  summary: any;
  checkpoints: any[];
}

export const TraceViewer: React.FC = () => {
  const { threadId, checkpointId } = useParams<{ threadId: string; checkpointId: string }>();
  const navigate = useNavigate();
  const { t } = useLanguage();
  const [traceData, setTraceData] = useState<TraceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [includeBlobs, setIncludeBlobs] = useState(false);

  useEffect(() => {
    if (threadId && checkpointId) {
      loadTrace();
    }
  }, [threadId, checkpointId, includeBlobs]);

  const loadTrace = async () => {
    if (!threadId || !checkpointId) return;

    try {
      setLoading(true);
      setError(null);
      const response = await offlineApi.getTrace(threadId, checkpointId, includeBlobs);
      setTraceData(response.data);
    } catch (err: any) {
      setError(err.message || 'Failed to load trace');
    } finally {
      setLoading(false);
    }
  };

  const renderTraceNode = (node: any, depth = 0): React.ReactNode => {
    if (!node) return null;

    return (
      <div key={node.id || Math.random()} className="trace-node" style={{ marginLeft: depth * 20 }}>
        <div className="node-header">
          <span className="node-type">{node.type || 'unknown'}</span>
          {node.id && <span className="node-id">{node.id}</span>}
        </div>
        {node.data && (
          <div className="node-data">
            <pre>{JSON.stringify(node.data, null, 2)}</pre>
          </div>
        )}
        {node.children && node.children.length > 0 && (
          <div className="node-children">
            {node.children.map((child: any) => renderTraceNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="trace-viewer">
        <div className="loading">{t('traceViewer.loading')}</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="trace-viewer">
        <div className="error">
          <p>{t('traceViewer.error')}: {error}</p>
          <button onClick={loadTrace}>{t('traceViewer.retry')}</button>
          <button onClick={() => navigate('/threads')}>{t('traceViewer.backToThreads')}</button>
        </div>
      </div>
    );
  }

  if (!traceData) {
    return (
      <div className="trace-viewer">
        <div className="empty-state">{t('traceViewer.noData')}</div>
      </div>
    );
  }

  return (
    <div className="trace-viewer">
      <div className="page-header">
        <button onClick={() => navigate('/threads')} className="back-btn">
          <ArrowLeft size={20} />
          {t('traceViewer.back')}
        </button>
        <div>
          <h1>{t('traceViewer.title')}</h1>
          <p className="thread-info">
            {t('traceViewer.thread')}: <code>{threadId}</code> | {t('traceViewer.checkpoint')}: <code>{checkpointId}</code>
          </p>
        </div>
        <div className="header-actions">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={includeBlobs}
              onChange={(e) => setIncludeBlobs(e.target.checked)}
            />
            {t('traceViewer.includeBlobs')}
          </label>
          <button onClick={loadTrace} className="btn-secondary">
            {t('traceViewer.refresh')}
          </button>
        </div>
      </div>

      <div className="trace-summary">
        <div className="summary-card">
          <div className="summary-icon">
            <Layers size={20} />
          </div>
          <div className="summary-content">
            <div className="summary-value">{traceData.summary.total_steps || 0}</div>
            <div className="summary-label">{t('traceViewer.stats.totalSteps')}</div>
          </div>
        </div>

        {traceData.summary.total_tokens && (
          <div className="summary-card">
            <div className="summary-icon">
              <Clock size={20} />
            </div>
            <div className="summary-content">
              <div className="summary-value">{traceData.summary.total_tokens}</div>
              <div className="summary-label">{t('traceViewer.stats.tokens')}</div>
            </div>
          </div>
        )}

        {traceData.summary.total_cost && (
          <div className="summary-card">
            <div className="summary-icon">
              <DollarSign size={20} />
            </div>
            <div className="summary-content">
              <div className="summary-value">${traceData.summary.total_cost.toFixed(4)}</div>
              <div className="summary-label">{t('traceViewer.stats.cost')}</div>
            </div>
          </div>
        )}

        {traceData.summary.execution_time && (
          <div className="summary-card">
            <div className="summary-icon">
              <Clock size={20} />
            </div>
            <div className="summary-content">
              <div className="summary-value">{traceData.summary.execution_time.toFixed(2)}s</div>
              <div className="summary-label">{t('traceViewer.stats.executionTime')}</div>
            </div>
          </div>
        )}
      </div>

      <div className="trace-content">
        <div className="trace-section">
          <h2>{t('traceViewer.executionTrace')}</h2>
          <div className="trace-graph">{renderTraceNode(traceData.trace)}</div>
        </div>

        {traceData.checkpoints && traceData.checkpoints.length > 0 && (
          <div className="checkpoint-chain">
            <h2>{t('traceViewer.checkpointChain')}</h2>
            <div className="checkpoint-list">
              {traceData.checkpoints.map((cp: any, idx: number) => (
                <div key={cp.checkpoint_id} className="checkpoint-item">
                  <div className="checkpoint-number">{idx + 1}</div>
                  <div className="checkpoint-details">
                    <div className="checkpoint-id">{cp.checkpoint_id}</div>
                    {cp.parent_checkpoint_id && (
                      <div className="checkpoint-parent">
                        {t('traceViewer.parent')}: {cp.parent_checkpoint_id}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="trace-raw">
        <h2>{t('traceViewer.rawData')}</h2>
        <details>
          <summary>{t('traceViewer.viewJson')}</summary>
          <pre>{JSON.stringify(traceData, null, 2)}</pre>
        </details>
      </div>
    </div>
  );
};

export default TraceViewer;
