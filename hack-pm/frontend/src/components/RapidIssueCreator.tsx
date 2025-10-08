import React, { useState, useEffect } from 'react';
import { api } from '../utils/api';

interface RapidIssueCreatorProps {
  repositoryId: number;
  onClose: () => void;
  onIssueCreated?: () => void;
}

interface QuickTemplate {
  id: string;
  name: string;
  icon: string;
  type: 'feature' | 'bug' | 'task';
  priority: 'critical' | 'high' | 'medium' | 'low';
  estimatedHours: number;
  description: string;
  titlePlaceholder: string;
}

const RapidIssueCreator: React.FC<RapidIssueCreatorProps> = ({
  repositoryId,
  onClose,
  onIssueCreated
}) => {
  const [selectedTemplate, setSelectedTemplate] = useState<QuickTemplate | null>(null);
  const [title, setTitle] = useState('');
  const [customEstimate, setCustomEstimate] = useState<number | null>(null);
  const [customPriority, setCustomPriority] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [batchMode, setBatchMode] = useState(false);
  const [batchTitles, setBatchTitles] = useState<string[]>(['']);

  const quickTemplates: QuickTemplate[] = [
    {
      id: 'quick-feature',
      name: 'クイック機能',
      icon: '⚡',
      type: 'feature',
      priority: 'medium',
      estimatedHours: 2,
      description: 'シンプルな機能実装',
      titlePlaceholder: 'ログイン機能を追加'
    },
    {
      id: 'bug-fix',
      name: 'バグ修正',
      icon: '🐛',
      type: 'bug',
      priority: 'high',
      estimatedHours: 1,
      description: '緊急バグ修正',
      titlePlaceholder: 'ログインエラーを修正'
    },
    {
      id: 'ui-task',
      name: 'UI改善',
      icon: '🎨',
      type: 'task',
      priority: 'medium',
      estimatedHours: 1.5,
      description: 'ユーザーインターフェース改善',
      titlePlaceholder: 'ボタンのスタイルを改善'
    },
    {
      id: 'api-task',
      name: 'API実装',
      icon: '🔌',
      type: 'task',
      priority: 'medium',
      estimatedHours: 3,
      description: 'API エンドポイント実装',
      titlePlaceholder: 'ユーザー情報取得APIを実装'
    },
    {
      id: 'test-task',
      name: 'テスト追加',
      icon: '🧪',
      type: 'task',
      priority: 'low',
      estimatedHours: 1,
      description: 'テストケース追加',
      titlePlaceholder: 'ログイン機能のテストを追加'
    },
    {
      id: 'docs-task',
      name: 'ドキュメント',
      icon: '📝',
      type: 'task',
      priority: 'low',
      estimatedHours: 0.5,
      description: 'ドキュメント作成・更新',
      titlePlaceholder: 'API仕様書を更新'
    },
    {
      id: 'hotfix',
      name: 'ホットフィックス',
      icon: '🚨',
      type: 'bug',
      priority: 'critical',
      estimatedHours: 0.5,
      description: '緊急修正',
      titlePlaceholder: '本番環境のクリティカルエラーを修正'
    },
    {
      id: 'refactor',
      name: 'リファクタリング',
      icon: '🔧',
      type: 'task',
      priority: 'low',
      estimatedHours: 2,
      description: 'コード改善',
      titlePlaceholder: 'ユーザー管理コードをリファクタリング'
    }
  ];

  const priorityColors = {
    critical: { bg: 'rgba(239, 68, 68, 0.2)', text: '#ef4444', border: '#dc2626' },
    high: { bg: 'rgba(245, 158, 11, 0.2)', text: '#f59e0b', border: '#d97706' },
    medium: { bg: 'rgba(59, 130, 246, 0.2)', text: '#3b82f6', border: '#2563eb' },
    low: { bg: 'rgba(107, 114, 128, 0.2)', text: '#6b7280', border: '#4b5563' }
  };

  const createIssue = async () => {
    if (!selectedTemplate || !title.trim()) return;

    setIsCreating(true);
    try {
      const issueData = {
        title: title.trim(),
        type: selectedTemplate.type,
        priority: customPriority || selectedTemplate.priority,
        estimated_hours: customEstimate || selectedTemplate.estimatedHours
      };

      await api.createRapidIssue(repositoryId, issueData);
      
      // Reset form
      setTitle('');
      setSelectedTemplate(null);
      setCustomEstimate(null);
      setCustomPriority(null);
      
      onIssueCreated?.();
      
      if (!batchMode) {
        onClose();
      }
    } catch (error) {
      console.error('Failed to create issue:', error);
    } finally {
      setIsCreating(false);
    }
  };

  const createBatchIssues = async () => {
    if (!selectedTemplate || batchTitles.filter(t => t.trim()).length === 0) return;

    setIsCreating(true);
    try {
      const validTitles = batchTitles.filter(t => t.trim());
      
      for (const issueTitle of validTitles) {
        const issueData = {
          title: issueTitle.trim(),
          type: selectedTemplate.type,
          priority: customPriority || selectedTemplate.priority,
          estimated_hours: customEstimate || selectedTemplate.estimatedHours
        };

        await api.createRapidIssue(repositoryId, issueData);
      }
      
      // Reset form
      setBatchTitles(['']);
      setSelectedTemplate(null);
      setCustomEstimate(null);
      setCustomPriority(null);
      setBatchMode(false);
      
      onIssueCreated?.();
      onClose();
    } catch (error) {
      console.error('Failed to create batch issues:', error);
    } finally {
      setIsCreating(false);
    }
  };

  const addBatchTitle = () => {
    setBatchTitles([...batchTitles, '']);
  };

  const updateBatchTitle = (index: number, value: string) => {
    const newTitles = [...batchTitles];
    newTitles[index] = value;
    setBatchTitles(newTitles);
  };

  const removeBatchTitle = (index: number) => {
    if (batchTitles.length > 1) {
      const newTitles = batchTitles.filter((_, i) => i !== index);
      setBatchTitles(newTitles);
    }
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case 'Enter':
            e.preventDefault();
            if (batchMode) {
              createBatchIssues();
            } else {
              createIssue();
            }
            break;
          case 'Escape':
            e.preventDefault();
            onClose();
            break;
          case 'b':
            e.preventDefault();
            setBatchMode(!batchMode);
            break;
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [batchMode, selectedTemplate, title, batchTitles]);

  return (
    <div style={{
      background: 'rgba(26, 26, 26, 0.95)',
      backdropFilter: 'blur(20px)',
      borderRadius: '1rem',
      padding: '2rem',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      maxWidth: '800px',
      width: '100%',
      maxHeight: '90vh',
      overflow: 'auto'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '2rem'
      }}>
        <h2 style={{
          fontSize: '1.5rem',
          fontWeight: '700',
          color: '#ffffff',
          margin: 0
        }}>
          ⚡ クイックIssue作成
        </h2>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            onClick={() => setBatchMode(!batchMode)}
            style={{
              padding: '0.5rem 1rem',
              background: batchMode ? 'rgba(34, 197, 94, 0.2)' : 'rgba(255, 255, 255, 0.1)',
              border: `1px solid ${batchMode ? 'rgba(34, 197, 94, 0.3)' : 'rgba(255, 255, 255, 0.2)'}`,
              borderRadius: '0.5rem',
              color: batchMode ? '#22c55e' : '#a1a1aa',
              cursor: 'pointer',
              fontSize: '0.875rem',
              fontWeight: '500'
            }}
          >
            📦 バッチ作成
          </button>
          <button
            onClick={onClose}
            style={{
              padding: '0.5rem 1rem',
              background: 'rgba(239, 68, 68, 0.2)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: '0.5rem',
              color: '#ef4444',
              cursor: 'pointer',
              fontSize: '0.875rem',
              fontWeight: '500'
            }}
          >
            ✕ 閉じる
          </button>
        </div>
      </div>

      {/* Keyboard Shortcuts Info */}
      <div style={{
        background: 'rgba(59, 130, 246, 0.1)',
        border: '1px solid rgba(59, 130, 246, 0.2)',
        borderRadius: '0.5rem',
        padding: '0.75rem',
        marginBottom: '2rem',
        fontSize: '0.875rem',
        color: '#60a5fa'
      }}>
        💡 キーボードショートカット: Ctrl+Enter (作成) | Ctrl+B (バッチモード) | Esc (閉じる)
      </div>

      {/* Template Selection */}
      <div style={{ marginBottom: '2rem' }}>
        <h3 style={{
          fontSize: '1.125rem',
          fontWeight: '600',
          color: '#ffffff',
          marginBottom: '1rem'
        }}>
          テンプレート選択
        </h3>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '1rem'
        }}>
          {quickTemplates.map((template) => (
            <button
              key={template.id}
              onClick={() => {
                setSelectedTemplate(template);
                if (!batchMode) {
                  setTitle('');
                }
              }}
              style={{
                padding: '1rem',
                background: selectedTemplate?.id === template.id 
                  ? 'rgba(34, 197, 94, 0.2)' 
                  : 'rgba(255, 255, 255, 0.05)',
                border: selectedTemplate?.id === template.id 
                  ? '2px solid rgba(34, 197, 94, 0.5)' 
                  : '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '0.75rem',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                if (selectedTemplate?.id !== template.id) {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
                }
              }}
              onMouseLeave={(e) => {
                if (selectedTemplate?.id !== template.id) {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
                }
              }}
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                marginBottom: '0.5rem'
              }}>
                <span style={{ fontSize: '1.5rem' }}>{template.icon}</span>
                <span style={{
                  fontSize: '1rem',
                  fontWeight: '600',
                  color: '#ffffff'
                }}>
                  {template.name}
                </span>
              </div>
              <div style={{
                fontSize: '0.875rem',
                color: '#a1a1aa',
                marginBottom: '0.5rem'
              }}>
                {template.description}
              </div>
              <div style={{
                display: 'flex',
                gap: '0.5rem',
                alignItems: 'center'
              }}>
                <span style={{
                  padding: '0.25rem 0.5rem',
                  background: priorityColors[template.priority].bg,
                  color: priorityColors[template.priority].text,
                  borderRadius: '0.25rem',
                  fontSize: '0.75rem',
                  fontWeight: '500'
                }}>
                  {template.priority}
                </span>
                <span style={{
                  fontSize: '0.75rem',
                  color: '#a1a1aa'
                }}>
                  {template.estimatedHours}h
                </span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Issue Creation Form */}
      {selectedTemplate && (
        <div style={{ marginBottom: '2rem' }}>
          <h3 style={{
            fontSize: '1.125rem',
            fontWeight: '600',
            color: '#ffffff',
            marginBottom: '1rem'
          }}>
            Issue詳細
          </h3>

          {!batchMode ? (
            /* Single Issue Mode */
            <div style={{ marginBottom: '1rem' }}>
              <label style={{
                display: 'block',
                fontSize: '0.875rem',
                fontWeight: '500',
                color: '#a1a1aa',
                marginBottom: '0.5rem'
              }}>
                タイトル
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder={selectedTemplate.titlePlaceholder}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '0.5rem',
                  color: '#ffffff',
                  fontSize: '0.875rem'
                }}
                autoFocus
              />
            </div>
          ) : (
            /* Batch Mode */
            <div style={{ marginBottom: '1rem' }}>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '0.5rem'
              }}>
                <label style={{
                  fontSize: '0.875rem',
                  fontWeight: '500',
                  color: '#a1a1aa'
                }}>
                  Issue タイトル一覧
                </label>
                <button
                  onClick={addBatchTitle}
                  style={{
                    padding: '0.25rem 0.5rem',
                    background: 'rgba(34, 197, 94, 0.2)',
                    border: '1px solid rgba(34, 197, 94, 0.3)',
                    borderRadius: '0.25rem',
                    color: '#22c55e',
                    cursor: 'pointer',
                    fontSize: '0.75rem',
                    fontWeight: '500'
                  }}
                >
                  ➕ 追加
                </button>
              </div>
              {batchTitles.map((batchTitle, index) => (
                <div key={index} style={{
                  display: 'flex',
                  gap: '0.5rem',
                  marginBottom: '0.5rem'
                }}>
                  <input
                    type="text"
                    value={batchTitle}
                    onChange={(e) => updateBatchTitle(index, e.target.value)}
                    placeholder={`${selectedTemplate.titlePlaceholder} ${index + 1}`}
                    style={{
                      flex: 1,
                      padding: '0.75rem',
                      background: 'rgba(255, 255, 255, 0.05)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      borderRadius: '0.5rem',
                      color: '#ffffff',
                      fontSize: '0.875rem'
                    }}
                  />
                  {batchTitles.length > 1 && (
                    <button
                      onClick={() => removeBatchTitle(index)}
                      style={{
                        padding: '0.75rem',
                        background: 'rgba(239, 68, 68, 0.2)',
                        border: '1px solid rgba(239, 68, 68, 0.3)',
                        borderRadius: '0.5rem',
                        color: '#ef4444',
                        cursor: 'pointer',
                        fontSize: '0.875rem'
                      }}
                    >
                      ✕
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Custom Settings */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '1rem',
            marginBottom: '2rem'
          }}>
            <div>
              <label style={{
                display: 'block',
                fontSize: '0.875rem',
                fontWeight: '500',
                color: '#a1a1aa',
                marginBottom: '0.5rem'
              }}>
                優先度 (デフォルト: {selectedTemplate.priority})
              </label>
              <select
                value={customPriority || ''}
                onChange={(e) => setCustomPriority(e.target.value || null)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '0.5rem',
                  color: '#ffffff',
                  fontSize: '0.875rem'
                }}
              >
                <option value="">デフォルト ({selectedTemplate.priority})</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
            <div>
              <label style={{
                display: 'block',
                fontSize: '0.875rem',
                fontWeight: '500',
                color: '#a1a1aa',
                marginBottom: '0.5rem'
              }}>
                見積時間 (デフォルト: {selectedTemplate.estimatedHours}h)
              </label>
              <input
                type="number"
                value={customEstimate || ''}
                onChange={(e) => setCustomEstimate(e.target.value ? parseFloat(e.target.value) : null)}
                placeholder={selectedTemplate.estimatedHours.toString()}
                min="0.5"
                max="40"
                step="0.5"
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '0.5rem',
                  color: '#ffffff',
                  fontSize: '0.875rem'
                }}
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div style={{
            display: 'flex',
            gap: '1rem',
            justifyContent: 'flex-end'
          }}>
            <button
              onClick={onClose}
              style={{
                padding: '0.75rem 1.5rem',
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                borderRadius: '0.5rem',
                color: '#a1a1aa',
                cursor: 'pointer',
                fontSize: '0.875rem',
                fontWeight: '500'
              }}
            >
              キャンセル
            </button>
            <button
              onClick={batchMode ? createBatchIssues : createIssue}
              disabled={isCreating || (!batchMode && !title.trim()) || (batchMode && batchTitles.filter(t => t.trim()).length === 0)}
              style={{
                padding: '0.75rem 1.5rem',
                background: isCreating || (!batchMode && !title.trim()) || (batchMode && batchTitles.filter(t => t.trim()).length === 0)
                  ? 'rgba(107, 114, 128, 0.2)'
                  : 'rgba(34, 197, 94, 0.2)',
                border: `1px solid ${isCreating || (!batchMode && !title.trim()) || (batchMode && batchTitles.filter(t => t.trim()).length === 0)
                  ? 'rgba(107, 114, 128, 0.3)'
                  : 'rgba(34, 197, 94, 0.3)'}`,
                borderRadius: '0.5rem',
                color: isCreating || (!batchMode && !title.trim()) || (batchMode && batchTitles.filter(t => t.trim()).length === 0)
                  ? '#6b7280'
                  : '#22c55e',
                cursor: isCreating || (!batchMode && !title.trim()) || (batchMode && batchTitles.filter(t => t.trim()).length === 0)
                  ? 'not-allowed'
                  : 'pointer',
                fontSize: '0.875rem',
                fontWeight: '500'
              }}
            >
              {isCreating 
                ? '作成中...' 
                : batchMode 
                  ? `${batchTitles.filter(t => t.trim()).length}件のIssueを作成`
                  : 'Issueを作成'
              }
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default RapidIssueCreator;