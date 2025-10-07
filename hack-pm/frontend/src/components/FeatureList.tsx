import React, { useState } from 'react';

interface Feature {
  id: number;
  name: string;
  description: string;
  status: 'todo' | 'in-progress' | 'review' | 'done';
  priority: 'low' | 'medium' | 'high' | 'critical';
  assignee: string;
  estimatedHours: number;
  actualHours?: number;
  startDate: string;
  endDate: string;
}

const FeatureList: React.FC = () => {
  const [features] = useState<Feature[]>([
    {
      id: 1,
      name: 'ユーザー認証システム',
      description: 'JWT認証を使用したログイン・ログアウト機能',
      status: 'done',
      priority: 'high',
      assignee: '田中',
      estimatedHours: 16,
      actualHours: 18,
      startDate: '2024-01-15',
      endDate: '2024-01-20'
    },
    {
      id: 2,
      name: 'ダッシュボード画面',
      description: 'プロジェクト統計を表示するダッシュボード',
      status: 'in-progress',
      priority: 'medium',
      assignee: '佐藤',
      estimatedHours: 12,
      startDate: '2024-01-18',
      endDate: '2024-01-25'
    },
    {
      id: 3,
      name: 'API設計・実装',
      description: 'RESTful APIの設計と実装',
      status: 'review',
      priority: 'high',
      assignee: '鈴木',
      estimatedHours: 20,
      actualHours: 22,
      startDate: '2024-01-16',
      endDate: '2024-01-24'
    },
    {
      id: 4,
      name: 'データベース設計',
      description: 'PostgreSQLを使用したデータベース設計',
      status: 'todo',
      priority: 'critical',
      assignee: '高橋',
      estimatedHours: 8,
      startDate: '2024-01-22',
      endDate: '2024-01-26'
    },
    {
      id: 5,
      name: 'フロントエンド実装',
      description: 'Reactを使用したUI実装',
      status: 'in-progress',
      priority: 'medium',
      assignee: '山田',
      estimatedHours: 24,
      startDate: '2024-01-20',
      endDate: '2024-01-30'
    }
  ]);

  const [filterStatus, setFilterStatus] = useState<string>('all');

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'todo': return { bg: '#374151', text: '#fbbf24', border: '#f59e0b' };
      case 'in-progress': return { bg: '#1e3a8a', text: '#60a5fa', border: '#3b82f6' };
      case 'review': return { bg: '#451a03', text: '#fbbf24', border: '#f59e0b' };
      case 'done': return { bg: '#064e3b', text: '#34d399', border: '#10b981' };
      default: return { bg: '#374151', text: '#9ca3af', border: '#6b7280' };
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'todo': return '未着手';
      case 'in-progress': return '進行中';
      case 'review': return 'レビュー';
      case 'done': return '完了';
      default: return status;
    }
  };

  const filteredFeatures = filterStatus === 'all' 
    ? features 
    : features.filter(f => f.status === filterStatus);

  const statusCounts = {
    all: features.length,
    todo: features.filter(f => f.status === 'todo').length,
    'in-progress': features.filter(f => f.status === 'in-progress').length,
    review: features.filter(f => f.status === 'review').length,
    done: features.filter(f => f.status === 'done').length,
  };

  return (
    <div style={{ 
      padding: '0',
      background: 'linear-gradient(135deg, #000000 0%, #1a1a1a 100%)',
      minHeight: '100vh'
    }}>
      {/* Hero Section */}
      <section style={{ 
        padding: '8rem 2rem 4rem 2rem', 
        textAlign: 'center',
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        <h1 style={{ 
          fontSize: '3.5rem', 
          fontWeight: '700', 
          color: '#ffffff', 
          marginBottom: '1rem',
          letterSpacing: '-0.02em',
          lineHeight: '1.1'
        }}>
          機能開発を
          <br />
          <span style={{ 
            background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            効率的に管理
          </span>
        </h1>
        <p style={{ 
          color: '#a1a1aa', 
          margin: '0 auto 3rem auto',
          fontSize: '1.2rem',
          maxWidth: '600px',
          lineHeight: '1.6'
        }}>
          プロジェクトの機能開発を美しく、直感的に追跡。
          チームの生産性を最大化します。
        </p>
      </section>

      {/* Filter Section */}
      <section style={{ 
        padding: '0 2rem 4rem 2rem',
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        <div style={{ 
          display: 'flex', 
          gap: '0.75rem', 
          marginBottom: '3rem',
          flexWrap: 'wrap',
          justifyContent: 'center'
        }}>
          {Object.entries(statusCounts).map(([status, count]) => (
            <button
              key={status}
              onClick={() => setFilterStatus(status)}
              style={{
                padding: '0.75rem 1.5rem',
                borderRadius: '2rem',
                border: 'none',
                background: filterStatus === status 
                  ? 'rgba(255, 255, 255, 0.2)' 
                  : 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(10px)',
                color: filterStatus === status ? '#ffffff' : '#a1a1aa',
                cursor: 'pointer',
                fontSize: '0.95rem',
                fontWeight: '500',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                if (filterStatus !== status) {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.15)';
                  e.currentTarget.style.color = '#ffffff';
                }
              }}
              onMouseLeave={(e) => {
                if (filterStatus !== status) {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
                  e.currentTarget.style.color = '#a1a1aa';
                }
              }}
            >
              {status === 'all' ? '全て' : 
               status === 'todo' ? '未着手' :
               status === 'in-progress' ? '進行中' :
               status === 'review' ? 'レビュー' : '完了'} ({count})
            </button>
          ))}
        </div>

        {/* Features Table */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(20px)',
          borderRadius: '1.5rem',
          overflow: 'hidden',
          border: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ 
                  background: 'rgba(255, 255, 255, 0.1)', 
                  borderBottom: '1px solid rgba(255, 255, 255, 0.1)' 
                }}>
                  <th style={{ 
                    padding: '1.5rem 1rem', 
                    textAlign: 'left', 
                    fontWeight: '600', 
                    color: '#ffffff',
                    fontSize: '0.95rem'
                  }}>機能名</th>
                  <th style={{ 
                    padding: '1.5rem 1rem', 
                    textAlign: 'left', 
                    fontWeight: '600', 
                    color: '#ffffff',
                    fontSize: '0.95rem'
                  }}>ステータス</th>
                  <th style={{ 
                    padding: '1.5rem 1rem', 
                    textAlign: 'left', 
                    fontWeight: '600', 
                    color: '#ffffff',
                    fontSize: '0.95rem'
                  }}>担当者</th>
                  <th style={{ 
                    padding: '1.5rem 1rem', 
                    textAlign: 'left', 
                    fontWeight: '600', 
                    color: '#ffffff',
                    fontSize: '0.95rem'
                  }}>期間</th>
                </tr>
              </thead>
              <tbody>
                {filteredFeatures.map((feature, index) => {
                  const statusColor = getStatusColor(feature.status);
                  return (
                    <tr 
                      key={feature.id}
                      style={{ 
                        borderBottom: index < filteredFeatures.length - 1 ? '1px solid rgba(255, 255, 255, 0.1)' : 'none',
                        transition: 'background-color 0.3s ease'
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.05)'}
                      onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                    >
                      <td style={{ padding: '1.5rem 1rem' }}>
                        <div>
                          <div style={{ 
                            fontWeight: '600', 
                            color: '#ffffff', 
                            marginBottom: '0.5rem',
                            fontSize: '1rem'
                          }}>
                            {feature.name}
                          </div>
                          <div style={{ 
                            fontSize: '0.9rem', 
                            color: '#a1a1aa',
                            lineHeight: '1.5'
                          }}>
                            {feature.description}
                          </div>
                        </div>
                      </td>
                      <td style={{ padding: '1.5rem 1rem' }}>
                        <span style={{
                          padding: '0.5rem 1rem',
                          borderRadius: '2rem',
                          fontSize: '0.85rem',
                          fontWeight: '500',
                          backgroundColor: statusColor.bg,
                          color: statusColor.text,
                          border: `1px solid ${statusColor.border}`
                        }}>
                          {getStatusText(feature.status)}
                        </span>
                      </td>
                      <td style={{ padding: '1.5rem 1rem' }}>
                        <span style={{ color: '#ffffff', fontWeight: '500' }}>
                          {feature.assignee}
                        </span>
                      </td>
                      <td style={{ padding: '1.5rem 1rem' }}>
                        <div style={{ color: '#a1a1aa', fontSize: '0.9rem' }}>
                          {feature.startDate} - {feature.endDate}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>
  );
};

export default FeatureList;