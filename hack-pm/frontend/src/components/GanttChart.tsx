import React, { useState } from 'react';

interface GanttTask {
  id: number;
  name: string;
  assignee: string;
  startDate: string;
  endDate: string;
  progress: number;
  color: string;
}

const GanttChart: React.FC = () => {
  const [tasks] = useState<GanttTask[]>([
    {
      id: 1,
      name: 'ユーザー認証システム',
      assignee: '田中',
      startDate: '2024-01-15',
      endDate: '2024-01-20',
      progress: 100,
      color: '#10b981'
    },
    {
      id: 2,
      name: 'ダッシュボード画面',
      assignee: '佐藤',
      startDate: '2024-01-18',
      endDate: '2024-01-25',
      progress: 60,
      color: '#3b82f6'
    },
    {
      id: 3,
      name: 'API設計・実装',
      assignee: '鈴木',
      startDate: '2024-01-16',
      endDate: '2024-01-24',
      progress: 80,
      color: '#f59e0b'
    },
    {
      id: 4,
      name: 'データベース設計',
      assignee: '高橋',
      startDate: '2024-01-22',
      endDate: '2024-01-28',
      progress: 30,
      color: '#8b5cf6'
    },
    {
      id: 5,
      name: 'フロントエンド実装',
      assignee: '山田',
      startDate: '2024-01-20',
      endDate: '2024-01-30',
      progress: 45,
      color: '#ef4444'
    }
  ]);

  // 日付範囲を計算
  const startDate = new Date('2024-01-15');
  const endDate = new Date('2024-01-30');
  const totalDays = Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)) + 1;

  // 日付配列を生成
  const dates: Date[] = [];
  for (let i = 0; i < totalDays; i++) {
    const date = new Date(startDate);
    date.setDate(startDate.getDate() + i);
    dates.push(date);
  }

  // タスクの位置とサイズを計算
  const getTaskPosition = (task: GanttTask) => {
    const taskStart = new Date(task.startDate);
    const taskEnd = new Date(task.endDate);
    
    const startOffset = Math.max(0, (taskStart.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));
    const duration = (taskEnd.getTime() - taskStart.getTime()) / (1000 * 60 * 60 * 24) + 1;
    
    const left = (startOffset / totalDays) * 100;
    const width = (duration / totalDays) * 100;
    
    return { left: `${left}%`, width: `${width}%` };
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', color: '#1f2937', marginBottom: '0.5rem' }}>
          ガントチャート
        </h1>
        <p style={{ color: '#6b7280', margin: 0 }}>
          プロジェクトスケジュールの可視化と進捗管理
        </p>
      </div>

      {/* Chart Container */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '0.75rem',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
        overflow: 'hidden',
        border: '1px solid #e5e7eb'
      }}>
        {/* Header */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: '300px 1fr',
          backgroundColor: '#f9fafb',
          borderBottom: '1px solid #e5e7eb'
        }}>
          <div style={{ 
            padding: '1rem', 
            borderRight: '1px solid #e5e7eb',
            fontWeight: '600',
            color: '#374151'
          }}>
            タスク
          </div>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: `repeat(${totalDays}, 1fr)`,
            gap: '1px'
          }}>
            {dates.map((date, index) => (
              <div
                key={index}
                style={{
                  padding: '0.5rem 0.25rem',
                  textAlign: 'center',
                  fontSize: '0.75rem',
                  color: '#6b7280',
                  borderRight: index < dates.length - 1 ? '1px solid #f3f4f6' : 'none',
                  backgroundColor: date.getDay() === 0 || date.getDay() === 6 ? '#f9fafb' : 'transparent'
                }}
              >
                <div>{date.getDate()}</div>
                <div style={{ fontSize: '0.625rem' }}>
                  {date.toLocaleDateString('ja-JP', { weekday: 'short' })}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Tasks */}
        <div>
          {tasks.map((task, index) => {
            const position = getTaskPosition(task);
            
            return (
              <div
                key={task.id}
                style={{
                  display: 'grid',
                  gridTemplateColumns: '300px 1fr',
                  borderBottom: index < tasks.length - 1 ? '1px solid #f3f4f6' : 'none',
                  minHeight: '4rem'
                }}
              >
                {/* Task Info */}
                <div style={{
                  padding: '1rem',
                  borderRight: '1px solid #e5e7eb',
                  display: 'flex',
                  alignItems: 'center'
                }}>
                  <div>
                    <div style={{ 
                      fontWeight: '500', 
                      color: '#1f2937',
                      marginBottom: '0.25rem',
                      fontSize: '0.875rem'
                    }}>
                      {task.name}
                    </div>
                    <div style={{ 
                      fontSize: '0.75rem', 
                      color: '#6b7280',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}>
                      <span>👤 {task.assignee}</span>
                      <span>📊 {task.progress}%</span>
                    </div>
                  </div>
                </div>

                {/* Timeline */}
                <div style={{ 
                  position: 'relative', 
                  padding: '1rem 0',
                  display: 'flex',
                  alignItems: 'center'
                }}>
                  {/* Background grid */}
                  <div style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    display: 'grid',
                    gridTemplateColumns: `repeat(${totalDays}, 1fr)`,
                    gap: '1px'
                  }}>
                    {dates.map((date, dateIndex) => (
                      <div
                        key={dateIndex}
                        style={{
                          backgroundColor: date.getDay() === 0 || date.getDay() === 6 ? '#f9fafb' : 'transparent',
                          borderRight: dateIndex < dates.length - 1 ? '1px solid #f3f4f6' : 'none'
                        }}
                      />
                    ))}
                  </div>

                  {/* Task Bar */}
                  <div
                    style={{
                      position: 'absolute',
                      left: position.left,
                      width: position.width,
                      height: '1.5rem',
                      backgroundColor: task.color,
                      borderRadius: '0.375rem',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                      fontSize: '0.75rem',
                      fontWeight: '500',
                      boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
                      overflow: 'hidden'
                    }}
                  >
                    {/* Progress overlay */}
                    <div
                      style={{
                        position: 'absolute',
                        left: 0,
                        top: 0,
                        bottom: 0,
                        width: `${task.progress}%`,
                        backgroundColor: 'rgba(255, 255, 255, 0.2)',
                        borderRadius: '0.375rem'
                      }}
                    />
                    <span style={{ position: 'relative', zIndex: 1 }}>
                      {task.progress}%
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Legend */}
      <div style={{
        marginTop: '2rem',
        backgroundColor: 'white',
        borderRadius: '0.75rem',
        padding: '1.5rem',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
        border: '1px solid #e5e7eb'
      }}>
        <h3 style={{ 
          fontSize: '1.125rem', 
          fontWeight: '600', 
          color: '#1f2937', 
          marginBottom: '1rem' 
        }}>
          凡例
        </h3>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
          gap: '1rem' 
        }}>
          {tasks.map((task) => (
            <div key={task.id} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div
                style={{
                  width: '1rem',
                  height: '1rem',
                  backgroundColor: task.color,
                  borderRadius: '0.25rem'
                }}
              />
              <span style={{ fontSize: '0.875rem', color: '#374151' }}>
                {task.name}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default GanttChart;