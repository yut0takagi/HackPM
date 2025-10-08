import React, { useState, useEffect } from 'react';
import { api, ApiError, checkApiHealth } from '../utils/api';
import RepositoryList from './RepositoryList';
import RecentEvents from './RecentEvents';

interface Stats {
    total_repos: number;
    total_branches: number;
    open_prs: number;
    open_issues: number;
    recent_ci_runs: number;
    recent_events: number;
    last_updated: string;
}

const Dashboard: React.FC = () => {
    const [stats, setStats] = useState<Stats | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        initializeApp();
        // Refresh stats every 5 minutes
        const interval = setInterval(fetchStats, 5 * 60 * 1000);
        return () => clearInterval(interval);
    }, []);

    const initializeApp = async () => {
        try {
            console.log('Initializing app...');
            // First check if API is healthy
            const healthy = await checkApiHealth();
            console.log('API health check result:', healthy);

            if (healthy) {
                console.log('API is healthy, fetching stats...');
                await fetchStats();
            } else {
                console.error('API health check failed');
                setError('APIサーバーに接続できません。バックエンドが起動しているか確認してください。');
                setLoading(false);
            }
        } catch (error) {
            console.error('Error during app initialization:', error);
            setError(`初期化エラー: ${error instanceof Error ? error.message : 'Unknown error'}`);
            setLoading(false);
        }
    };

    const fetchStats = async () => {
        try {
            console.log('Fetching stats...');
            setError(null);
            const data = await api.getStats();
            console.log('Stats data received:', data);
            setStats(data);
        } catch (err) {
            console.error('Failed to fetch stats:', err);
            if (err instanceof ApiError) {
                setError(`統計情報の読み込みに失敗しました (${err.status}): ${err.message}`);
            } else {
                setError(err instanceof Error ? err.message : '統計情報の読み込みに失敗しました');
            }
        } finally {
            setLoading(false);
        }
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
                background: 'radial-gradient(ellipse at center, rgba(59, 130, 246, 0.1) 0%, transparent 70%)'
            }}>
                <div style={{
                    display: 'inline-block',
                    padding: '0.5rem 1.5rem',
                    background: 'rgba(34, 197, 94, 0.1)',
                    border: '1px solid rgba(34, 197, 94, 0.3)',
                    borderRadius: '2rem',
                    color: '#22c55e',
                    fontSize: '0.9rem',
                    fontWeight: '500',
                    marginBottom: '2rem'
                }}>
                    🚀 Hackathon Project Dashboard
                </div>
                <h1 style={{
                    fontSize: '4rem',
                    fontWeight: '700',
                    color: '#ffffff',
                    marginBottom: '1.5rem',
                    letterSpacing: '-0.02em',
                    lineHeight: '1.1'
                }}>
                    Keel Project
                    <br />
                    <span style={{
                        background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        backgroundClip: 'text'
                    }}>
                        Management Hub
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
                    Hackathon用テンプレートリポジトリの進捗管理。
                    <br />
                    チームの開発状況をリアルタイムで追跡します。
                </p>

                {/* Quick Actions */}
                <div style={{
                    display: 'flex',
                    gap: '1rem',
                    justifyContent: 'center',
                    marginTop: '2rem',
                    flexWrap: 'wrap'
                }}>
                    <a
                        href="https://github.com/yut0takagi/Keel"
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            padding: '0.75rem 1.5rem',
                            background: 'rgba(255, 255, 255, 0.1)',
                            backdropFilter: 'blur(20px)',
                            border: '1px solid rgba(255, 255, 255, 0.2)',
                            borderRadius: '0.75rem',
                            color: '#ffffff',
                            textDecoration: 'none',
                            fontSize: '0.95rem',
                            fontWeight: '500',
                            transition: 'all 0.3s ease'
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.15)';
                            e.currentTarget.style.transform = 'translateY(-2px)';
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
                            e.currentTarget.style.transform = 'translateY(0)';
                        }}
                    >
                        📁 リポジトリを開く
                    </a>
                    <a
                        href="https://github.com/yut0takagi/Keel/issues"
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            padding: '0.75rem 1.5rem',
                            background: 'rgba(59, 130, 246, 0.1)',
                            backdropFilter: 'blur(20px)',
                            border: '1px solid rgba(59, 130, 246, 0.3)',
                            borderRadius: '0.75rem',
                            color: '#3b82f6',
                            textDecoration: 'none',
                            fontSize: '0.95rem',
                            fontWeight: '500',
                            transition: 'all 0.3s ease'
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.background = 'rgba(59, 130, 246, 0.15)';
                            e.currentTarget.style.transform = 'translateY(-2px)';
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.background = 'rgba(59, 130, 246, 0.1)';
                            e.currentTarget.style.transform = 'translateY(0)';
                        }}
                    >
                        🎯 Issues管理
                    </a>
                </div>
            </section>

            {/* Stats Section */}
            {loading ? (
                <section style={{
                    padding: '4rem 2rem',
                    textAlign: 'center'
                }}>
                    <div style={{ color: '#a1a1aa', fontSize: '1.1rem' }}>
                        統計情報を読み込み中...
                    </div>
                </section>
            ) : error ? (
                <section style={{
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
                            統計情報の読み込みに失敗しました
                        </h3>
                        <p style={{ color: '#a1a1aa', marginBottom: '1.5rem' }}>
                            {error}
                        </p>
                        <button
                            onClick={fetchStats}
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
                </section>
            ) : stats && (
                <section style={{
                    padding: '4rem 2rem',
                    maxWidth: '1200px',
                    margin: '0 auto'
                }}>
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                        gap: '2rem',
                        marginBottom: '2rem'
                    }}>
                        <div style={{
                            background: 'rgba(255, 255, 255, 0.05)',
                            backdropFilter: 'blur(20px)',
                            padding: '2rem',
                            borderRadius: '1.5rem',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            textAlign: 'center',
                            transition: 'transform 0.3s ease'
                        }}
                            onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-4px)'}
                            onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}>
                            <div style={{
                                fontSize: '2.5rem',
                                fontWeight: '700',
                                color: '#60a5fa',
                                marginBottom: '0.5rem'
                            }}>
                                {stats.total_branches}
                            </div>
                            <div style={{ color: '#a1a1aa', fontSize: '0.9rem' }}>
                                開発ブランチ
                            </div>
                        </div>

                        <div style={{
                            background: 'rgba(255, 255, 255, 0.05)',
                            backdropFilter: 'blur(20px)',
                            padding: '2rem',
                            borderRadius: '1.5rem',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            textAlign: 'center',
                            transition: 'transform 0.3s ease'
                        }}
                            onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-4px)'}
                            onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}>
                            <div style={{
                                fontSize: '2.5rem',
                                fontWeight: '700',
                                color: stats.open_issues === 0 ? '#22c55e' : '#fbbf24',
                                marginBottom: '0.5rem'
                            }}>
                                {stats.open_issues}
                            </div>
                            <div style={{ color: '#a1a1aa', fontSize: '0.9rem' }}>
                                残りタスク
                            </div>
                        </div>

                        <div style={{
                            background: 'rgba(255, 255, 255, 0.05)',
                            backdropFilter: 'blur(20px)',
                            padding: '2rem',
                            borderRadius: '1.5rem',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            textAlign: 'center',
                            transition: 'transform 0.3s ease'
                        }}
                            onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-4px)'}
                            onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}>
                            <div style={{
                                fontSize: '2.5rem',
                                fontWeight: '700',
                                color: '#34d399',
                                marginBottom: '0.5rem'
                            }}>
                                {stats.open_prs}
                            </div>
                            <div style={{ color: '#a1a1aa', fontSize: '0.9rem' }}>
                                レビュー待ちPR
                            </div>
                        </div>

                        <div style={{
                            background: 'rgba(255, 255, 255, 0.05)',
                            backdropFilter: 'blur(20px)',
                            padding: '2rem',
                            borderRadius: '1.5rem',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            textAlign: 'center',
                            transition: 'transform 0.3s ease'
                        }}
                            onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-4px)'}
                            onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}>
                            <div style={{
                                fontSize: '2.5rem',
                                fontWeight: '700',
                                color: stats.recent_ci_runs > 0 ? '#a78bfa' : '#6b7280',
                                marginBottom: '0.5rem'
                            }}>
                                {stats.recent_ci_runs}
                            </div>
                            <div style={{ color: '#a1a1aa', fontSize: '0.9rem' }}>
                                CI実行回数
                            </div>
                        </div>
                    </div>

                    <div style={{
                        textAlign: 'center',
                        color: '#6b7280',
                        fontSize: '0.8rem',
                        marginBottom: '3rem'
                    }}>
                        最終更新: {new Date(stats.last_updated).toLocaleString('ja-JP')}
                    </div>

                    {/* Project Progress Section */}
                    <div style={{
                        background: 'rgba(255, 255, 255, 0.05)',
                        backdropFilter: 'blur(20px)',
                        padding: '2.5rem',
                        borderRadius: '1.5rem',
                        border: '1px solid rgba(255, 255, 255, 0.1)',
                        marginBottom: '2rem'
                    }}>
                        <h3 style={{
                            color: '#ffffff',
                            fontSize: '1.5rem',
                            fontWeight: '600',
                            marginBottom: '1.5rem',
                            textAlign: 'center'
                        }}>
                            🎯 プロジェクト進捗
                        </h3>

                        <div style={{
                            display: 'grid',
                            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                            gap: '1.5rem'
                        }}>
                            {/* Task Completion */}
                            <div style={{
                                background: 'rgba(0, 0, 0, 0.2)',
                                padding: '1.5rem',
                                borderRadius: '1rem',
                                border: '1px solid rgba(255, 255, 255, 0.1)'
                            }}>
                                <div style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                    marginBottom: '1rem'
                                }}>
                                    <span style={{ color: '#a1a1aa', fontSize: '0.9rem' }}>
                                        タスク完了率
                                    </span>
                                    <span style={{ color: '#ffffff', fontWeight: '600' }}>
                                        {stats.open_issues === 0 ? '100%' : `${Math.round((1 - stats.open_issues / (stats.open_issues + 1)) * 100)}%`}
                                    </span>
                                </div>
                                <div style={{
                                    width: '100%',
                                    height: '8px',
                                    background: 'rgba(255, 255, 255, 0.1)',
                                    borderRadius: '4px',
                                    overflow: 'hidden'
                                }}>
                                    <div style={{
                                        width: stats.open_issues === 0 ? '100%' : `${Math.round((1 - stats.open_issues / (stats.open_issues + 1)) * 100)}%`,
                                        height: '100%',
                                        background: 'linear-gradient(90deg, #22c55e 0%, #16a34a 100%)',
                                        transition: 'width 0.5s ease'
                                    }} />
                                </div>
                            </div>

                            {/* Development Activity */}
                            <div style={{
                                background: 'rgba(0, 0, 0, 0.2)',
                                padding: '1.5rem',
                                borderRadius: '1rem',
                                border: '1px solid rgba(255, 255, 255, 0.1)'
                            }}>
                                <div style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                    marginBottom: '1rem'
                                }}>
                                    <span style={{ color: '#a1a1aa', fontSize: '0.9rem' }}>
                                        開発アクティビティ
                                    </span>
                                    <span style={{
                                        color: stats.recent_ci_runs > 5 ? '#22c55e' : stats.recent_ci_runs > 0 ? '#fbbf24' : '#ef4444',
                                        fontWeight: '600'
                                    }}>
                                        {stats.recent_ci_runs > 5 ? '高' : stats.recent_ci_runs > 0 ? '中' : '低'}
                                    </span>
                                </div>
                                <div style={{
                                    display: 'flex',
                                    gap: '0.5rem',
                                    alignItems: 'center'
                                }}>
                                    {[...Array(5)].map((_, i) => (
                                        <div
                                            key={i}
                                            style={{
                                                width: '12px',
                                                height: '12px',
                                                borderRadius: '50%',
                                                background: i < Math.min(stats.recent_ci_runs / 2, 5)
                                                    ? 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)'
                                                    : 'rgba(255, 255, 255, 0.1)'
                                            }}
                                        />
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
            )}

            {/* Repository List */}
            <RepositoryList />

            {/* Recent Events */}
            <RecentEvents />
        </div>
    );
};

export default Dashboard;