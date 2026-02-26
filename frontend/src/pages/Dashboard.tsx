import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';
import { offlineApi, realtimeApi } from '../services/api';
import { Activity, Database, Zap, TrendingUp } from 'lucide-react';

interface Stats {
  totalThreads: number;
  activeThreads: number;
  totalCheckpoints: number;
  databaseType: string;
}

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { t } = useLanguage();
  const [stats, setStats] = useState<Stats>({
    totalThreads: 0,
    activeThreads: 0,
    totalCheckpoints: 0,
    databaseType: 'unknown',
  });
  const [recentThreads, setRecentThreads] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [threadsRes, activeRes, dbInfo] = await Promise.all([
        offlineApi.listThreads({ limit: 10 }),
        realtimeApi.listActiveThreads().catch(() => ({ data: { threads: [], count: 0 } })),
        offlineApi.getDatabaseInfo().catch(() => ({ data: { database_type: 'unknown' } })),
      ]);

      const totalCheckpoints = threadsRes.data.threads.reduce(
        (sum: number, t: any) => sum + t.checkpoint_count,
        0
      );

      setStats({
        totalThreads: threadsRes.data.total,
        activeThreads: activeRes.data.count,
        totalCheckpoints,
        databaseType: dbInfo.data.database_type || 'unknown',
      });

      setRecentThreads(threadsRes.data.threads);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard">
        <div className="loading">{t('common.loading')}</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard">
        <div className="error">
          <p>{t('common.error')}: {error}</p>
          <button onClick={loadDashboardData}>{t('common.retry')}</button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>{t('dashboard.title')}</h1>
        <p>{t('dashboard.subtitle')}</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">
            <Activity size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{stats.totalThreads}</div>
            <div className="stat-label">{t('dashboard.stats.totalThreads')}</div>
          </div>
        </div>

        <div className="stat-card active">
          <div className="stat-icon">
            <Zap size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{stats.activeThreads}</div>
            <div className="stat-label">{t('dashboard.stats.activeThreads')}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <TrendingUp size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{stats.totalCheckpoints}</div>
            <div className="stat-label">{t('dashboard.stats.checkpoints')}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <Database size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{stats.databaseType}</div>
            <div className="stat-label">{t('dashboard.stats.database')}</div>
          </div>
        </div>
      </div>

      <div className="recent-threads">
        <div className="section-header">
          <h2>{t('dashboard.recentThreads')}</h2>
          <button onClick={() => navigate('/threads')} className="view-all-btn">
            {t('dashboard.viewAll')}
          </button>
        </div>

        {recentThreads.length === 0 ? (
          <div className="empty-state">
            <p>{t('dashboard.noThreads')}</p>
          </div>
        ) : (
          <div className="thread-list">
            {recentThreads.map((thread) => (
              <div
                key={thread.thread_id}
                className="thread-item"
                onClick={() => navigate(`/threads/${thread.thread_id}`)}
              >
                <div className="thread-info">
                  <div className="thread-id">{thread.thread_id}</div>
                  <div className="thread-meta">
                    {thread.checkpoint_count} {t('dashboard.checkpointsCount')}
                  </div>
                </div>
                <div className="thread-actions">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/trace/${thread.thread_id}/${thread.latest_checkpoint_id}`);
                    }}
                    className="btn-secondary"
                  >
                    {t('dashboard.viewTrace')}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
