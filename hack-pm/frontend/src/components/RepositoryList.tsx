import React, { useState, useEffect } from 'react';
import { api, ApiError } from '../utils/api';

interface Repository {
  id: number;
  full_name: string;
  name: string;
  owner: string;
  description: string;
  html_url: string;
  default_branch: string;
  visibility: string;
  updated_at: string;
  stats: {
    branches: number;
    open_prs: number;
    open_issues: number;
    latest_ci_status: string | null;
    latest_ci_conclusion: string | null;
  };
}

const RepositoryList: React.FC = () => {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRepositories();
  }, []);

  const fetchRepositories = async () => {
    try {
      setError(null);
      const data = await api.getRepositories();
      setRepositories(data);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(`API Error (${err.status}): ${err.message}`);
      } else {
        setError(err instanceof Error ? err.message : 'Unknown error occurred');
      }
      console.error('Failed to fetch repositories:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string | null, conclusion: string | null) => {
    if (!status) return '#6b7280';
    if (status === 'completed') {
      if (conclusion === 'success') return '#10b981';
      if (conclusion === 'failure') return '#ef4444';
    }
    if (status === 'in_progress') return '#f59e0b';
    return '#6b7280';
  };

  const getStatusText = (status: string | null, conclusion: string | null) => {
    if (!status) return 'No CI';
    if (status === 'completed') {
      if (conclusion === 'success') return '✅ Success';
      if (conclusion === 'failure') return '❌ Failed';
      return `✓ ${conclusion}`;
    }
    if (status === 'in_progress') return '🔄 Running';
    return status;
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '400px' 
      }}>
        <div style={{ color: '#a1a1aa', fontSize: '1.1rem' }}>
          Loading repositories...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        padding: '2rem', 
        textAlign: 'center',
        color: '#ef4444' 
      }}>
        <h3>Error loading repositories</h3>
        <p>{error}</p>
        <button 
          onClick={fetchRepositories}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '0.5rem',
            cursor: 'pointer',
            marginTop: '1rem'
          }}
        >
          Retry
        </button>
      </div>
    );
  }

  if (repositories.length === 0) {
    return (
      <div style={{ 
        padding: '4rem 2rem', 
        textAlign: 'center',
        color: '#a1a1aa' 
      }}>
        <h3 style={{ color: '#ffffff', marginBottom: '1rem' }}>No repositories found</h3>
        <p>Configure your ALLOWED_REPOS environment variable and set up webhooks to start monitoring repositories.</p>
      </div>
    );
  }

  return (
    <section style={{ 
      padding: '2rem',
      maxWidth: '1200px',
      margin: '0 auto'
    }}>
      <h2 style={{ 
        fontSize: '2rem', 
        fontWeight: '700', 
        color: '#ffffff', 
        marginBottom: '2rem',
        textAlign: 'center'
      }}>
        📊 プロジェクト詳細
      </h2>
      
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
        gap: '1.5rem'
      }}>
        {repositories.map((repo) => (
          <div
            key={repo.id}
            style={{
              background: 'rgba(255, 255, 255, 0.05)',
              backdropFilter: 'blur(20px)',
              padding: '2rem',
              borderRadius: '1rem',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              transition: 'transform 0.3s ease, box-shadow 0.3s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-4px)';
              e.currentTarget.style.boxShadow = '0 20px 40px -12px rgba(0, 0, 0, 0.4)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            <div style={{ marginBottom: '1rem' }}>
              <h3 style={{ 
                color: '#ffffff', 
                fontSize: '1.25rem', 
                fontWeight: '600',
                marginBottom: '0.5rem'
              }}>
                <a 
                  href={repo.html_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  style={{ 
                    color: '#ffffff', 
                    textDecoration: 'none' 
                  }}
                >
                  {repo.full_name}
                </a>
              </h3>
              {repo.description && (
                <p style={{ 
                  color: '#a1a1aa', 
                  fontSize: '0.9rem',
                  lineHeight: '1.5',
                  margin: 0
                }}>
                  {repo.description}
                </p>
              )}
            </div>

            {/* Quick Actions */}
            <div style={{
              display: 'flex',
              gap: '0.75rem',
              marginBottom: '1.5rem',
              flexWrap: 'wrap'
            }}>
              <a
                href={`${repo.html_url}/issues`}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.5rem 1rem',
                  background: 'rgba(251, 191, 36, 0.1)',
                  border: '1px solid rgba(251, 191, 36, 0.3)',
                  borderRadius: '0.5rem',
                  color: '#fbbf24',
                  textDecoration: 'none',
                  fontSize: '0.85rem',
                  fontWeight: '500',
                  transition: 'all 0.3s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(251, 191, 36, 0.15)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(251, 191, 36, 0.1)';
                }}
              >
                🎯 Issues ({repo.stats.open_issues})
              </a>
              <a
                href={`${repo.html_url}/pulls`}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.5rem 1rem',
                  background: 'rgba(52, 211, 153, 0.1)',
                  border: '1px solid rgba(52, 211, 153, 0.3)',
                  borderRadius: '0.5rem',
                  color: '#34d399',
                  textDecoration: 'none',
                  fontSize: '0.85rem',
                  fontWeight: '500',
                  transition: 'all 0.3s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(52, 211, 153, 0.15)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(52, 211, 153, 0.1)';
                }}
              >
                🔄 PRs ({repo.stats.open_prs})
              </a>
              <a
                href={`${repo.html_url}/actions`}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.5rem 1rem',
                  background: `rgba(${getStatusColor(repo.stats.latest_ci_status, repo.stats.latest_ci_conclusion).replace('#', '')}, 0.1)`,
                  border: `1px solid rgba(${getStatusColor(repo.stats.latest_ci_status, repo.stats.latest_ci_conclusion).replace('#', '')}, 0.3)`,
                  borderRadius: '0.5rem',
                  color: getStatusColor(repo.stats.latest_ci_status, repo.stats.latest_ci_conclusion),
                  textDecoration: 'none',
                  fontSize: '0.85rem',
                  fontWeight: '500',
                  transition: 'all 0.3s ease'
                }}
              >
                {getStatusText(repo.stats.latest_ci_status, repo.stats.latest_ci_conclusion)}
              </a>
            </div>

            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: '1fr 1fr 1fr', 
              gap: '1rem',
              marginBottom: '1rem'
            }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ 
                  fontSize: '1.5rem', 
                  fontWeight: '700', 
                  color: '#60a5fa' 
                }}>
                  {repo.stats.branches}
                </div>
                <div style={{ 
                  fontSize: '0.8rem', 
                  color: '#a1a1aa' 
                }}>
                  開発ブランチ
                </div>
              </div>
              
              <div style={{ textAlign: 'center' }}>
                <div style={{ 
                  fontSize: '1.5rem', 
                  fontWeight: '700', 
                  color: repo.stats.open_issues === 0 ? '#22c55e' : '#fbbf24'
                }}>
                  {repo.stats.open_issues}
                </div>
                <div style={{ 
                  fontSize: '0.8rem', 
                  color: '#a1a1aa' 
                }}>
                  残りタスク
                </div>
              </div>
              
              <div style={{ textAlign: 'center' }}>
                <div style={{ 
                  fontSize: '1.5rem', 
                  fontWeight: '700', 
                  color: '#34d399' 
                }}>
                  {repo.stats.open_prs}
                </div>
                <div style={{ 
                  fontSize: '0.8rem', 
                  color: '#a1a1aa' 
                }}>
                  レビュー待ち
                </div>
              </div>
            </div>

            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              alignItems: 'center',
              paddingTop: '1rem',
              borderTop: '1px solid rgba(255, 255, 255, 0.1)'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}>
                <span style={{
                  padding: '0.25rem 0.75rem',
                  background: 'rgba(34, 197, 94, 0.1)',
                  border: '1px solid rgba(34, 197, 94, 0.3)',
                  borderRadius: '1rem',
                  color: '#22c55e',
                  fontSize: '0.75rem',
                  fontWeight: '500'
                }}>
                  🚀 Hackathon
                </span>
                <span style={{ 
                  fontSize: '0.8rem', 
                  color: '#a1a1aa' 
                }}>
                  {repo.visibility}
                </span>
              </div>
              <span style={{ 
                fontSize: '0.8rem', 
                color: '#a1a1aa' 
              }}>
                更新: {new Date(repo.updated_at).toLocaleDateString('ja-JP')}
              </span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

export default RepositoryList;