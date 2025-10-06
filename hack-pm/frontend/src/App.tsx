import React from 'react';
import './App.css';

function App() {
  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc', padding: '20px' }}>
      <header style={{ backgroundColor: '#1e293b', color: 'white', padding: '1rem', marginBottom: '2rem', borderRadius: '8px' }}>
        <h1>Hack PM - ハッカソンプロジェクト管理システム</h1>
        <p>チーム開発を効率化するプロジェクト管理ツール</p>
      </header>
      
      <main style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <Dashboard />
      </main>
    </div>
  );
}

const Dashboard = () => (
  <div style={{ backgroundColor: 'white', padding: '2rem', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
    <h2>ダッシュボード</h2>
    <p>ハッカソンプロジェクトの進捗を管理します。</p>
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginTop: '2rem' }}>
      <div style={{ backgroundColor: '#dbeafe', padding: '1rem', borderRadius: '8px' }}>
        <h3>総機能数</h3>
        <p style={{ fontSize: '2rem', margin: '0.5rem 0' }}>12</p>
      </div>
      <div style={{ backgroundColor: '#dcfce7', padding: '1rem', borderRadius: '8px' }}>
        <h3>完了機能</h3>
        <p style={{ fontSize: '2rem', margin: '0.5rem 0' }}>8</p>
      </div>
      <div style={{ backgroundColor: '#fef3c7', padding: '1rem', borderRadius: '8px' }}>
        <h3>進行中</h3>
        <p style={{ fontSize: '2rem', margin: '0.5rem 0' }}>4</p>
      </div>
    </div>
    
    <div style={{ marginTop: '2rem', backgroundColor: '#f1f5f9', padding: '1.5rem', borderRadius: '8px' }}>
      <h3>技術スタック</h3>
      <ul>
        <li>React (TypeScript)</li>
        <li>Go (Gin)</li>
        <li>Python (FastAPI)</li>
        <li>PostgreSQL</li>
        <li>Docker</li>
      </ul>
    </div>
  </div>
);

export default App;