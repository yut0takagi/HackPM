import React, { useState, useEffect } from 'react';
import { api, ApiError } from '../utils/api';
import CountdownTimer from './CountdownTimer';
import TimeBoxManager from './TimeBoxManager';
import RapidIssueCreator from './RapidIssueCreator';

interface TemplateData {
  template_type: 'feature' | 'bug' | 'task' | 'unknown';
  priority: 'critical' | 'high' | 'medium' | 'low';
  estimated_time?: number;
  acceptance_criteria: string[];
  technical_requirements: string[];
  branch_suggestion?: string;
  user_story?: string;
  reproduction_steps?: string[];
  expected_behavior?: string;
  actual_behavior?: string;
  environment_details?: Record<string, string>;
  task_checklist?: string[];
  dependencies?: string[];
}

interface PullRequest {
  id: number;
  number: number;
  title: string;
  body: string;
  author: string;
  author_avatar: string;
  state: 'open' | 'closed' | 'merged';
  draft: boolean;
  head_ref: string;
  base_ref: string;
  html_url: string;
  mergeable?: boolean;
  merged_at?: string;
  closed_at?: string;
  created_at: string;
  updated_at: string;
}

interface DashboardData {
  category: 'feature' | 'bug' | 'task' | 'maintenance';
  priority: 'critical' | 'high' | 'medium' | 'low';
  status: 'todo' | 'in-progress' | 'review' | 'done';
  progress_percentage: number;
  estimated_hours?: number;
  acceptance_criteria_total: number;
  acceptance_criteria_completed: number;
  has_technical_requirements: boolean;
  is_time_sensitive: boolean;
}

interface TimeBoxData {
  estimated_hours?: number;
  deadline?: string;
  time_box_start?: string;
  time_box_end?: string;
  priority_escalated: boolean;
  hackathon_phase?: string;
  hours_until_deadline?: number;
  is_overdue: boolean;
  time_remaining_percentage?: number;
}

interface Issue {
  id: number;
  number: number;
  title: string;
  body: string;
  author: string;
  author_avatar: string;
  state: 'open' | 'closed';
  labels: string[];
  assignees: string[];
  milestone: string | null;
  html_url: string;
  closed_at: string | null;
  created_at: string;
  updated_at: string;
  template_data?: TemplateData;
  dashboard_data?: DashboardData;
  timebox_data?: TimeBoxData;
}

interface Branch {
  id: number;
  name: string;
  head_sha: string;
  is_default: boolean;
  is_protected: boolean;
  last_commit_message: string | null;
  last_commit_author: string | null;
  last_commit_date: string | null;
  pushed_at: string | null;
  updated_at: string;
}

interface Repository {
  id: number;
  full_name: string;
  name: string;
  owner: string;
  description: string;
  html_url: string;
  default_branch: string;
}

const FeatureList: React.FC = () => {
  const [issues, setIssues] = useState<Issue[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [pullRequests, setPullRequests] = useState<PullRequest[]>([]);
  const [repository, setRepository] = useState<Repository | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [expandedIssues, setExpandedIssues] = useState<Set<number>>(new Set());
  const [showTimeBoxManager, setShowTimeBoxManager] = useState(false);
  const [timeFilter, setTimeFilter] = useState<string>('all'); // all, urgent, overdue, today
  const [showRapidCreator, setShowRapidCreator] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setError(null);
      
      // Get repository info
      const repos = await api.getRepositories();
      if (repos.length > 0) {
        const repo = repos[0]; // Get first repository (Keel)
        setRepository(repo);
        
        // Get issues, branches, and PRs for the repository
        const [issuesData, branchesData, pullRequestsData] = await Promise.all([
          api.getRepositoryIssues(repo.id, 'all', 100, true), // Include template data
          api.getRepositoryBranches(repo.id, 50),
          api.getRepositoryPulls(repo.id, 'all', 50)
        ]);
        
        setIssues(issuesData);
        setBranches(branchesData);
        setPullRequests(pullRequestsData);
      }
    } catch (err) {
      console.error('Failed to fetch data:', err);
      if (err instanceof ApiError) {
        setError(`データの取得に失敗しました (${err.status}): ${err.message}`);
      } else {
        setError(err instanceof Error ? err.message : 'データの取得に失敗しました');
      }
    } finally {
      setLoading(false);
    }
  };

  const getIssueStatus = (issue: Issue) => {
    if (issue.state === 'closed') return 'done';
    
    // Use dashboard data status if available
    if (issue.dashboard_data?.status) {
      return issue.dashboard_data.status;
    }
    
    // Check labels for status
    const labels = issue.labels.map(l => l.toLowerCase());
    if (labels.includes('in progress') || labels.includes('in-progress')) return 'in-progress';
    if (labels.includes('review') || labels.includes('needs review')) return 'review';
    
    return 'todo';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'todo': return { bg: 'rgba(251, 191, 36, 0.1)', text: '#fbbf24', border: '#f59e0b' };
      case 'in-progress': return { bg: 'rgba(59, 130, 246, 0.1)', text: '#60a5fa', border: '#3b82f6' };
      case 'review': return { bg: 'rgba(168, 85, 247, 0.1)', text: '#a855f7', border: '#8b5cf6' };
      case 'done': return { bg: 'rgba(34, 197, 94, 0.1)', text: '#34d399', border: '#10b981' };
      default: return { bg: 'rgba(107, 114, 128, 0.1)', text: '#9ca3af', border: '#6b7280' };
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'todo': return '📋 未着手';
      case 'in-progress': return '🔄 進行中';
      case 'review': return '👀 レビュー';
      case 'done': return '✅ 完了';
      default: return status;
    }
  };

  const getIssuePriority = (issue: Issue) => {
    // Use template data priority if available
    if (issue.template_data?.priority) {
      return issue.template_data.priority;
    }
    
    // Fall back to label-based detection
    const labelNames = issue.labels.map(l => l.toLowerCase());
    if (labelNames.includes('critical') || labelNames.includes('urgent')) return 'critical';
    if (labelNames.includes('high') || labelNames.includes('important')) return 'high';
    if (labelNames.includes('medium')) return 'medium';
    return 'low';
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return { bg: 'rgba(239, 68, 68, 0.1)', text: '#ef4444', border: '#dc2626' };
      case 'high': return { bg: 'rgba(245, 158, 11, 0.1)', text: '#f59e0b', border: '#d97706' };
      case 'medium': return { bg: 'rgba(59, 130, 246, 0.1)', text: '#3b82f6', border: '#2563eb' };
      case 'low': return { bg: 'rgba(107, 114, 128, 0.1)', text: '#6b7280', border: '#4b5563' };
      default: return { bg: 'rgba(107, 114, 128, 0.1)', text: '#6b7280', border: '#4b5563' };
    }
  };

  const getTemplateTypeInfo = (templateType: string) => {
    switch (templateType) {
      case 'feature': 
        return { 
          icon: '✨', 
          label: 'Feature', 
          color: { bg: 'rgba(34, 197, 94, 0.1)', text: '#22c55e', border: '#16a34a' }
        };
      case 'bug': 
        return { 
          icon: '🐛', 
          label: 'Bug', 
          color: { bg: 'rgba(239, 68, 68, 0.1)', text: '#ef4444', border: '#dc2626' }
        };
      case 'task': 
        return { 
          icon: '📋', 
          label: 'Task', 
          color: { bg: 'rgba(168, 85, 247, 0.1)', text: '#a855f7', border: '#8b5cf6' }
        };
      default: 
        return { 
          icon: '📄', 
          label: 'Issue', 
          color: { bg: 'rgba(107, 114, 128, 0.1)', text: '#6b7280', border: '#4b5563' }
        };
    }
  };

  const getRelatedBranch = (issue: Issue) => {
    const issueNumber = issue.number;
    return branches.find(branch => 
      branch.name.includes(`${issueNumber}`) || 
      branch.name.includes(issue.title.toLowerCase().replace(/\s+/g, '-').substring(0, 20))
    );
  };

  const toggleIssueExpansion = (issueId: number) => {
    setExpandedIssues(prev => {
      const newSet = new Set(prev);
      if (newSet.has(issueId)) {
        newSet.delete(issueId);
      } else {
        newSet.add(issueId);
      }
      return newSet;
    });
  };

  const getRelatedPRs = (issue: Issue): PullRequest[] => {
    const issueNumber = issue.number;
    return pullRequests.filter(pr => {
      // Check if PR title or body mentions the issue number
      const titleMatch = pr.title.toLowerCase().includes(`#${issueNumber}`) || 
                        pr.title.toLowerCase().includes(`issue ${issueNumber}`);
      const bodyMatch = pr.body && (
        pr.body.includes(`#${issueNumber}`) ||
        pr.body.includes(`fixes #${issueNumber}`) ||
        pr.body.includes(`closes #${issueNumber}`) ||
        pr.body.includes(`resolves #${issueNumber}`)
      );
      
      // Check if branch name suggests it's related to this issue
      const branchMatch = pr.head_ref.includes(`${issueNumber}`) ||
                         pr.head_ref.includes(issue.title.toLowerCase().replace(/\s+/g, '-').substring(0, 20));
      
      return titleMatch || bodyMatch || branchMatch;
    });
  };

  const getPRStatusInfo = (pr: PullRequest) => {
    if (pr.state === 'merged') {
      return {
        icon: '✅',
        label: 'Merged',
        color: { bg: 'rgba(34, 197, 94, 0.1)', text: '#22c55e', border: '#16a34a' }
      };
    } else if (pr.state === 'closed') {
      return {
        icon: '❌',
        label: 'Closed',
        color: { bg: 'rgba(107, 114, 128, 0.1)', text: '#6b7280', border: '#4b5563' }
      };
    } else if (pr.draft) {
      return {
        icon: '📝',
        label: 'Draft',
        color: { bg: 'rgba(245, 158, 11, 0.1)', text: '#f59e0b', border: '#d97706' }
      };
    } else {
      return {
        icon: '🔄',
        label: 'Open',
        color: { bg: 'rgba(59, 130, 246, 0.1)', text: '#3b82f6', border: '#2563eb' }
      };
    }
  };

  const checkBranchNamingCompliance = (branchName: string, issueNumber: number) => {
    // Check if branch follows naming conventions
    const patterns = [
      new RegExp(`^feature/${issueNumber}-(.+)$`, 'i'),
      new RegExp(`^feat/${issueNumber}-(.+)$`, 'i'),
      new RegExp(`^bugfix/${issueNumber}-(.+)$`, 'i'),
      new RegExp(`^bug/${issueNumber}-(.+)$`, 'i'),
      new RegExp(`^fix/${issueNumber}-(.+)$`, 'i'),
      new RegExp(`^hotfix/${issueNumber}-(.+)$`, 'i'),
      new RegExp(`^chore/${issueNumber}-(.+)$`, 'i'),
      new RegExp(`^${issueNumber}-(.+)$`, 'i')
    ];

    const isCompliant = patterns.some(pattern => pattern.test(branchName));
    
    // Extract branch type
    let branchType = 'unknown';
    if (branchName.toLowerCase().includes('feature') || branchName.toLowerCase().includes('feat')) {
      branchType = 'feature';
    } else if (branchName.toLowerCase().includes('bug') || branchName.toLowerCase().includes('fix')) {
      branchType = 'bugfix';
    } else if (branchName.toLowerCase().includes('hotfix')) {
      branchType = 'hotfix';
    } else if (branchName.toLowerCase().includes('chore')) {
      branchType = 'chore';
    }

    return { isCompliant, branchType };
  };

  const getBranchTypeInfo = (branchType: string, isCompliant: boolean) => {
    const baseInfo = {
      feature: { icon: '✨', label: 'Feature' },
      bugfix: { icon: '🐛', label: 'Bugfix' },
      hotfix: { icon: '🚨', label: 'Hotfix' },
      chore: { icon: '🔧', label: 'Chore' },
      unknown: { icon: '❓', label: 'Unknown' }
    };

    const info = baseInfo[branchType as keyof typeof baseInfo] || baseInfo.unknown;
    
    return {
      ...info,
      color: isCompliant 
        ? { bg: 'rgba(34, 197, 94, 0.1)', text: '#22c55e', border: '#16a34a' }
        : { bg: 'rgba(245, 158, 11, 0.1)', text: '#f59e0b', border: '#d97706' }
    };
  };

  const getWorkflowStatus = (issue: Issue, relatedBranch: Branch | undefined, relatedPRs: PullRequest[]) => {
    const steps = [
      { 
        name: 'Issue Created', 
        completed: true, 
        icon: '📝',
        color: '#22c55e'
      },
      { 
        name: 'Branch Created', 
        completed: !!relatedBranch, 
        icon: '🌿',
        color: relatedBranch ? '#22c55e' : '#6b7280'
      },
      { 
        name: 'PR Created', 
        completed: relatedPRs.length > 0, 
        icon: '🔄',
        color: relatedPRs.length > 0 ? '#22c55e' : '#6b7280'
      },
      { 
        name: 'PR Merged', 
        completed: relatedPRs.some(pr => pr.state === 'merged'), 
        icon: '✅',
        color: relatedPRs.some(pr => pr.state === 'merged') ? '#22c55e' : '#6b7280'
      }
    ];

    return steps;
  };

  const applyTimeFilter = (issueList: Issue[]) => {
    if (timeFilter === 'all') return issueList;
    
    const now = new Date();
    const todayEnd = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59);
    
    return issueList.filter(issue => {
      if (!issue.timebox_data) return timeFilter === 'all';
      
      switch (timeFilter) {
        case 'urgent':
          return issue.timebox_data.hours_until_deadline !== undefined && 
                 issue.timebox_data.hours_until_deadline <= 6 && 
                 issue.timebox_data.hours_until_deadline > 0;
        case 'overdue':
          return issue.timebox_data.is_overdue;
        case 'today':
          return issue.timebox_data.deadline && 
                 new Date(issue.timebox_data.deadline) <= todayEnd;
        default:
          return true;
      }
    });
  };

  const statusFilteredIssues = filterStatus === 'all' 
    ? issues 
    : issues.filter(issue => getIssueStatus(issue) === filterStatus);
  
  const filteredIssues = applyTimeFilter(statusFilteredIssues);

  const statusCounts = {
    all: issues.length,
    todo: issues.filter(issue => getIssueStatus(issue) === 'todo').length,
    'in-progress': issues.filter(issue => getIssueStatus(issue) === 'in-progress').length,
    review: issues.filter(issue => getIssueStatus(issue) === 'review').length,
    done: issues.filter(issue => getIssueStatus(issue) === 'done').length,
  };

  const timeCounts = {
    all: issues.length,
    urgent: issues.filter(issue => 
      issue.timebox_data?.hours_until_deadline !== undefined && 
      issue.timebox_data.hours_until_deadline <= 6 && 
      issue.timebox_data.hours_until_deadline > 0
    ).length,
    overdue: issues.filter(issue => issue.timebox_data?.is_overdue).length,
    today: issues.filter(issue => {
      if (!issue.timebox_data?.deadline) return false;
      const now = new Date();
      const todayEnd = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59);
      return new Date(issue.timebox_data.deadline) <= todayEnd;
    }).length,
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
        <div style={{
          display: 'inline-block',
          padding: '0.5rem 1.5rem',
          background: 'rgba(59, 130, 246, 0.1)',
          border: '1px solid rgba(59, 130, 246, 0.3)',
          borderRadius: '2rem',
          color: '#3b82f6',
          fontSize: '0.9rem',
          fontWeight: '500',
          marginBottom: '2rem'
        }}>
          🎯 Issue-Based Task Management
        </div>
        <h1 style={{ 
          fontSize: '3.5rem', 
          fontWeight: '700', 
          color: '#ffffff', 
          marginBottom: '1rem',
          letterSpacing: '-0.02em',
          lineHeight: '1.1'
        }}>
          タスク管理
          <br />
          <span style={{ 
            background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            & ブランチ戦略
          </span>
        </h1>
        <p style={{ 
          color: '#a1a1aa', 
          margin: '0 auto 2rem auto',
          fontSize: '1.2rem',
          maxWidth: '600px',
          lineHeight: '1.6'
        }}>
          GitHub Issuesと連携したタスク管理。
          <br />
          ブランチ戦略に基づく効率的な開発フローを実現。
        </p>
        
        {repository && (
          <div style={{
            display: 'flex',
            gap: '1rem',
            justifyContent: 'center',
            marginTop: '2rem',
            flexWrap: 'wrap'
          }}>
            <a
              href={`${repository.html_url}/issues`}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.75rem 1.5rem',
                background: 'rgba(34, 197, 94, 0.1)',
                border: '1px solid rgba(34, 197, 94, 0.3)',
                borderRadius: '0.75rem',
                color: '#22c55e',
                textDecoration: 'none',
                fontSize: '0.95rem',
                fontWeight: '500',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(34, 197, 94, 0.15)';
                e.currentTarget.style.transform = 'translateY(-2px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(34, 197, 94, 0.1)';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              ➕ 新しいIssueを作成
            </a>
            <a
              href={`${repository.html_url}/branches`}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.75rem 1.5rem',
                background: 'rgba(168, 85, 247, 0.1)',
                border: '1px solid rgba(168, 85, 247, 0.3)',
                borderRadius: '0.75rem',
                color: '#a855f7',
                textDecoration: 'none',
                fontSize: '0.95rem',
                fontWeight: '500',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(168, 85, 247, 0.15)';
                e.currentTarget.style.transform = 'translateY(-2px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(168, 85, 247, 0.1)';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              🌿 ブランチ管理
            </a>
            <button
              onClick={() => setShowTimeBoxManager(true)}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.75rem 1.5rem',
                background: 'rgba(59, 130, 246, 0.1)',
                border: '1px solid rgba(59, 130, 246, 0.3)',
                borderRadius: '0.75rem',
                color: '#3b82f6',
                cursor: 'pointer',
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
              ⏱️ タイムボックス管理
            </button>
            <button
              onClick={() => setShowRapidCreator(true)}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.75rem 1.5rem',
                background: 'rgba(245, 158, 11, 0.1)',
                border: '1px solid rgba(245, 158, 11, 0.3)',
                borderRadius: '0.75rem',
                color: '#f59e0b',
                cursor: 'pointer',
                fontSize: '0.95rem',
                fontWeight: '500',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(245, 158, 11, 0.15)';
                e.currentTarget.style.transform = 'translateY(-2px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(245, 158, 11, 0.1)';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              ⚡ クイック作成
            </button>
          </div>
        )}
      </section>

      {/* Loading and Error States */}
      {loading && (
        <section style={{ 
          padding: '4rem 2rem',
          textAlign: 'center',
          maxWidth: '1200px',
          margin: '0 auto'
        }}>
          <div style={{ color: '#a1a1aa', fontSize: '1.1rem' }}>
            タスクデータを読み込み中...
          </div>
        </section>
      )}

      {error && (
        <section style={{ 
          padding: '4rem 2rem',
          textAlign: 'center',
          maxWidth: '1200px',
          margin: '0 auto'
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
              データの読み込みに失敗しました
            </h3>
            <p style={{ color: '#a1a1aa', marginBottom: '1.5rem' }}>
              {error}
            </p>
            <button
              onClick={fetchData}
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
      )}

      {/* Time Box Manager Modal */}
      {showTimeBoxManager && repository && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '2rem'
        }}>
          <div style={{
            background: 'rgba(26, 26, 26, 0.95)',
            backdropFilter: 'blur(20px)',
            borderRadius: '1rem',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            maxWidth: '1200px',
            width: '100%',
            maxHeight: '90vh',
            overflow: 'auto',
            position: 'relative'
          }}>
            <button
              onClick={() => setShowTimeBoxManager(false)}
              style={{
                position: 'absolute',
                top: '1rem',
                right: '1rem',
                background: 'rgba(239, 68, 68, 0.2)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                borderRadius: '0.5rem',
                color: '#ef4444',
                cursor: 'pointer',
                padding: '0.5rem',
                fontSize: '1.25rem',
                zIndex: 1001
              }}
            >
              ✕
            </button>
            <TimeBoxManager repositoryId={repository.id} />
          </div>
        </div>
      )}

      {/* Rapid Issue Creator Modal */}
      {showRapidCreator && repository && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '2rem'
        }}>
          <RapidIssueCreator
            repositoryId={repository.id}
            onClose={() => setShowRapidCreator(false)}
            onIssueCreated={fetchData}
          />
        </div>
      )}

      {/* Filter Section */}
      {!loading && !error && (
        <section style={{ 
          padding: '0 2rem 4rem 2rem',
          maxWidth: '1200px',
          margin: '0 auto'
        }}>
          {/* Status Filter */}
          <div style={{ marginBottom: '1.5rem' }}>
            <h3 style={{
              fontSize: '1rem',
              fontWeight: '600',
              color: '#ffffff',
              marginBottom: '0.75rem',
              textAlign: 'center'
            }}>
              ステータス別フィルター
            </h3>
            <div style={{ 
              display: 'flex', 
              gap: '0.75rem', 
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
                  {status === 'all' ? '📋 全て' : 
                   status === 'todo' ? '📋 未着手' :
                   status === 'in-progress' ? '🔄 進行中' :
                   status === 'review' ? '👀 レビュー' : '✅ 完了'} ({count})
                </button>
              ))}
            </div>
          </div>

          {/* Time-based Filter */}
          <div style={{ marginBottom: '3rem' }}>
            <h3 style={{
              fontSize: '1rem',
              fontWeight: '600',
              color: '#ffffff',
              marginBottom: '0.75rem',
              textAlign: 'center'
            }}>
              ⏰ 時間別フィルター
            </h3>
            <div style={{ 
              display: 'flex', 
              gap: '0.75rem', 
              flexWrap: 'wrap',
              justifyContent: 'center'
            }}>
              {Object.entries(timeCounts).map(([timeType, count]) => (
                <button
                  key={timeType}
                  onClick={() => setTimeFilter(timeType)}
                  style={{
                    padding: '0.75rem 1.5rem',
                    borderRadius: '2rem',
                    border: 'none',
                    background: timeFilter === timeType 
                      ? 'rgba(59, 130, 246, 0.3)' 
                      : 'rgba(59, 130, 246, 0.1)',
                    backdropFilter: 'blur(10px)',
                    color: timeFilter === timeType ? '#ffffff' : '#60a5fa',
                    cursor: 'pointer',
                    fontSize: '0.95rem',
                    fontWeight: '500',
                    transition: 'all 0.3s ease'
                  }}
                  onMouseEnter={(e) => {
                    if (timeFilter !== timeType) {
                      e.currentTarget.style.background = 'rgba(59, 130, 246, 0.2)';
                      e.currentTarget.style.color = '#ffffff';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (timeFilter !== timeType) {
                      e.currentTarget.style.background = 'rgba(59, 130, 246, 0.1)';
                      e.currentTarget.style.color = '#60a5fa';
                    }
                  }}
                >
                  {timeType === 'all' ? '⏱️ 全て' : 
                   timeType === 'urgent' ? '🚨 緊急' :
                   timeType === 'overdue' ? '⏰ 期限切れ' : '📅 今日'} ({count})
                </button>
              ))}
            </div>
          </div>

          {/* Issues Table */}
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
                    }}>Issue / タスク</th>
                    <th style={{ 
                      padding: '1.5rem 1rem', 
                      textAlign: 'left', 
                      fontWeight: '600', 
                      color: '#ffffff',
                      fontSize: '0.95rem'
                    }}>タイプ</th>
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
                    }}>優先度</th>
                    <th style={{ 
                      padding: '1.5rem 1rem', 
                      textAlign: 'left', 
                      fontWeight: '600', 
                      color: '#ffffff',
                      fontSize: '0.95rem'
                    }}>ブランチ</th>
                    <th style={{ 
                      padding: '1.5rem 1rem', 
                      textAlign: 'left', 
                      fontWeight: '600', 
                      color: '#ffffff',
                      fontSize: '0.95rem'
                    }}>PR状況</th>
                    <th style={{ 
                      padding: '1.5rem 1rem', 
                      textAlign: 'left', 
                      fontWeight: '600', 
                      color: '#ffffff',
                      fontSize: '0.95rem'
                    }}>⏰ 期限</th>
                    <th style={{ 
                      padding: '1.5rem 1rem', 
                      textAlign: 'left', 
                      fontWeight: '600', 
                      color: '#ffffff',
                      fontSize: '0.95rem'
                    }}>作成日</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredIssues.length === 0 ? (
                    <tr>
                      <td colSpan={8} style={{ 
                        padding: '3rem', 
                        textAlign: 'center', 
                        color: '#a1a1aa' 
                      }}>
                        {filterStatus === 'all' && timeFilter === 'all'
                          ? 'Issueが見つかりませんでした。新しいIssueを作成してタスク管理を開始しましょう。'
                          : `フィルター条件に一致するIssueはありません。`
                        }
                      </td>
                    </tr>
                  ) : (
                    filteredIssues.map((issue, index) => {
                      const status = getIssueStatus(issue);
                      const statusColor = getStatusColor(status);
                      const priority = getIssuePriority(issue);
                      const priorityColor = getPriorityColor(priority);
                      const templateType = issue.template_data?.template_type || 'unknown';
                      const templateInfo = getTemplateTypeInfo(templateType);
                      const relatedBranch = getRelatedBranch(issue);
                      const relatedPRs = getRelatedPRs(issue);
                      
                      return (
                        <tr 
                          key={issue.id}
                          style={{ 
                            borderBottom: index < filteredIssues.length - 1 ? '1px solid rgba(255, 255, 255, 0.1)' : 'none',
                            transition: 'background-color 0.3s ease'
                          }}
                          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.05)'}
                          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                        >
                          <td style={{ padding: '1.5rem 1rem' }}>
                            <div>
                              <div style={{ 
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem',
                                marginBottom: '0.5rem'
                              }}>
                                <a
                                  href={issue.html_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  style={{
                                    fontWeight: '600', 
                                    color: '#ffffff', 
                                    fontSize: '1rem',
                                    textDecoration: 'none'
                                  }}
                                  onMouseEnter={(e) => e.currentTarget.style.color = '#3b82f6'}
                                  onMouseLeave={(e) => e.currentTarget.style.color = '#ffffff'}
                                >
                                  #{issue.number} {issue.title}
                                </a>
                                {(issue.template_data?.acceptance_criteria?.length || 
                                  issue.template_data?.technical_requirements?.length) && (
                                  <button
                                    onClick={() => toggleIssueExpansion(issue.id)}
                                    style={{
                                      background: 'none',
                                      border: 'none',
                                      color: '#a1a1aa',
                                      cursor: 'pointer',
                                      fontSize: '0.8rem',
                                      padding: '0.25rem',
                                      borderRadius: '0.25rem',
                                      transition: 'color 0.2s ease'
                                    }}
                                    onMouseEnter={(e) => e.currentTarget.style.color = '#ffffff'}
                                    onMouseLeave={(e) => e.currentTarget.style.color = '#a1a1aa'}
                                  >
                                    {expandedIssues.has(issue.id) ? '▼' : '▶'}
                                  </button>
                                )}
                              </div>
                              
                              {/* User Story Display */}
                              {issue.template_data?.user_story && (
                                <div style={{ 
                                  fontSize: '0.9rem', 
                                  color: '#60a5fa',
                                  lineHeight: '1.5',
                                  marginBottom: '0.5rem',
                                  fontStyle: 'italic'
                                }}>
                                  {issue.template_data.user_story}
                                </div>
                              )}
                              
                              <div style={{ 
                                fontSize: '0.9rem', 
                                color: '#a1a1aa',
                                lineHeight: '1.5',
                                marginBottom: '0.5rem'
                              }}>
                                {issue.body ? issue.body.substring(0, 100) + (issue.body.length > 100 ? '...' : '') : 'No description'}
                              </div>
                              
                              {/* Progress Bar for Acceptance Criteria */}
                              {issue.dashboard_data && issue.dashboard_data.acceptance_criteria_total > 0 && (
                                <div style={{ marginBottom: '0.5rem' }}>
                                  <div style={{ 
                                    display: 'flex', 
                                    justifyContent: 'space-between', 
                                    alignItems: 'center',
                                    marginBottom: '0.25rem'
                                  }}>
                                    <span style={{ fontSize: '0.8rem', color: '#a1a1aa' }}>
                                      進捗: {issue.dashboard_data.acceptance_criteria_completed}/{issue.dashboard_data.acceptance_criteria_total}
                                    </span>
                                    <span style={{ fontSize: '0.8rem', color: '#a1a1aa' }}>
                                      {Math.round(issue.dashboard_data.progress_percentage)}%
                                    </span>
                                  </div>
                                  <div style={{
                                    width: '100%',
                                    height: '4px',
                                    background: 'rgba(255, 255, 255, 0.1)',
                                    borderRadius: '2px',
                                    overflow: 'hidden'
                                  }}>
                                    <div style={{
                                      width: `${issue.dashboard_data.progress_percentage}%`,
                                      height: '100%',
                                      background: issue.dashboard_data.progress_percentage === 100 
                                        ? 'linear-gradient(90deg, #22c55e 0%, #16a34a 100%)'
                                        : 'linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%)',
                                      transition: 'width 0.3s ease'
                                    }} />
                                  </div>
                                </div>
                              )}
                              
                              <div style={{
                                display: 'flex',
                                gap: '0.5rem',
                                flexWrap: 'wrap'
                              }}>
                                {issue.labels.slice(0, 3).map((label, i) => (
                                  <span
                                    key={i}
                                    style={{
                                      padding: '0.25rem 0.5rem',
                                      background: 'rgba(107, 114, 128, 0.2)',
                                      borderRadius: '0.375rem',
                                      fontSize: '0.75rem',
                                      color: '#9ca3af'
                                    }}
                                  >
                                    {label}
                                  </span>
                                ))}
                              </div>
                              
                              {/* Expandable Content */}
                              {expandedIssues.has(issue.id) && (
                                <div style={{
                                  marginTop: '1rem',
                                  padding: '1rem',
                                  background: 'rgba(0, 0, 0, 0.3)',
                                  borderRadius: '0.5rem',
                                  border: '1px solid rgba(255, 255, 255, 0.1)'
                                }}>
                                  {/* Acceptance Criteria */}
                                  {issue.template_data?.acceptance_criteria && issue.template_data.acceptance_criteria.length > 0 && (
                                    <div style={{ marginBottom: '1rem' }}>
                                      <h4 style={{ 
                                        color: '#ffffff', 
                                        fontSize: '0.9rem', 
                                        fontWeight: '600',
                                        marginBottom: '0.5rem'
                                      }}>
                                        ✅ 受け入れ条件
                                      </h4>
                                      <ul style={{ 
                                        margin: 0, 
                                        paddingLeft: '1.5rem',
                                        color: '#a1a1aa',
                                        fontSize: '0.85rem'
                                      }}>
                                        {issue.template_data.acceptance_criteria.map((criteria, i) => (
                                          <li key={i} style={{ marginBottom: '0.25rem' }}>
                                            {criteria}
                                          </li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                  
                                  {/* Technical Requirements */}
                                  {issue.template_data?.technical_requirements && issue.template_data.technical_requirements.length > 0 && (
                                    <div style={{ marginBottom: '1rem' }}>
                                      <h4 style={{ 
                                        color: '#ffffff', 
                                        fontSize: '0.9rem', 
                                        fontWeight: '600',
                                        marginBottom: '0.5rem'
                                      }}>
                                        🔧 技術要件
                                      </h4>
                                      <ul style={{ 
                                        margin: 0, 
                                        paddingLeft: '1.5rem',
                                        color: '#a1a1aa',
                                        fontSize: '0.85rem'
                                      }}>
                                        {issue.template_data.technical_requirements.map((req, i) => (
                                          <li key={i} style={{ marginBottom: '0.25rem' }}>
                                            {req}
                                          </li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                  
                                  {/* Bug-specific information */}
                                  {issue.template_data?.template_type === 'bug' && (
                                    <>
                                      {issue.template_data.reproduction_steps && issue.template_data.reproduction_steps.length > 0 && (
                                        <div style={{ marginBottom: '1rem' }}>
                                          <h4 style={{ 
                                            color: '#ffffff', 
                                            fontSize: '0.9rem', 
                                            fontWeight: '600',
                                            marginBottom: '0.5rem'
                                          }}>
                                            🔄 再現手順
                                          </h4>
                                          <ol style={{ 
                                            margin: 0, 
                                            paddingLeft: '1.5rem',
                                            color: '#a1a1aa',
                                            fontSize: '0.85rem'
                                          }}>
                                            {issue.template_data.reproduction_steps.map((step, i) => (
                                              <li key={i} style={{ marginBottom: '0.25rem' }}>
                                                {step}
                                              </li>
                                            ))}
                                          </ol>
                                        </div>
                                      )}
                                      
                                      {(issue.template_data.expected_behavior || issue.template_data.actual_behavior) && (
                                        <div style={{ 
                                          display: 'grid', 
                                          gridTemplateColumns: '1fr 1fr', 
                                          gap: '1rem',
                                          marginBottom: '1rem'
                                        }}>
                                          {issue.template_data.expected_behavior && (
                                            <div>
                                              <h4 style={{ 
                                                color: '#22c55e', 
                                                fontSize: '0.9rem', 
                                                fontWeight: '600',
                                                marginBottom: '0.5rem'
                                              }}>
                                                ✅ 期待される動作
                                              </h4>
                                              <p style={{ 
                                                margin: 0,
                                                color: '#a1a1aa',
                                                fontSize: '0.85rem'
                                              }}>
                                                {issue.template_data.expected_behavior}
                                              </p>
                                            </div>
                                          )}
                                          
                                          {issue.template_data.actual_behavior && (
                                            <div>
                                              <h4 style={{ 
                                                color: '#ef4444', 
                                                fontSize: '0.9rem', 
                                                fontWeight: '600',
                                                marginBottom: '0.5rem'
                                              }}>
                                                ❌ 実際の動作
                                              </h4>
                                              <p style={{ 
                                                margin: 0,
                                                color: '#a1a1aa',
                                                fontSize: '0.85rem'
                                              }}>
                                                {issue.template_data.actual_behavior}
                                              </p>
                                            </div>
                                          )}
                                        </div>
                                      )}
                                    </>
                                  )}
                                  
                                  {/* Task checklist */}
                                  {issue.template_data?.task_checklist && issue.template_data.task_checklist.length > 0 && (
                                    <div style={{ marginBottom: '1rem' }}>
                                      <h4 style={{ 
                                        color: '#ffffff', 
                                        fontSize: '0.9rem', 
                                        fontWeight: '600',
                                        marginBottom: '0.5rem'
                                      }}>
                                        📋 タスクチェックリスト
                                      </h4>
                                      <div style={{ 
                                        color: '#a1a1aa',
                                        fontSize: '0.85rem'
                                      }}>
                                        {issue.template_data.task_checklist.map((task, i) => (
                                          <div key={i} style={{ marginBottom: '0.25rem' }}>
                                            {task}
                                          </div>
                                        ))}
                                      </div>
                                    </div>
                                  )}
                                  
                                  {/* Estimated Time */}
                                  {issue.template_data?.estimated_time && (
                                    <div style={{
                                      display: 'inline-flex',
                                      alignItems: 'center',
                                      gap: '0.5rem',
                                      padding: '0.5rem 1rem',
                                      background: 'rgba(59, 130, 246, 0.1)',
                                      borderRadius: '1rem',
                                      border: '1px solid rgba(59, 130, 246, 0.3)',
                                      marginBottom: '1rem'
                                    }}>
                                      <span style={{ fontSize: '0.8rem' }}>⏱️</span>
                                      <span style={{ 
                                        color: '#3b82f6', 
                                        fontSize: '0.85rem',
                                        fontWeight: '500'
                                      }}>
                                        予想時間: {issue.template_data.estimated_time}時間
                                      </span>
                                    </div>
                                  )}
                                  
                                  {/* Related Pull Requests */}
                                  {relatedPRs.length > 0 && (
                                    <div style={{ marginTop: '1rem' }}>
                                      <h4 style={{ 
                                        color: '#ffffff', 
                                        fontSize: '0.9rem', 
                                        fontWeight: '600',
                                        marginBottom: '0.5rem'
                                      }}>
                                        🔄 関連プルリクエスト
                                      </h4>
                                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                        {relatedPRs.map((pr) => {
                                          const prStatus = getPRStatusInfo(pr);
                                          return (
                                            <div 
                                              key={pr.id} 
                                              style={{
                                                padding: '0.75rem',
                                                background: 'rgba(0, 0, 0, 0.2)',
                                                borderRadius: '0.5rem',
                                                border: '1px solid rgba(255, 255, 255, 0.1)'
                                              }}
                                            >
                                              <div style={{ 
                                                display: 'flex', 
                                                alignItems: 'center', 
                                                justifyContent: 'space-between',
                                                marginBottom: '0.5rem'
                                              }}>
                                                <a
                                                  href={pr.html_url}
                                                  target="_blank"
                                                  rel="noopener noreferrer"
                                                  style={{
                                                    color: '#ffffff',
                                                    textDecoration: 'none',
                                                    fontSize: '0.9rem',
                                                    fontWeight: '500'
                                                  }}
                                                  onMouseEnter={(e) => e.currentTarget.style.color = '#3b82f6'}
                                                  onMouseLeave={(e) => e.currentTarget.style.color = '#ffffff'}
                                                >
                                                  #{pr.number} {pr.title}
                                                </a>
                                                <span style={{
                                                  display: 'inline-flex',
                                                  alignItems: 'center',
                                                  gap: '0.25rem',
                                                  padding: '0.25rem 0.5rem',
                                                  borderRadius: '1rem',
                                                  fontSize: '0.75rem',
                                                  fontWeight: '500',
                                                  backgroundColor: prStatus.color.bg,
                                                  color: prStatus.color.text,
                                                  border: `1px solid ${prStatus.color.border}`
                                                }}>
                                                  <span>{prStatus.icon}</span>
                                                  {prStatus.label}
                                                </span>
                                              </div>
                                              <div style={{ 
                                                fontSize: '0.8rem', 
                                                color: '#a1a1aa',
                                                marginBottom: '0.5rem'
                                              }}>
                                                {pr.head_ref} → {pr.base_ref}
                                              </div>
                                              <div style={{ 
                                                fontSize: '0.75rem', 
                                                color: '#6b7280'
                                              }}>
                                                by {pr.author} • {new Date(pr.created_at).toLocaleDateString('ja-JP')}
                                                {pr.merged_at && (
                                                  <span style={{ color: '#22c55e', marginLeft: '0.5rem' }}>
                                                    • Merged {new Date(pr.merged_at).toLocaleDateString('ja-JP')}
                                                  </span>
                                                )}
                                              </div>
                                            </div>
                                          );
                                        })}
                                      </div>
                                    </div>
                                  )}
                                  
                                  {/* Workflow Visualization */}
                                  <div style={{ marginTop: '1rem' }}>
                                    <h4 style={{ 
                                      color: '#ffffff', 
                                      fontSize: '0.9rem', 
                                      fontWeight: '600',
                                      marginBottom: '0.75rem'
                                    }}>
                                      🔄 開発フロー
                                    </h4>
                                    <div style={{
                                      display: 'flex',
                                      alignItems: 'center',
                                      gap: '0.5rem',
                                      padding: '1rem',
                                      background: 'rgba(0, 0, 0, 0.2)',
                                      borderRadius: '0.5rem',
                                      border: '1px solid rgba(255, 255, 255, 0.1)'
                                    }}>
                                      {getWorkflowStatus(issue, relatedBranch, relatedPRs).map((step, index, array) => (
                                        <React.Fragment key={step.name}>
                                          <div style={{
                                            display: 'flex',
                                            flexDirection: 'column',
                                            alignItems: 'center',
                                            gap: '0.25rem'
                                          }}>
                                            <div style={{
                                              width: '2rem',
                                              height: '2rem',
                                              borderRadius: '50%',
                                              display: 'flex',
                                              alignItems: 'center',
                                              justifyContent: 'center',
                                              backgroundColor: step.completed 
                                                ? 'rgba(34, 197, 94, 0.2)' 
                                                : 'rgba(107, 114, 128, 0.2)',
                                              border: `2px solid ${step.color}`,
                                              fontSize: '0.8rem'
                                            }}>
                                              {step.icon}
                                            </div>
                                            <span style={{
                                              fontSize: '0.7rem',
                                              color: step.completed ? '#22c55e' : '#6b7280',
                                              fontWeight: '500',
                                              textAlign: 'center',
                                              maxWidth: '4rem'
                                            }}>
                                              {step.name}
                                            </span>
                                          </div>
                                          {index < array.length - 1 && (
                                            <div style={{
                                              flex: 1,
                                              height: '2px',
                                              backgroundColor: step.completed && array[index + 1].completed
                                                ? '#22c55e'
                                                : '#6b7280',
                                              margin: '0 0.5rem'
                                            }} />
                                          )}
                                        </React.Fragment>
                                      ))}
                                    </div>
                                    
                                    {/* Branch Naming Suggestion */}
                                    {!relatedBranch && issue.template_data?.branch_suggestion && (
                                      <div style={{
                                        marginTop: '0.75rem',
                                        padding: '0.75rem',
                                        background: 'rgba(59, 130, 246, 0.1)',
                                        borderRadius: '0.5rem',
                                        border: '1px solid rgba(59, 130, 246, 0.3)'
                                      }}>
                                        <div style={{
                                          display: 'flex',
                                          alignItems: 'center',
                                          gap: '0.5rem',
                                          marginBottom: '0.5rem'
                                        }}>
                                          <span style={{ fontSize: '0.8rem' }}>💡</span>
                                          <span style={{
                                            color: '#3b82f6',
                                            fontSize: '0.85rem',
                                            fontWeight: '500'
                                          }}>
                                            推奨ブランチ名
                                          </span>
                                        </div>
                                        <code style={{
                                          display: 'block',
                                          padding: '0.5rem',
                                          background: 'rgba(0, 0, 0, 0.3)',
                                          borderRadius: '0.25rem',
                                          color: '#a1a1aa',
                                          fontSize: '0.8rem',
                                          fontFamily: 'monospace'
                                        }}>
                                          {issue.template_data.branch_suggestion}
                                        </code>
                                      </div>
                                    )}
                                  </div>
                                </div>
                              )}
                            </div>
                          </td>
                          <td style={{ padding: '1.5rem 1rem' }}>
                            <span style={{
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '0.5rem',
                              padding: '0.5rem 1rem',
                              borderRadius: '2rem',
                              fontSize: '0.85rem',
                              fontWeight: '500',
                              backgroundColor: templateInfo.color.bg,
                              color: templateInfo.color.text,
                              border: `1px solid ${templateInfo.color.border}`
                            }}>
                              <span>{templateInfo.icon}</span>
                              {templateInfo.label}
                            </span>
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
                              {getStatusText(status)}
                            </span>
                          </td>
                          <td style={{ padding: '1.5rem 1rem' }}>
                            <span style={{
                              padding: '0.25rem 0.75rem',
                              borderRadius: '1rem',
                              fontSize: '0.8rem',
                              fontWeight: '500',
                              backgroundColor: priorityColor.bg,
                              color: priorityColor.text,
                              border: `1px solid ${priorityColor.border}`
                            }}>
                              {priority.toUpperCase()}
                            </span>
                          </td>
                          <td style={{ padding: '1.5rem 1rem' }}>
                            {relatedBranch ? (
                              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                <div style={{
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: '0.5rem'
                                }}>
                                  <span style={{ fontSize: '1rem' }}>🌿</span>
                                  <span style={{ 
                                    color: '#34d399', 
                                    fontWeight: '500',
                                    fontSize: '0.9rem'
                                  }}>
                                    {relatedBranch.name}
                                  </span>
                                </div>
                                {(() => {
                                  const compliance = checkBranchNamingCompliance(relatedBranch.name, issue.number);
                                  const branchInfo = getBranchTypeInfo(compliance.branchType, compliance.isCompliant);
                                  return (
                                    <div style={{ display: 'flex', gap: '0.25rem' }}>
                                      <span style={{
                                        display: 'inline-flex',
                                        alignItems: 'center',
                                        gap: '0.25rem',
                                        padding: '0.125rem 0.375rem',
                                        borderRadius: '0.75rem',
                                        fontSize: '0.7rem',
                                        fontWeight: '500',
                                        backgroundColor: branchInfo.color.bg,
                                        color: branchInfo.color.text,
                                        border: `1px solid ${branchInfo.color.border}`
                                      }}>
                                        <span>{branchInfo.icon}</span>
                                        {branchInfo.label}
                                      </span>
                                      {!compliance.isCompliant && (
                                        <span style={{
                                          display: 'inline-flex',
                                          alignItems: 'center',
                                          padding: '0.125rem 0.375rem',
                                          borderRadius: '0.75rem',
                                          fontSize: '0.7rem',
                                          fontWeight: '500',
                                          backgroundColor: 'rgba(245, 158, 11, 0.1)',
                                          color: '#f59e0b',
                                          border: '1px solid #d97706'
                                        }}>
                                          ⚠️ Non-compliant
                                        </span>
                                      )}
                                    </div>
                                  );
                                })()}
                              </div>
                            ) : (
                              <span style={{ 
                                color: '#6b7280', 
                                fontSize: '0.9rem',
                                fontStyle: 'italic'
                              }}>
                                ブランチなし
                              </span>
                            )}
                          </td>
                          <td style={{ padding: '1.5rem 1rem' }}>
                            {relatedPRs.length > 0 ? (
                              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                {relatedPRs.slice(0, 2).map((pr) => {
                                  const prStatus = getPRStatusInfo(pr);
                                  return (
                                    <div key={pr.id} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                      <a
                                        href={pr.html_url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        style={{
                                          display: 'inline-flex',
                                          alignItems: 'center',
                                          gap: '0.25rem',
                                          padding: '0.25rem 0.5rem',
                                          borderRadius: '1rem',
                                          fontSize: '0.75rem',
                                          fontWeight: '500',
                                          backgroundColor: prStatus.color.bg,
                                          color: prStatus.color.text,
                                          border: `1px solid ${prStatus.color.border}`,
                                          textDecoration: 'none',
                                          transition: 'opacity 0.2s ease'
                                        }}
                                        onMouseEnter={(e) => e.currentTarget.style.opacity = '0.8'}
                                        onMouseLeave={(e) => e.currentTarget.style.opacity = '1'}
                                      >
                                        <span>{prStatus.icon}</span>
                                        <span>#{pr.number}</span>
                                      </a>
                                    </div>
                                  );
                                })}
                                {relatedPRs.length > 2 && (
                                  <span style={{ 
                                    fontSize: '0.75rem', 
                                    color: '#6b7280',
                                    fontStyle: 'italic'
                                  }}>
                                    +{relatedPRs.length - 2} more
                                  </span>
                                )}
                              </div>
                            ) : (
                              <span style={{ 
                                color: '#6b7280', 
                                fontSize: '0.9rem',
                                fontStyle: 'italic'
                              }}>
                                PRなし
                              </span>
                            )}
                          </td>
                          {/* Deadline Column */}
                          <td style={{ padding: '1.5rem 1rem' }}>
                            {issue.timebox_data?.deadline ? (
                              <div style={{ minWidth: '200px' }}>
                                <CountdownTimer
                                  targetDate={issue.timebox_data.deadline}
                                  startDate={issue.timebox_data.time_box_start}
                                  label="期限まで"
                                  showProgress={!!issue.timebox_data.time_box_start}
                                />
                                {issue.timebox_data.priority_escalated && (
                                  <div style={{
                                    marginTop: '0.5rem',
                                    padding: '0.25rem 0.5rem',
                                    background: 'rgba(239, 68, 68, 0.2)',
                                    border: '1px solid rgba(239, 68, 68, 0.3)',
                                    borderRadius: '0.25rem',
                                    fontSize: '0.75rem',
                                    color: '#ef4444',
                                    textAlign: 'center'
                                  }}>
                                    🚨 自動エスカレート済み
                                  </div>
                                )}
                              </div>
                            ) : (
                              <div style={{ 
                                fontSize: '0.875rem', 
                                color: '#6b7280',
                                textAlign: 'center'
                              }}>
                                期限未設定
                              </div>
                            )}
                          </td>

                          <td style={{ padding: '1.5rem 1rem' }}>
                            <div style={{ color: '#a1a1aa', fontSize: '0.9rem' }}>
                              {new Date(issue.created_at).toLocaleDateString('ja-JP')}
                            </div>
                            <div style={{ color: '#6b7280', fontSize: '0.8rem' }}>
                              by {issue.author}
                            </div>
                            {issue.timebox_data?.estimated_hours && (
                              <div style={{
                                fontSize: '0.75rem',
                                color: '#60a5fa',
                                marginTop: '0.25rem'
                              }}>
                                見積: {issue.timebox_data.estimated_hours}時間
                              </div>
                            )}
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      )}
    </div>
  );
};

export default FeatureList;