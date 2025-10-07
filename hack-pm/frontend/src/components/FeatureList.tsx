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
  const [features, setFeatures] = useState<Feature[]>([
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
      description: 'PostgreSQLデータベースの設計と構築',
      status: 'todo',
      priority: 'high',
      assignee: '高橋',
      estimatedHours: 14,
      startDate: '2024-01-22',
      endDate: '2024-01-28'
    },
    {
      id: 5,
      name: 'フロントエンド実装',
      description: 'React TypeScriptでのUI実装',
      status: 'in-progress',
      priority: 'medium',
      assignee: '山田',
      estimatedHours: 24,
      startDate: '2024-01-20',
      endDate: '2024-01-30'
    }
  ]);

  const [showAddModal, setShowAddModal] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>('all');

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'todo': return { bg: '#fef3c7', text: '#92400e', border: '#f59e0b' };
      case 'in-progress': return { bg: '#dbeafe', text: '#1e40af', border: '#3b82f6' };
      case 'review': return { bg: '#fde68a', text: '#92400e', border: '#f59e0b' };
      case 'done': return { bg: '#d1fae5', text: '#065f46', border: '#10b981' };
      default: return { bg: '#f3f4f6', text: '#374151', border: '#9ca3af' };
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'low': return '#10b981';
      case 'medium': return '#f59e0b';
      case 'high': return '#ef4444';
      case 'critical': return '#dc2626';
      default: return '#6b7280';
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
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', color: '#1f2937', marginBottom: '0.5rem' }}>
          機能一覧
        </h1>
        <p style={{ color: '#6b7280', margin: 0 }}>
          プロジェクトの機能開発を管理・追跡します
        </p>
      </div>

      {/* Status Filter */}
      <div style={{ 
        display: 'flex', 
        gap: '0.5rem', 
        marginBottom: '2rem',
        flexWrap: 'wrap'
      }}>
        {Object.entries(statusCounts).map(([status, count]) => (
          <button
            key={status}
            onClick={() => setFilterStatus(status)}
            style={{
              padding: '0.5rem 1rem',
              borderRadius: '0.5rem',
              border: '1px solid',
              borderColor: filterStatus === status ? '#3b82f6' : '#d1d5db',
              backgroundColor: filterStatus === status ? '#dbeafe' : 'white',
              color: filterStatus === status ? '#1e40af' : '#374151',
              cursor: 'pointer',
              fontSize: '0.875rem',
              fontWeight: '500',
              transition: 'all 0.2s'
            }}
          >
            {status === 'all' ? '全て' : 
             status === 'todo' ? '未着手' :
             status === 'in-progress' ? '進行中' :
             status === 'review' ? 'レビュー' : '完了'} ({count})
          </button>
        ))}
      </div>

      {/* Add Feature Button */}
      <div style={{ marginBottom: '2rem' }}>
        <button
          onClick={() => setShowAddModal(true)}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '0.5rem',
            fontSize: '0.875rem',
            fontWeight: '500',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#2563eb'}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#3b82f6'}
        >
          <span>➕</span>
          新機能追加
        </button>
      </div>

      {/* Features Table */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '0.75rem',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
        overflow: 'hidden',
        border: '1px solid #e5e7eb'
      }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ backgroundColor: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
                <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600', color: '#374151' }}>機能名</th>
                <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600', color: '#374151' }}>ステータス</th>
                <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600', color: '#374151' }}>優先度</th>
                <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600', color: '#374151' }}>担当者</th>
                <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600', color: '#374151' }}>期間</th>
                <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600', color: '#374151' }}>工数</th>
                <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600', color: '#374151' }}>操作</th>
              </tr>
            </thead>
            <tbody>
              {filteredFeatures.map((feature, index) => {
                const statusColor = getStatusColor(feature.status);
                return (
                  <tr 
                    key={feature.id}
                    style={{ 
                      borderBottom: index < filteredFeatures.length - 1 ? '1px solid #f3f4f6' : 'none',
                      transition: 'background-color 0.2s'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                  >
                    <td style={{ padding: '1rem' }}>
                      <div>
                        <div style={{ fontWeight: '500', color: '#1f2937', marginBottom: '0.25rem' }}>
                          {feature.name}
                        </div>
                        <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                          {feature.description}
                        </div>
                      </div>
                    </td>
                    <td style={{ padding: '1rem' }}>
                      <span style={{
                        padding: '0.25rem 0.75rem',
                        borderRadius: '9999px',
                        fontSize: '0.75rem',
                        fontWeight: '500',
                        backgroundColor: statusColor.bg,
                        color: statusColor.text,
                        border: `1px solid ${statusColor.border}`
                      }}>
                        {getStatusText(feature.status)}
                      </span>
                    </td>
                    <td style={{ padding: '1rem' }}>
                      <div style={{
                        width: '0.75rem',
                        height: '0.75rem',
                        borderRadius: '50%',
                        backgroundColor: getPriorityColor(feature.priority),
                        display: 'inline-block'
                      }} />
                    </td>
                    <td style={{ padding: '1rem', color: '#374151' }}>
                      {feature.assignee}
                    </td>
                    <td style={{ padding: '1rem', fontSize: '0.875rem', color: '#6b7280' }}>
                      {feature.startDate} - {feature.endDate}
                    </td>
                    <td style={{ padding: '1rem', fontSize: '0.875rem', color: '#6b7280' }}>
                      {feature.actualHours ? `${feature.actualHours}h` : `${feature.estimatedHours}h予定`}
                    </td>
                    <td style={{ padding: '1rem' }}>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button style={{
                          padding: '0.25rem 0.5rem',
                          fontSize: '0.75rem',
                          backgroundColor: '#f3f4f6',
                          border: '1px solid #d1d5db',
                          borderRadius: '0.375rem',
                          cursor: 'pointer',
                          color: '#374151'
                        }}>
                          編集
                        </button>
                        <button style={{
                          padding: '0.25rem 0.5rem',
                          fontSize: '0.75rem',
                          backgroundColor: '#fef2f2',
                          border: '1px solid #fecaca',
                          borderRadius: '0.375rem',
                          cursor: 'pointer',
                          color: '#dc2626'
                        }}>
                          削除
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default FeatureList;