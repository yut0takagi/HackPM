import React, { useState, useEffect } from 'react';
import { api } from '../utils/api';

interface Commit {
  sha: string;
  full_sha: string;
  message: string;
  author: string;
  email: string;
  date: string;
  branch: string;
  event_id: number;
}

interface Branch {
  name: string;
  head_sha: string;
  is_default: boolean;
  is_protected: boolean;
  last_commit: {
    sha: string;
    message: string;
    author: string;
    date: string | null;
  };
  updated_at: string;
}

interface Merge {
  pr_number: number;
  title: string;
  from_branch: string;
  to_branch: string;
  merge_sha: string | null;
  author: string;
  merged_at: string | null;
}

interface GitGraphData {
  repository: {
    id: number;
    full_name: string;
    default_branch: string;
  };
  branches: Branch[];
  commits: Commit[];
  merges: Merge[];
}

interface GitGraphProps {
  repositoryId: number;
}

const GitGraph: React.FC<GitGraphProps> = ({ repositoryId }) => {
  const [graphData, setGraphData] = useState<GitGraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedBranch, setSelectedBranch] = useState<string>('all');

  useEffect(() => {
    fetchGraphData();
  }, [repositoryId]);

  const fetchGraphData = async () => {
    try {
      setError(null);
      const data = await api.getRepositoryGitGraph(repositoryId);
      setGraphData(data);
      if (data.branches.length > 0) {
        setSelectedBranch(data.repository.default_branch);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load git graph');
      console.error('Failed to fetch git graph:', err);
    } finally {
      setLoading(false);
    }
  };

  const getBranchColor = (branchName: string) => {
    const colors = [
      '#3b82f6', '#10b981', '#f59e0b', '#ef4444', 
      '#8b5cf6', '#06b6d4', '#84cc16', '#f97316'
    ];
    let hash = 0;
    for (let i = 0; i < branchName.length; i++) {
      hash = branchName.charCodeAt(i) + ((hash << 5) - hash);
    }
    return colors[Math.abs(hash) % colors.length];
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)}d ago`;
    return date.toLocaleDateString();
  };

  const filteredCommits = selectedBranch === 'all' 
    ? graphData?.commits || []
    : graphData?.commits.filter(commit => commit.branch === selectedBranch) || [];

  if (loading) {
    return (
      <div style={{ 
        padding: '4rem 2rem',
        textAlign: 'center',
        color: '#a1a1aa'
      }}>
        <div style={{ fontSize: '1.1rem' }}>
          Loading git graph...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        padding: '4rem 2rem',
        textAlign: 'center'
      }}>
        <div style={{ 
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '1rem',
          padding: '2rem',
          maxWidth: '600px',
          margin: '0 auto'
        }}>
          <h3 style={{ color: '#ef4444', marginBottom: '1rem' }}>
            Git Graph読み込みエラー
          </h3>
          <p style={{ color: '#a1a1aa', marginBottom: '1.5rem' }}>
            {error}
          </p>
          <button
            onClick={fetchGraphData}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#ef4444',
              color: 'white',
              border: 'none',
              borderRadius: '0.5rem',
              cursor: 'pointer',
              fontSize: '0.95rem',
              fontWeight: '500'
            }}
          >
            再試行
          </button>
        </div>
      </div>
    );
  }

  if (!graphData || graphData.commits.length === 0) {
    return (
      <div style={{ 
        padding: '4rem 2rem',
        textAlign: 'center',
        color: '#a1a1aa'
      }}>
        <h3 style={{ color: '#ffffff', marginBottom: '1rem' }}>
          コミット履歴がありません
        </h3>
        <p>
          このリポジトリにはまだコミット履歴が記録されていません。
          <br />
          Webhookが設定されると、新しいコミットが表示されます。
        </p>
      </div>
    );
  }

  return (
    <div style={{ 
      padding: '0',
      background: 'linear-gradient(135deg, #000000 0%, #1a1a1a 100%)',
      minHeight: '100vh'
    }}>
      {/* Header */}
      <section style={{ 
        padding: '6rem 2rem 2rem 2rem',
        textAlign: 'center',
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        <h1 style={{ 
          fontSize: '3rem', 
          fontWeight: '700', 
          color: '#ffffff', 
          marginBottom: '1rem',
          letterSpacing: '-0.02em'
        }}>
          <span style={{ 
            background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            Git Graph
          </span>
        </h1>
        <p style={{ 
          color: '#a1a1aa', 
          fontSize: '1.1rem',
          marginBottom: '2rem'
        }}>
          {graphData.repository.full_name}
        </p>

        {/* Branch Filter */}
        <div style={{ 
          display: 'flex', 
          gap: '0.75rem', 
          justifyContent: 'center',
          flexWrap: 'wrap',
          marginBottom: '2rem'
        }}>
          <button
            onClick={() => setSelectedBranch('all')}
            style={{
              padding: '0.75rem 1.5rem',
              borderRadius: '2rem',
              border: 'none',
              background: selectedBranch === 'all' 
                ? 'rgba(255, 255, 255, 0.2)' 
                : 'rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(10px)',
              color: selectedBranch === 'all' ? '#ffffff' : '#a1a1aa',
              cursor: 'pointer',
              fontSize: '0.95rem',
              fontWeight: '500',
              transition: 'all 0.3s ease'
            }}
          >
            All Branches ({graphData.commits.length})
          </button>
          
          {graphData.branches.map((branch) => (
            <button
              key={branch.name}
              onClick={() => setSelectedBranch(branch.name)}
              style={{
                padding: '0.75rem 1.5rem',
                borderRadius: '2rem',
                border: 'none',
                background: selectedBranch === branch.name 
                  ? 'rgba(255, 255, 255, 0.2)' 
                  : 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(10px)',
                color: selectedBranch === branch.name ? '#ffffff' : '#a1a1aa',
                cursor: 'pointer',
                fontSize: '0.95rem',
                fontWeight: '500',
                transition: 'all 0.3s ease',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}
            >
              <div style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: getBranchColor(branch.name)
              }}></div>
              {branch.name}
              {branch.is_default && (
                <span style={{ 
                  fontSize: '0.7rem',
                  padding: '0.2rem 0.5rem',
                  backgroundColor: 'rgba(16, 185, 129, 0.2)',
                  color: '#10b981',
                  borderRadius: '0.5rem'
                }}>
                  default
                </span>
              )}
            </button>
          ))}
        </div>
      </section>

      {/* Git Graph */}
      <section style={{ 
        padding: '0 2rem 4rem 2rem',
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        <div style={{
          background: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(20px)',
          borderRadius: '1rem',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          overflow: 'hidden'
        }}>
          {/* Graph Header */}
          <div style={{
            padding: '1.5rem',
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
            background: 'rgba(255, 255, 255, 0.05)'
          }}>
            <div style={{
              display: 'grid',
              gridTemplateColumns: '60px 120px 1fr 150px 120px',
              gap: '1rem',
              alignItems: 'center',
              fontSize: '0.9rem',
              fontWeight: '600',
              color: '#ffffff'
            }}>
              <div>Graph</div>
              <div>SHA</div>
              <div>Message</div>
              <div>Author</div>
              <div>Date</div>
            </div>
          </div>

          {/* Commit List */}
          <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
            {filteredCommits.length === 0 ? (
              <div style={{ 
                padding: '3rem',
                textAlign: 'center',
                color: '#a1a1aa'
              }}>
                <p>選択されたブランチにコミットがありません</p>
              </div>
            ) : (
              filteredCommits.map((commit, index) => (
                <div
                  key={`${commit.full_sha}-${commit.event_id}`}
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '60px 120px 1fr 150px 120px',
                    gap: '1rem',
                    alignItems: 'center',
                    padding: '1rem 1.5rem',
                    borderBottom: index < filteredCommits.length - 1 
                      ? '1px solid rgba(255, 255, 255, 0.05)' 
                      : 'none',
                    transition: 'background-color 0.2s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'transparent';
                  }}
                >
                  {/* Graph visualization */}
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    <div style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      height: '40px',
                      position: 'relative'
                    }}>
                      {/* Vertical line */}
                      {index < filteredCommits.length - 1 && (
                        <div style={{
                          position: 'absolute',
                          top: '20px',
                          width: '2px',
                          height: '40px',
                          backgroundColor: getBranchColor(commit.branch),
                          opacity: 0.3
                        }}></div>
                      )}
                      
                      {/* Commit dot */}
                      <div style={{
                        width: '12px',
                        height: '12px',
                        borderRadius: '50%',
                        backgroundColor: getBranchColor(commit.branch),
                        border: '2px solid rgba(255, 255, 255, 0.2)',
                        zIndex: 1,
                        boxShadow: `0 0 10px ${getBranchColor(commit.branch)}40`
                      }}></div>
                    </div>
                  </div>

                  {/* SHA */}
                  <div style={{
                    fontFamily: 'Monaco, Consolas, monospace',
                    fontSize: '0.85rem',
                    color: '#60a5fa',
                    fontWeight: '500'
                  }}>
                    {commit.sha}
                  </div>

                  {/* Message */}
                  <div>
                    <div style={{
                      color: '#ffffff',
                      fontSize: '0.95rem',
                      fontWeight: '500',
                      marginBottom: '0.25rem',
                      lineHeight: '1.4'
                    }}>
                      {commit.message.split('\n')[0]}
                    </div>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}>
                      <div style={{
                        width: '6px',
                        height: '6px',
                        borderRadius: '50%',
                        backgroundColor: getBranchColor(commit.branch)
                      }}></div>
                      <span style={{
                        fontSize: '0.8rem',
                        color: '#a1a1aa',
                        fontWeight: '500'
                      }}>
                        {commit.branch}
                      </span>
                    </div>
                  </div>

                  {/* Author */}
                  <div style={{
                    color: '#e5e7eb',
                    fontSize: '0.9rem'
                  }}>
                    {commit.author}
                  </div>

                  {/* Date */}
                  <div style={{
                    color: '#a1a1aa',
                    fontSize: '0.85rem'
                  }}>
                    {formatTimeAgo(commit.date)}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Merge Information */}
        {graphData.merges.length > 0 && (
          <div style={{ marginTop: '2rem' }}>
            <h3 style={{
              color: '#ffffff',
              fontSize: '1.5rem',
              fontWeight: '600',
              marginBottom: '1rem',
              textAlign: 'center'
            }}>
              Recent Merges
            </h3>
            
            <div style={{
              background: 'rgba(255, 255, 255, 0.05)',
              backdropFilter: 'blur(20px)',
              borderRadius: '1rem',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              overflow: 'hidden'
            }}>
              {graphData.merges.map((merge, index) => (
                <div
                  key={merge.pr_number}
                  style={{
                    padding: '1.5rem',
                    borderBottom: index < graphData.merges.length - 1 
                      ? '1px solid rgba(255, 255, 255, 0.1)' 
                      : 'none',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '1rem'
                  }}
                >
                  <div style={{
                    fontSize: '1.5rem'
                  }}>
                    🔀
                  </div>
                  
                  <div style={{ flex: 1 }}>
                    <div style={{
                      color: '#ffffff',
                      fontSize: '1rem',
                      fontWeight: '500',
                      marginBottom: '0.5rem'
                    }}>
                      PR #{merge.pr_number}: {merge.title}
                    </div>
                    
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '1rem',
                      fontSize: '0.85rem',
                      color: '#a1a1aa'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div style={{
                          width: '6px',
                          height: '6px',
                          borderRadius: '50%',
                          backgroundColor: getBranchColor(merge.from_branch)
                        }}></div>
                        <span>{merge.from_branch}</span>
                        <span>→</span>
                        <div style={{
                          width: '6px',
                          height: '6px',
                          borderRadius: '50%',
                          backgroundColor: getBranchColor(merge.to_branch)
                        }}></div>
                        <span>{merge.to_branch}</span>
                      </div>
                      
                      <span>by {merge.author}</span>
                      
                      {merge.merged_at && (
                        <span>{formatTimeAgo(merge.merged_at)}</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </section>
    </div>
  );
};

export default GitGraph;