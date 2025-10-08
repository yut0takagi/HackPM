import React, { useState, useEffect } from 'react';
import { api } from '../utils/api';

interface Event {
  id: number;
  repository: string;
  event_type: string;
  action: string | null;
  actor: string | null;
  ref: string | null;
  delivery_id: string | null;
  created_at: string;
}

const RecentEvents: React.FC = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEvents();
    // Poll for new events every 30 seconds
    const interval = setInterval(fetchEvents, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchEvents = async () => {
    try {
      const data = await api.getEvents({ limit: 20 });
      setEvents(data);
    } catch (error) {
      console.error('Failed to fetch events:', error);
    } finally {
      setLoading(false);
    }
  };

  const getEventIcon = (eventType: string, action: string | null) => {
    switch (eventType) {
      case 'push':
        return '📤';
      case 'pull_request':
        if (action === 'opened') return '🔄';
        if (action === 'closed') return '✅';
        return '🔄';
      case 'issues':
        if (action === 'opened') return '🐛';
        if (action === 'closed') return '✅';
        return '📋';
      case 'workflow_run':
        return '⚙️';
      case 'create':
        return '🌿';
      case 'delete':
        return '🗑️';
      default:
        return '📝';
    }
  };

  const getEventDescription = (event: Event) => {
    const { event_type, action, actor, ref, repository } = event;
    
    switch (event_type) {
      case 'push':
        return `${actor} pushed to ${ref?.replace('refs/heads/', '') || 'branch'} in ${repository}`;
      case 'pull_request':
        return `${actor} ${action} a pull request in ${repository}`;
      case 'issues':
        return `${actor} ${action} an issue in ${repository}`;
      case 'workflow_run':
        return `CI workflow ${action} in ${repository}`;
      case 'create':
        return `${actor} created ${ref?.replace('refs/heads/', '') || 'branch'} in ${repository}`;
      case 'delete':
        return `${actor} deleted ${ref?.replace('refs/heads/', '') || 'branch'} in ${repository}`;
      default:
        return `${event_type} event in ${repository}`;
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return `${Math.floor(diffInSeconds / 86400)}d ago`;
  };

  if (loading) {
    return (
      <div style={{ 
        padding: '2rem',
        textAlign: 'center',
        color: '#a1a1aa'
      }}>
        Loading recent events...
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
        📈 開発アクティビティ
      </h2>
      
      {events.length === 0 ? (
        <div style={{ 
          textAlign: 'center',
          color: '#a1a1aa',
          padding: '3rem',
          background: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(20px)',
          borderRadius: '1rem',
          border: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🚀</div>
          <h3 style={{ color: '#ffffff', marginBottom: '1rem' }}>
            開発を開始しましょう！
          </h3>
          <p>GitHubでコミット、PR、Issueの作成を行うと、ここにアクティビティが表示されます。</p>
          <div style={{ marginTop: '1.5rem' }}>
            <a
              href="https://github.com/yut0takagi/Keel/issues/new"
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.75rem 1.5rem',
                background: 'rgba(59, 130, 246, 0.1)',
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
              ➕ 新しいIssueを作成
            </a>
          </div>
        </div>
      ) : (
        <div style={{
          background: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(20px)',
          borderRadius: '1rem',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          overflow: 'hidden'
        }}>
          {events.map((event, index) => (
            <div
              key={event.id}
              style={{
                padding: '1.5rem',
                borderBottom: index < events.length - 1 ? '1px solid rgba(255, 255, 255, 0.1)' : 'none',
                display: 'flex',
                alignItems: 'center',
                gap: '1rem',
                transition: 'background-color 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              <div style={{ 
                fontSize: '1.5rem',
                minWidth: '2rem',
                textAlign: 'center'
              }}>
                {getEventIcon(event.event_type, event.action)}
              </div>
              
              <div style={{ flex: 1 }}>
                <div style={{ 
                  color: '#ffffff',
                  fontSize: '0.95rem',
                  marginBottom: '0.25rem'
                }}>
                  {getEventDescription(event)}
                </div>
                <div style={{ 
                  color: '#a1a1aa',
                  fontSize: '0.8rem'
                }}>
                  {formatTimeAgo(event.created_at)}
                </div>
              </div>
              
              <div style={{
                padding: '0.25rem 0.75rem',
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                borderRadius: '1rem',
                fontSize: '0.75rem',
                color: '#a1a1aa'
              }}>
                {event.event_type}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
};

export default RecentEvents;