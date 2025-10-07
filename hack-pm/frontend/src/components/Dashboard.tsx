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
        // First check if API is healthy
        const healthy = await checkApiHealth();
        
        if (healthy) {
            await fetchStats();
        } else {
            setError('APIサーバーに接続できません。バックエンドが起動しているか確認してください。');
            setLoading(false);
        }
    };

    const fetchStats = async () => {
        try {
            setError(null);
            const data = await api.getStats();
            setStats(data);
        } catch (err) {
            if (err instanceof ApiError) {
                setError(`Failed to load stats (${err.status}): ${err.message}`);
            } else {
                setError(err instanceof Error ? err.message : 'Failed to load statistics');
            }
            console.error('Failed to fetch stats:', err);
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
                <h1 style={{
                    fontSize: '4rem',
                    fontWeight: '700',
                    color: '#ffffff',
                    marginBottom: '1.5rem',
                    letterSpacing: '-0.02em',
                    lineHeight: '1.1'
                }}>
                    GitHub統合
                    <br />
                    <span style={{
                        background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        backgroundClip: 'text'
                    }}>
                        ダッシュボード
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
                    リアルタイムでGitHubリポジトリの活動を監視。
                    <br />
                    プロジェクトの進捗を美しく可視化します。
                </p>
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
                                {stats.total_repos}
                            </div>
                            <div style={{ color: '#a1a1aa', fontSize: '0.9rem' }}>
                                監視中リポジトリ
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
                                オープンPR
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
                                color: '#fbbf24',
                                marginBottom: '0.5rem'
                            }}>
                                {stats.open_issues}
                            </div>
                            <div style={{ color: '#a1a1aa', fontSize: '0.9rem' }}>
                                オープンIssue
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
                                color: '#a78bfa',
                                marginBottom: '0.5rem'
                            }}>
                                {stats.recent_events}
                            </div>
                            <div style={{ color: '#a1a1aa', fontSize: '0.9rem' }}>
                                最近のイベント
                            </div>
                        </div>
                    </div>

                    <div style={{
                        textAlign: 'center',
                        color: '#6b7280',
                        fontSize: '0.8rem',
                        marginBottom: '2rem'
                    }}>
                        最終更新: {new Date(stats.last_updated).toLocaleString('ja-JP')}
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