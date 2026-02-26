import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';
import { offlineApi } from '../services/api';
import { Search, ChevronLeft, ChevronRight } from 'lucide-react';

interface Thread {
  thread_id: string;
  checkpoint_count: number;
  latest_checkpoint_id: string;
}

export const ThreadList: React.FC = () => {
  const navigate = useNavigate();
  const { t } = useLanguage();
  const [threads, setThreads] = useState<Thread[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [limit] = useState(20);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadThreads();
  }, [page]);

  const loadThreads = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await offlineApi.listThreads({
        limit,
        offset: page * limit,
      });
      setThreads(response.data.threads);
      setTotal(response.data.total);
    } catch (err: any) {
      setError(err.message || 'Failed to load threads');
    } finally {
      setLoading(false);
    }
  };

  const filteredThreads = threads.filter((thread) =>
    thread.thread_id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="thread-list-page">
      <div className="page-header">
        <div>
          <h1>{t('threadList.title')}</h1>
          <p>{t('threadList.subtitle')}</p>
        </div>
        <button onClick={loadThreads} className="btn-primary">
          {t('threadList.refresh')}
        </button>
      </div>

      <div className="search-bar">
        <Search size={20} />
        <input
          type="text"
          placeholder={t('threadList.search')}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {loading ? (
        <div className="loading">{t('common.loading')}</div>
      ) : error ? (
        <div className="error">
          <p>{t('common.error')}: {error}</p>
          <button onClick={loadThreads}>{t('common.retry')}</button>
        </div>
      ) : filteredThreads.length === 0 ? (
        <div className="empty-state">
          <p>
            {searchTerm
              ? t('threadList.noMatch')
              : t('threadList.noThreads')}
          </p>
        </div>
      ) : (
        <>
          <div className="threads-table">
            <div className="table-header">
              <div className="col-thread-id">{t('threadList.tableHeaders.threadId')}</div>
              <div className="col-checkpoints">{t('threadList.tableHeaders.checkpoints')}</div>
              <div className="col-latest">{t('threadList.tableHeaders.latestCheckpoint')}</div>
              <div className="col-actions">{t('threadList.tableHeaders.actions')}</div>
            </div>
            {filteredThreads.map((thread) => (
              <div key={thread.thread_id} className="table-row">
                <div className="col-thread-id">
                  <span className="thread-id-text">{thread.thread_id}</span>
                </div>
                <div className="col-checkpoints">
                  <span className="badge">{thread.checkpoint_count}</span>
                </div>
                <div className="col-latest">
                  <span className="checkpoint-id">{thread.latest_checkpoint_id}</span>
                </div>
                <div className="col-actions">
                  <button
                    onClick={() =>
                      navigate(`/trace/${thread.thread_id}/${thread.latest_checkpoint_id}`)
                    }
                    className="btn-secondary"
                  >
                    {t('threadList.viewTrace')}
                  </button>
                  <button
                    onClick={() => navigate(`/threads/${thread.thread_id}`)}
                    className="btn-secondary"
                  >
                    {t('threadList.details')}
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="pagination">
            <button
              onClick={() => setPage(page - 1)}
              disabled={page === 0}
              className="pagination-btn"
            >
              <ChevronLeft size={20} />
              {t('threadList.pagination.previous')}
            </button>
            <span className="pagination-info">
              {t('threadList.pagination.page')} {page + 1} {t('threadList.pagination.of')} {totalPages} ({total} {t('threadList.pagination.total')})
            </span>
            <button
              onClick={() => setPage(page + 1)}
              disabled={page >= totalPages - 1}
              className="pagination-btn"
            >
              {t('threadList.pagination.next')}
              <ChevronRight size={20} />
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default ThreadList;
