import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';

// Placeholder components
const Dashboard = () => (
  <div className="page">
    <h1>Dashboard</h1>
    <p>Overview of all threads and recent activity</p>
  </div>
);

const ThreadList = () => (
  <div className="page">
    <h1>Threads</h1>
    <p>List of all execution threads</p>
  </div>
);

const TraceViewer = () => (
  <div className="page">
    <h1>Trace Viewer</h1>
    <p>Visualize execution traces</p>
  </div>
);

const RealtimeMonitor = () => (
  <div className="page">
    <h1>Real-time Monitor</h1>
    <p>Live tracking of running agents</p>
  </div>
);

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="sidebar">
          <div className="logo">
            <h2>🌸 FlintBloom</h2>
            <p className="subtitle">AI Observability</p>
          </div>
          <ul className="nav-links">
            <li><Link to="/">Dashboard</Link></li>
            <li><Link to="/threads">Threads</Link></li>
            <li><Link to="/trace">Trace Viewer</Link></li>
            <li><Link to="/realtime">Real-time</Link></li>
          </ul>
          <div className="nav-footer">
            <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">
              API Docs
            </a>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/threads" element={<ThreadList />} />
            <Route path="/trace" element={<TraceViewer />} />
            <Route path="/realtime" element={<RealtimeMonitor />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
