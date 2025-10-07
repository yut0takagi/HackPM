import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import FeatureList from './components/FeatureList';
import GanttChart from './components/GanttChart';
import TeamPage from './components/TeamPage';

// Dashboard Component
const Dashboard: React.FC = () => {
  return (
    <div style={{ 
      padding: '0', 
      maxWidth: '100%', 
      margin: '0 auto',
      background: 'linear-gradient(135deg, #000000 0%, #1a1a1a 100%)'
    }}>
      {/* Hero Section */}
      <section style={{ 
        padding: '8rem 2rem 6rem 2rem', 
        textAlign: 'center',
        background: 'radial-gradient(ellipse at center, rgba(59, 130, 246, 0.1) 0%, transparent 70%)'
      }}>
        <h1 style={{ 
          fontSize: '4rem', 
          fontWeight: '700', 
          color: '#ffffff', 
          marginBottom: '1.5rem',
          letterSpacing: '-0.02em',
          lineHeight: '1.1'
        }}>
          プロジェクトを
          <br />
          <span style={{ 
            background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            シンプルに管理
          </span>
        </h1>
        <p style={{ 
          color: '#a1a1aa', 
          margin: '0 auto',
          fontSize: '1.25rem',
          maxWidth: '600px',
          lineHeight: '1.6',
          fontWeight: '400'
        }}>
          ハッカソンプロジェクトの進捗を美しく、直感的に追跡。
          <br />
          チームの生産性を最大化します。
        </p>
      </section>

      {/* Stats Section */}
      <section style={{ 
        padding: '6rem 2rem',
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '2rem'
        }}>
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(20px)',
            padding: '3rem 2rem',
            borderRadius: '1.5rem',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            textAlign: 'center',
            transition: 'transform 0.3s ease, box-shadow 0.3s ease'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-8px)';
            e.currentTarget.style.boxShadow = '0 25px 50px -12px rgba(0, 0, 0, 0.5)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = 'none';
          }}>
            <div style={{ 
              fontSize: '4rem', 
              marginBottom: '1rem',
              background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>12</div>
            <h3 style={{ 
              margin: '0 0 0.5rem 0', 
              color: '#ffffff',
              fontSize: '1.25rem',
              fontWeight: '600'
            }}>総機能数</h3>
            <p style={{ 
              color: '#a1a1aa',
              fontSize: '0.95rem',
              margin: 0
            }}>開発予定の機能</p>
          </div>
          
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(20px)',
            padding: '3rem 2rem',
            borderRadius: '1.5rem',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            textAlign: 'center',
            transition: 'transform 0.3s ease, box-shadow 0.3s ease'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-8px)';
            e.currentTarget.style.boxShadow = '0 25px 50px -12px rgba(0, 0, 0, 0.5)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = 'none';
          }}>
            <div style={{ 
              fontSize: '4rem', 
              marginBottom: '1rem',
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>8</div>
            <h3 style={{ 
              margin: '0 0 0.5rem 0', 
              color: '#ffffff',
              fontSize: '1.25rem',
              fontWeight: '600'
            }}>完了機能</h3>
            <p style={{ 
              color: '#a1a1aa',
              fontSize: '0.95rem',
              margin: 0
            }}>リリース準備完了</p>
          </div>
          
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(20px)',
            padding: '3rem 2rem',
            borderRadius: '1.5rem',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            textAlign: 'center',
            transition: 'transform 0.3s ease, box-shadow 0.3s ease'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-8px)';
            e.currentTarget.style.boxShadow = '0 25px 50px -12px rgba(0, 0, 0, 0.5)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = 'none';
          }}>
            <div style={{ 
              fontSize: '4rem', 
              marginBottom: '1rem',
              background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>4</div>
            <h3 style={{ 
              margin: '0 0 0.5rem 0', 
              color: '#ffffff',
              fontSize: '1.25rem',
              fontWeight: '600'
            }}>進行中</h3>
            <p style={{ 
              color: '#a1a1aa',
              fontSize: '0.95rem',
              margin: 0
            }}>開発中の機能</p>
          </div>
          
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(20px)',
            padding: '3rem 2rem',
            borderRadius: '1.5rem',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            textAlign: 'center',
            transition: 'transform 0.3s ease, box-shadow 0.3s ease'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-8px)';
            e.currentTarget.style.boxShadow = '0 25px 50px -12px rgba(0, 0, 0, 0.5)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = 'none';
          }}>
            <div style={{ 
              fontSize: '4rem', 
              marginBottom: '1rem',
              background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>5</div>
            <h3 style={{ 
              margin: '0 0 0.5rem 0', 
              color: '#ffffff',
              fontSize: '1.25rem',
              fontWeight: '600'
            }}>チームメンバー</h3>
            <p style={{ 
              color: '#a1a1aa',
              fontSize: '0.95rem',
              margin: 0
            }}>アクティブな開発者</p>
          </div>
        </div>
      </section>

      {/* Technology & Status Section */}
      <section style={{ 
        padding: '6rem 2rem',
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '4rem',
          alignItems: 'start'
        }}>
          <div>
            <h2 style={{ 
              fontSize: '2.5rem', 
              fontWeight: '700', 
              color: '#ffffff', 
              marginBottom: '1.5rem',
              letterSpacing: '-0.02em'
            }}>
              最新技術で構築
            </h2>
            <p style={{ 
              color: '#a1a1aa', 
              fontSize: '1.1rem',
              lineHeight: '1.7',
              marginBottom: '2rem'
            }}>
              モダンな技術スタックを使用して、
              スケーラブルで保守性の高いアプリケーションを構築しています。
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
              {['React', 'TypeScript', 'Go', 'Python', 'PostgreSQL', 'Docker'].map((tech) => (
                <span key={tech} style={{
                  padding: '0.75rem 1.5rem',
                  background: 'rgba(255, 255, 255, 0.1)',
                  backdropFilter: 'blur(10px)',
                  color: '#ffffff',
                  borderRadius: '2rem',
                  fontSize: '0.95rem',
                  fontWeight: '500',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  transition: 'all 0.3s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}>
                  {tech}
                </span>
              ))}
            </div>
          </div>

          <div>
            <h2 style={{ 
              fontSize: '2.5rem', 
              fontWeight: '700', 
              color: '#ffffff', 
              marginBottom: '1.5rem',
              letterSpacing: '-0.02em'
            }}>
              システム状況
            </h2>
            <p style={{ 
              color: '#a1a1aa', 
              fontSize: '1.1rem',
              lineHeight: '1.7',
              marginBottom: '2rem'
            }}>
              全てのサービスが正常に稼働中。
              リアルタイムでシステムの健全性を監視しています。
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {[
                { name: 'フロントエンド', status: '稼働中', color: '#10b981' },
                { name: 'Go API', status: '稼働中', color: '#10b981' },
                { name: 'Python API', status: '稼働中', color: '#10b981' },
                { name: 'データベース', status: '接続済み', color: '#10b981' }
              ].map((service) => (
                <div key={service.name} style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '1rem 0',
                  borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
                }}>
                  <span style={{ 
                    color: '#ffffff', 
                    fontWeight: '500',
                    fontSize: '1.1rem'
                  }}>{service.name}</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <div style={{
                      width: '8px',
                      height: '8px',
                      borderRadius: '50%',
                      backgroundColor: service.color,
                      boxShadow: `0 0 10px ${service.color}`
                    }}></div>
                    <span style={{ color: service.color, fontWeight: '500' }}>
                      {service.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

function App() {
  return (
    <Router>
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #000000 0%, #1a1a1a 100%)',
        fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", "Roboto", sans-serif'
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