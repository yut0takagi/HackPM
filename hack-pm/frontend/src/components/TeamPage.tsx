import React, { useState } from 'react';

interface TeamMember {
  id: number;
  name: string;
  role: string;
  email: string;
  skills: string[];
  avatar: string;
  tasksAssigned: number;
  tasksCompleted: number;
}

const TeamPage: React.FC = () => {
  const [members] = useState<TeamMember[]>([
    {
      id: 1,
      name: '田中太郎',
      role: 'フロントエンドエンジニア',
      email: 'tanaka@example.com',
      skills: ['React', 'TypeScript', 'CSS'],
      avatar: '👨‍💻',
      tasksAssigned: 3,
      tasksCompleted: 2
    },
    {
      id: 2,
      name: '佐藤花子',
      role: 'バックエンドエンジニア',
      email: 'sato@example.com',
      skills: ['Go', 'PostgreSQL', 'Docker'],
      avatar: '👩‍💻',
      tasksAssigned: 2,
      tasksCompleted: 1
    },
    {
      id: 3,
      name: '鈴木一郎',
      role: 'フルスタックエンジニア',
      email: 'suzuki@example.com',
      skills: ['Python', 'FastAPI', 'React'],
      avatar: '👨‍🔬',
      tasksAssigned: 2,
      tasksCompleted: 2
    },
    {
      id: 4,
      name: '高橋美咲',
      role: 'データベースエンジニア',
      email: 'takahashi@example.com',
      skills: ['PostgreSQL', 'SQL', 'データ設計'],
      avatar: '👩‍🔬',
      tasksAssigned: 1,
      tasksCompleted: 0
    },
    {
      id: 5,
      name: '山田健太',
      role: 'UIデザイナー',
      email: 'yamada@example.com',
      skills: ['UI/UX', 'Figma', 'デザインシステム'],
      avatar: '🎨',
      tasksAssigned: 1,
      tasksCompleted: 1
    }
  ]);

  const getCompletionRate = (member: TeamMember) => {
    if (member.tasksAssigned === 0) return 0;
    return Math.round((member.tasksCompleted / member.tasksAssigned) * 100);
  };

  const totalTasks = members.reduce((sum, member) => sum + member.tasksAssigned, 0);
  const completedTasks = members.reduce((sum, member) => sum + member.tasksCompleted, 0);
  const overallProgress = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  return (
    <div style={{ 
      padding: '0',
      background: 'linear-gradient(135deg, #000000 0%, #1a1a1a 100%)',
      minHeight: '100vh'
    }}>
      <section style={{ 
        padding: '8rem 2rem 4rem 2rem', 
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        <h1 style={{ 
          fontSize: '3.5rem', 
          fontWeight: '700', 
          color: '#ffffff', 
          marginBottom: '1rem',
          letterSpacing: '-0.02em',
          textAlign: 'center'
        }}>
          チームの
          <br />
          <span style={{ 
            background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            パフォーマンス
          </span>
        </h1>
        <p style={{ 
          color: '#a1a1aa', 
          margin: '0 auto',
          fontSize: '1.2rem',
          maxWidth: '600px',
          lineHeight: '1.6',
          textAlign: 'center'
        }}>
          チームメンバーの情報とタスクの進捗を管理
        </p>
      </section>

      {/* Team Stats */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
        gap: '1.5rem',
        marginBottom: '2rem'
      }}>
        <div style={{
          backgroundColor: '#1f2937',
          padding: '1.5rem',
          borderRadius: '0.75rem',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.3)',
          border: '1px solid #374151',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#60a5fa', marginBottom: '0.5rem' }}>
            {members.length}
          </div>
          <div style={{ color: '#9ca3af', fontSize: '0.875rem' }}>チームメンバー</div>
        </div>

        <div style={{
          backgroundColor: '#1f2937',
          padding: '1.5rem',
          borderRadius: '0.75rem',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.3)',
          border: '1px solid #374151',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#34d399', marginBottom: '0.5rem' }}>
            {completedTasks}
          </div>
          <div style={{ color: '#9ca3af', fontSize: '0.875rem' }}>完了タスク</div>
        </div>

        <div style={{
          backgroundColor: '#1f2937',
          padding: '1.5rem',
          borderRadius: '0.75rem',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.3)',
          border: '1px solid #374151',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#fbbf24', marginBottom: '0.5rem' }}>
            {totalTasks}
          </div>
          <div style={{ color: '#9ca3af', fontSize: '0.875rem' }}>総タスク数</div>
        </div>

        <div style={{
          backgroundColor: '#1f2937',
          padding: '1.5rem',
          borderRadius: '0.75rem',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.3)',
          border: '1px solid #374151',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#a78bfa', marginBottom: '0.5rem' }}>
            {overallProgress}%
          </div>
          <div style={{ color: '#9ca3af', fontSize: '0.875rem' }}>全体進捗</div>
        </div>
      </div>

      {/* Team Members Grid */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', 
        gap: '1.5rem' 
      }}>
        {members.map((member) => {
          const completionRate = getCompletionRate(member);
          
          return (
            <div
              key={member.id}
              style={{
                backgroundColor: '#1f2937',
                borderRadius: '0.75rem',
                padding: '1.5rem',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.3)',
                border: '1px solid #374151',
                transition: 'transform 0.2s, box-shadow 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 8px 12px -2px rgba(0, 0, 0, 0.4)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.3)';
              }}
            >
              {/* Member Header */}
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
                <div style={{ 
                  fontSize: '3rem', 
                  marginRight: '1rem',
                  width: '4rem',
                  height: '4rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  backgroundColor: '#374151',
                  borderRadius: '50%'
                }}>
                  {member.avatar}
                </div>
                <div>
                  <h3 style={{ 
                    fontSize: '1.25rem', 
                    fontWeight: '600', 
                    color: '#f8fafc', 
                    margin: '0 0 0.25rem 0' 
                  }}>
                    {member.name}
                  </h3>
                  <p style={{ 
                    color: '#9ca3af', 
                    fontSize: '0.875rem', 
                    margin: '0 0 0.25rem 0' 
                  }}>
                    {member.role}
                  </p>
                  <p style={{ 
                    color: '#6b7280', 
                    fontSize: '0.75rem', 
                    margin: 0 
                  }}>
                    {member.email}
                  </p>
                </div>
              </div>

              {/* Skills */}
              <div style={{ marginBottom: '1rem' }}>
                <h4 style={{ 
                  fontSize: '0.875rem', 
                  fontWeight: '600', 
                  color: '#e5e7eb', 
                  marginBottom: '0.5rem' 
                }}>
                  スキル
                </h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                  {member.skills.map((skill, index) => (
                    <span
                      key={index}
                      style={{
                        padding: '0.25rem 0.75rem',
                        backgroundColor: '#1e3a8a',
                        color: '#60a5fa',
                        borderRadius: '9999px',
                        fontSize: '0.75rem',
                        fontWeight: '500'
                      }}
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>

              {/* Task Progress */}
              <div>
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  marginBottom: '0.5rem'
                }}>
                  <h4 style={{ 
                    fontSize: '0.875rem', 
                    fontWeight: '600', 
                    color: '#e5e7eb', 
                    margin: 0 
                  }}>
                    タスク進捗
                  </h4>
                  <span style={{ 
                    fontSize: '0.875rem', 
                    fontWeight: '600', 
                    color: '#e5e7eb' 
                  }}>
                    {member.tasksCompleted}/{member.tasksAssigned}
                  </span>
                </div>
                
                <div style={{
                  width: '100%',
                  height: '0.5rem',
                  backgroundColor: '#4b5563',
                  borderRadius: '9999px',
                  overflow: 'hidden',
                  marginBottom: '0.5rem'
                }}>
                  <div
                    style={{
                      width: `${completionRate}%`,
                      height: '100%',
                      backgroundColor: completionRate === 100 ? '#34d399' : '#60a5fa',
                      borderRadius: '9999px',
                      transition: 'width 0.3s ease'
                    }}
                  />
                </div>
                
                <div style={{ 
                  fontSize: '0.75rem', 
                  color: '#9ca3af',
                  textAlign: 'right'
                }}>
                  {completionRate}% 完了
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default TeamPage;