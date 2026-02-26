import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { LanguageProvider, useLanguage } from './contexts/LanguageContext';
import Logo from './components/Logo';
import LanguageSwitcher from './components/LanguageSwitcher';
import Dashboard from './pages/Dashboard';
import ThreadList from './pages/ThreadList';
import TraceViewer from './pages/TraceViewer';
import RealtimeMonitor from './pages/RealtimeMonitor';
import './App.css';

function AppContent() {
  const { t } = useLanguage();

  return (
    <Router>
      <div className="app">
        <nav className="sidebar">
          <div className="logo">
            <div className="logo-container">
              <Logo size={48} />
              <div className="logo-text">
                <h2>FlintBloom</h2>
                <p className="subtitle">{t('nav.dashboard').includes('Dashboard') ? 'AI Observability Platform' : 'AI 可观测性平台'}</p>
              </div>
            </div>
          </div>
          <ul className="nav-links">
            <li><Link to="/">{t('nav.dashboard')}</Link></li>
            <li><Link to="/threads">{t('nav.threads')}</Link></li>
            <li><Link to="/realtime">{t('nav.realtime')}</Link></li>
          </ul>
          <div className="nav-footer">
            <LanguageSwitcher />
            <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">
              {t('nav.apiDocs')}
            </a>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/threads" element={<ThreadList />} />
            <Route path="/threads/:threadId" element={<ThreadList />} />
            <Route path="/trace/:threadId/:checkpointId" element={<TraceViewer />} />
            <Route path="/realtime" element={<RealtimeMonitor />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

function App() {
  return (
    <LanguageProvider>
      <AppContent />
    </LanguageProvider>
  );
}

export default App;
