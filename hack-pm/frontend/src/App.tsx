import React from 'react';

function App() {
  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#f8fafc', 
      padding: '20px',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif'
    }}>
      <header style={{ 
        backgroundColor: '#1e293b', 
        color: 'white', 
        padding: '2rem', 
        marginBottom: '2rem', 
        borderRadius: '8px',
        textAlign: 'center'
      }}>
        <h1 style={{ margin: '0 0 1rem 0', fontSize: '2.5rem' }}>
          Hack PM
        </h1>
        <p style={{ margin: 0, fontSize: '1.2rem', opacity: 0.9 }}>
          ハッカソンプロジェクト管理システム
        </p>
      </header>
      
      <main style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ 
          backgroundColor: 'white', 
          padding: '2rem', 
          borderRadius: '8px', 
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)' 
        }}>
          <h2 style={{ marginTop: 0 }}>ダッシュボード</h2>
          <p>ハッカソンプロジェクトの進捗を管理します。</p>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '1rem', 
            marginTop: '2rem' 
          }}>
            <div style={{ 
              backgroundColor: '#dbeafe', 
              padding: '1.5rem', 
              borderRadius: '8px',
              textAlign: 'center'
            }}>
              <h3 style={{ margin: '0 0 0.5rem 0' }}>総機能数</h3>
              <p style={{ fontSize: '3rem', margin: '0.5rem 0', fontWeight: 'bold', color: '#1e40af' }}>12</p>
            </div>
            <div style={{ 
              backgroundColor: '#dcfce7', 
              padding: '1.5rem', 
              borderRadius: '8px',
              textAlign: 'center'
            }}>
              <h3 style={{ margin: '0 0 0.5rem 0' }}>完了機能</h3>
              <p style={{ fontSize: '3rem', margin: '0.5rem 0', fontWeight: 'bold', color: '#166534' }}>8</p>
            </div>
            <div style={{ 
              backgroundColor: '#fef3c7', 
              padding: '1.5rem', 
              borderRadius: '8px',
              textAlign: 'center'
            }}>
              <h3 style={{ margin: '0 0 0.5rem 0' }}>進行中</h3>
              <p style={{ fontSize: '3rem', margin: '0.5rem 0', fontWeight: 'bold', color: '#a16207' }}>4</p>
            </div>
          </div>
          
          <div style={{ 
            marginTop: '2rem', 
            backgroundColor: '#f1f5f9', 
            padding: '1.5rem', 
            borderRadius: '8px' 
          }}>
            <h3 style={{ marginTop: 0 }}>技術スタック</h3>
            <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
              <li style={{ marginBottom: '0.5rem' }}>React (TypeScript)</li>
              <li style={{ marginBottom: '0.5rem' }}>Go (Gin)</li>
              <li style={{ marginBottom: '0.5rem' }}>Python (FastAPI)</li>
              <li style={{ marginBottom: '0.5rem' }}>PostgreSQL</li>
              <li style={{ marginBottom: '0.5rem' }}>Docker</li>
            </ul>
          </div>

          <div style={{ 
            marginTop: '2rem', 
            padding: '1.5rem', 
            backgroundColor: '#f0f9ff',
            borderRadius: '8px',
            border: '1px solid #0ea5e9'
          }}>
            <h3 style={{ marginTop: 0, color: '#0c4a6e' }}>システム状況</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <p><strong>フロントエンド:</strong> ✅ 起動中</p>
                <p><strong>Go API:</strong> ✅ 起動中</p>
              </div>
              <div>
                <p><strong>Python API:</strong> ✅ 起動中</p>
                <p><strong>データベース:</strong> ✅ 接続済み</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;