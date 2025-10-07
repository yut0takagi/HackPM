import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import FeatureList from './components/FeatureList';
import GanttChart from './components/GanttChart';
import TeamPage from './components/TeamPage';

// Dashboard Component
const Dashboard: React.FC = () => {
  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', color: '#1f2937', marginBottom: '0.5rem' }}>
          ダッシュボード
        </h1>
        <p style={{ color: '#6b7280', margin: 0 }}>
          ハッカソンプロジェクトの進捗を一目で確認
        </p>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '1.5rem',
        marginBottom: '2rem'
      }}>
        <div style={{
          backgroundColor: 'white',
          padding: '2rem',
          borderRadius: '0.75rem',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
          border: '1px solid #e5e7eb',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>📊</div>
          <h3 style={{ margin: '0 0 0.5rem 0', color: '#1f2937' }}>総機能数</h3>
          <p style={{ fontSize: '3rem', margin: '0.5rem 0', fontWeight: 'bold', color: '#3b82f6' }}>12</p>
        </div>
        <div style={{
          backgroundColor: 'white',
          padding: '2rem',
          borderRadius: '0.75rem',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
          border: '1px solid #e5e7eb',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>✅</div>
          <h3 style={{ margin: '0 0 0.5rem 0', color: '#1f2937' }}>完了機能</h3>
          <p style={{ fontSize: '3rem', margin: '0.5rem 0', fontWeight: 'bold', color: '#10b981' }}>8</p>
        </div>
        <div style={{
          backgroundColor: 'white',
          padding: '2rem',
          borderRadius: '0.75rem',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
          border: '1px solid #e5e7eb',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>⏳</div>
          <h3 style={{ margin: '0 0 0.5rem 0', color: '#1f2937' }}>進行中</h3>
          <p style={{ fontSize: '3rem', margin: '0.5rem 0', fontWeight: 'bold', color: '#f59e0b' }}>4</p>
        </div>
        <div style={{
          backgroundColor: 'white',
          padding: '2rem',
          borderRadius: '0.75rem',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
          border: '1px solid #e5e7eb',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>👥</div>
          <h3 style={{ margin: '0 0 0.5rem 0', color: '#1f2937' }}>チームメンバー</h3>
          <p style={{ fontSize: '3rem', margin: '0.5rem 0', fontWeight: 'bold', color: '#8b5cf6' }}>5</p>
        </div>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '1.5rem'
      }}>
        <div style={{
          backgroundColor: 'white',
          padding: '1.5rem',
          borderRadius: '0.75rem',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
          border: '1px solid #e5e7eb'
        }}>
          <h3 style={{ marginTop: 0, color: '#1f2937', marginBottom: '1rem' }}>技術スタック</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {['React', 'TypeScript', 'Go', 'Python', 'PostgreSQL', 'Docker'].map((tech) => (
              <span key={tech} style={{
                padding: '0.5rem 1rem',
                backgroundColor: '#f3f4f6',
                color: '#374151',
                borderRadius: '9999px',
                fontSize: '0.875rem',
                fontWeight: '500'
              }}>
                {tech}
              </span>
            ))}
          </div>
        </div>

        <div style={{
          backgroundColor: 'white',
          padding: '1.5rem',
          borderRadius: '0.75rem',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
          border: '1px solid #e5e7eb'
        }}>
          <h3 style={{ marginTop: 0, color: '#1f2937', marginBottom: '1rem' }}>システム状況</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {[
              { name: 'フロントエンド', status: '✅ 起動中' },
              { name: 'Go API', status: '✅ 起動中' },
              { name: 'Python API', status: '✅ 起動中' },
              { name: 'データベース', status: '✅ 接続済み' }
            ].map((service) => (
              <div key={service.name} style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#374151', fontWeight: '500' }}>{service.name}:</span>
                <span style={{ color: '#10b981' }}>{service.status}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <Router>
      <div style={{
        minHeight: '100vh',
        backgroundColor: '#f8fafc',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif'
      }}>
        <Navbar />
        <main>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/features" element={<FeatureList />} />
            <Route path="/gantt" element={<GanttChart />} />
            <Route path="/team" element={<TeamPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;