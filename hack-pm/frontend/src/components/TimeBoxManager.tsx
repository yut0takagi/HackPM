import React, { useState, useEffect } from 'react';
import { api } from '../utils/api';
import CountdownTimer from './CountdownTimer';

interface TimeBox {
  id: number;
  name: string;
  phase: 'planning' | 'development' | 'testing' | 'presentation';
  start_time: string;
  end_time: string;
  description?: string;
  is_active: boolean;
  remaining_hours: number;
  created_at?: string;
}

interface TimeBoxStats {
  active_time_box: {
    name: string | null;
    phase: string | null;
    start_time: string | null;
    end_time: string | null;
    remaining_hours: number | null;
  };
  time_tracking: {
    total_issues: number;
    completed_issues: number;
    total_estimated_hours: number;
    completed_hours: number;
    completion_rate: number;
  };
  urgency: {
    time_sensitive_count: number;
    overdue_count: number;
    escalated_count: number;
  };
}

interface PhaseRecommendations {
  current_phase: string | null;
  remaining_hours?: number;
  open_issues?: number;
  recommended_action: string;
  message: string;
}

interface TimeBoxManagerProps {
  repositoryId: number;
}

const TimeBoxManager: React.FC<TimeBoxManagerProps> = ({ repositoryId }) => {
  const [timeBoxes, setTimeBoxes] = useState<TimeBox[]>([]);
  const [activeTimeBox, setActiveTimeBox] = useState<TimeBox | null>(null);
  const [stats, setStats] = useState<TimeBoxStats | null>(null);
  const [recommendations, setRecommendations] = useState<PhaseRecommendations | null>(null);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newTimeBox, setNewTimeBox] = useState<{
    name: string;
    phase: 'planning' | 'development' | 'testing' | 'presentation';
    duration_hours: number;
    description: string;
  }>({
    name: '',
    phase: 'planning',
    duration_hours: 4,
    description: ''
  });

  useEffect(() => {
    fetchData();
  }, [repositoryId]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [timeBoxesData, activeData, statsData, recommendationsData] = await Promise.all([
        api.get<TimeBox[]>(`/api/repos/${repositoryId}/timeboxes`),
        api.get<TimeBox | null>(`/api/repos/${repositoryId}/timeboxes/active`),
        api.get<TimeBoxStats>(`/api/repos/${repositoryId}/timebox-stats`),
        api.get<PhaseRecommendations>(`/api/repos/${repositoryId}/phase-recommendations`)
      ]);

      setTimeBoxes(timeBoxesData);
      setActiveTimeBox(activeData);
      setStats(statsData);
      setRecommendations(recommendationsData);
    } catch (error) {
      console.error('Failed to fetch time box data:', error);
    } finally {
      setLoading(false);
    }
  };

  const createTimeBox = async () => {
    try {
      await api.post(`/api/repos/${repositoryId}/timeboxes`, newTimeBox);
      setShowCreateForm(false);
      setNewTimeBox({
        name: '',
        phase: 'planning',
        duration_hours: 4,
        description: ''
      });
      fetchData();
    } catch (error) {
      console.error('Failed to create time box:', error);
    }
  };

  const getPhaseInfo = (phase: string) => {
    const phaseMap = {
      planning: { icon: '📋', label: 'Planning', color: '#3b82f6', defaultHours: 4 },
      development: { icon: '💻', label: 'Development', color: '#22c55e', defaultHours: 20 },
      testing: { icon: '🧪', label: 'Testing', color: '#f59e0b', defaultHours: 6 },
      presentation: { icon: '🎯', label: 'Presentation', color: '#8b5cf6', defaultHours: 2 }
    };
    return phaseMap[phase as keyof typeof phaseMap] || phaseMap.planning;
  };

  const getRecommendationAction = (action: string) => {
    const actionMap = {
      create_planning_phase: { icon: '🚀', label: 'Start Planning', color: '#3b82f6' },
      transition_to_development: { icon: '💻', label: 'Begin Development', color: '#22c55e' },
      transition_to_testing: { icon: '🧪', label: 'Start Testing', color: '#f59e0b' },
      transition_to_presentation: { icon: '🎯', label: 'Prepare Presentation', color: '#8b5cf6' },
      continue_planning: { icon: '📋', label: 'Continue Planning', color: '#3b82f6' },
      continue_development: { icon: '⚡', label: 'Keep Developing', color: '#22c55e' },
      continue_testing: { icon: '🔍', label: 'Continue Testing', color: '#f59e0b' },
      finalize_presentation: { icon: '✨', label: 'Finalize Presentation', color: '#8b5cf6' }
    };
    return actionMap[action as keyof typeof actionMap] || { icon: '❓', label: action, color: '#6b7280' };
  };

  if (loading) {
    return (
      <div style={{
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(20px)',
        borderRadius: '1rem',
        padding: '2rem',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        textAlign: 'center'
      }}>
        <div style={{ color: '#a1a1aa' }}>Loading time box data...</div>
      </div>
    );
  }

  return (
    <div style={{
      background: 'rgba(255, 255, 255, 0.05)',
      backdropFilter: 'blur(20px)',
      borderRadius: '1rem',
      padding: '2rem',
      border: '1px solid rgba(255, 255, 255, 0.1)'
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
          ⏱️ Time Box Management
        </h2>
        <button
          onClick={() => setShowCreateForm(true)}
          style={{
            padding: '0.5rem 1rem',
            background: 'rgba(34, 197, 94, 0.2)',
            border: '1px solid rgba(34, 197, 94, 0.3)',
            borderRadius: '0.5rem',
            color: '#22c55e',
            cursor: 'pointer',
            fontSize: '0.875rem',
            fontWeight: '500'
          }}
        >
          ➕ New Time Box
        </button>
      </div>

      {/* Active Time Box */}
      {activeTimeBox && (
        <div style={{ marginBottom: '2rem' }}>
          <h3 style={{
            fontSize: '1.125rem',
            fontWeight: '600',
            color: '#ffffff',
            marginBottom: '1rem'
          }}>
            🎯 Active Time Box
          </h3>
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            borderRadius: '0.75rem',
            padding: '1.5rem',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'flex-start',
              marginBottom: '1rem'
            }}>
              <div>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  marginBottom: '0.5rem'
                }}>
                  <span style={{ fontSize: '1.5rem' }}>
                    {getPhaseInfo(activeTimeBox.phase).icon}
                  </span>
                  <h4 style={{
                    fontSize: '1.125rem',
                    fontWeight: '600',
                    color: '#ffffff',
                    margin: 0
                  }}>
                    {activeTimeBox.name}
                  </h4>
                  <span style={{
                    padding: '0.25rem 0.75rem',
                    background: `${getPhaseInfo(activeTimeBox.phase).color}20`,
                    color: getPhaseInfo(activeTimeBox.phase).color,
                    borderRadius: '1rem',
                    fontSize: '0.75rem',
                    fontWeight: '500'
                  }}>
                    {getPhaseInfo(activeTimeBox.phase).label}
                  </span>
                </div>
                {activeTimeBox.description && (
                  <p style={{
                    color: '#a1a1aa',
                    fontSize: '0.875rem',
                    margin: 0
                  }}>
                    {activeTimeBox.description}
                  </p>
                )}
              </div>
              <CountdownTimer
                targetDate={activeTimeBox.end_time}
                startDate={activeTimeBox.start_time}
                label="Time Box Ends"
                showProgress={true}
              />
            </div>
          </div>
        </div>
      )}

      {/* Phase Recommendations */}
      {recommendations && (
        <div style={{ marginBottom: '2rem' }}>
          <h3 style={{
            fontSize: '1.125rem',
            fontWeight: '600',
            color: '#ffffff',
            marginBottom: '1rem'
          }}>
            💡 Phase Recommendations
          </h3>
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            borderRadius: '0.75rem',
            padding: '1.5rem',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '1rem',
              marginBottom: '1rem'
            }}>
              <span style={{ fontSize: '2rem' }}>
                {getRecommendationAction(recommendations.recommended_action).icon}
              </span>
              <div>
                <h4 style={{
                  fontSize: '1rem',
                  fontWeight: '600',
                  color: getRecommendationAction(recommendations.recommended_action).color,
                  margin: 0
                }}>
                  {getRecommendationAction(recommendations.recommended_action).label}
                </h4>
                <p style={{
                  color: '#a1a1aa',
                  fontSize: '0.875rem',
                  margin: 0
                }}>
                  {recommendations.message}
                </p>
              </div>
            </div>
            {recommendations.remaining_hours !== undefined && (
              <div style={{
                display: 'flex',
                gap: '2rem',
                fontSize: '0.875rem',
                color: '#a1a1aa'
              }}>
                <span>⏰ {recommendations.remaining_hours.toFixed(1)} hours remaining</span>
                {recommendations.open_issues !== undefined && (
                  <span>📋 {recommendations.open_issues} open issues</span>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Statistics */}
      {stats && (
        <div style={{ marginBottom: '2rem' }}>
          <h3 style={{
            fontSize: '1.125rem',
            fontWeight: '600',
            color: '#ffffff',
            marginBottom: '1rem'
          }}>
            📊 Time Tracking Statistics
          </h3>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1rem'
          }}>
            {/* Completion Stats */}
            <div style={{
              background: 'rgba(34, 197, 94, 0.1)',
              borderRadius: '0.75rem',
              padding: '1rem',
              border: '1px solid rgba(34, 197, 94, 0.2)'
            }}>
              <div style={{
                fontSize: '2rem',
                fontWeight: '700',
                color: '#22c55e',
                marginBottom: '0.25rem'
              }}>
                {Math.round(stats.time_tracking.completion_rate)}%
              </div>
              <div style={{
                fontSize: '0.875rem',
                color: '#a1a1aa'
              }}>
                Completion Rate
              </div>
              <div style={{
                fontSize: '0.75rem',
                color: '#a1a1aa',
                marginTop: '0.25rem'
              }}>
                {stats.time_tracking.completed_hours}h / {stats.time_tracking.total_estimated_hours}h
              </div>
            </div>

            {/* Issue Stats */}
            <div style={{
              background: 'rgba(59, 130, 246, 0.1)',
              borderRadius: '0.75rem',
              padding: '1rem',
              border: '1px solid rgba(59, 130, 246, 0.2)'
            }}>
              <div style={{
                fontSize: '2rem',
                fontWeight: '700',
                color: '#3b82f6',
                marginBottom: '0.25rem'
              }}>
                {stats.time_tracking.completed_issues}/{stats.time_tracking.total_issues}
              </div>
              <div style={{
                fontSize: '0.875rem',
                color: '#a1a1aa'
              }}>
                Issues Completed
              </div>
            </div>

            {/* Urgency Stats */}
            <div style={{
              background: 'rgba(245, 158, 11, 0.1)',
              borderRadius: '0.75rem',
              padding: '1rem',
              border: '1px solid rgba(245, 158, 11, 0.2)'
            }}>
              <div style={{
                fontSize: '2rem',
                fontWeight: '700',
                color: '#f59e0b',
                marginBottom: '0.25rem'
              }}>
                {stats.urgency.time_sensitive_count}
              </div>
              <div style={{
                fontSize: '0.875rem',
                color: '#a1a1aa'
              }}>
                Time Sensitive
              </div>
              <div style={{
                fontSize: '0.75rem',
                color: '#a1a1aa',
                marginTop: '0.25rem'
              }}>
                {stats.urgency.overdue_count} overdue
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Time Box Form */}
      {showCreateForm && (
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
          zIndex: 1000
        }}>
          <div style={{
            background: 'rgba(26, 26, 26, 0.95)',
            backdropFilter: 'blur(20px)',
            borderRadius: '1rem',
            padding: '2rem',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            maxWidth: '500px',
            width: '90%'
          }}>
            <h3 style={{
              fontSize: '1.25rem',
              fontWeight: '600',
              color: '#ffffff',
              marginBottom: '1.5rem'
            }}>
              Create New Time Box
            </h3>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{
                display: 'block',
                fontSize: '0.875rem',
                fontWeight: '500',
                color: '#a1a1aa',
                marginBottom: '0.5rem'
              }}>
                Name
              </label>
              <input
                type="text"
                value={newTimeBox.name}
                onChange={(e) => setNewTimeBox({ ...newTimeBox, name: e.target.value })}
                placeholder="e.g., Sprint 1, Feature Development"
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

            <div style={{ marginBottom: '1rem' }}>
              <label style={{
                display: 'block',
                fontSize: '0.875rem',
                fontWeight: '500',
                color: '#a1a1aa',
                marginBottom: '0.5rem'
              }}>
                Phase
              </label>
              <select
                value={newTimeBox.phase}
                onChange={(e) => {
                  const phase = e.target.value as 'planning' | 'development' | 'testing' | 'presentation';
                  const phaseInfo = getPhaseInfo(phase);
                  setNewTimeBox({ 
                    ...newTimeBox, 
                    phase,
                    duration_hours: phaseInfo.defaultHours
                  });
                }}
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
                <option value="planning">📋 Planning</option>
                <option value="development">💻 Development</option>
                <option value="testing">🧪 Testing</option>
                <option value="presentation">🎯 Presentation</option>
              </select>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{
                display: 'block',
                fontSize: '0.875rem',
                fontWeight: '500',
                color: '#a1a1aa',
                marginBottom: '0.5rem'
              }}>
                Duration (hours)
              </label>
              <input
                type="number"
                value={newTimeBox.duration_hours}
                onChange={(e) => setNewTimeBox({ ...newTimeBox, duration_hours: parseInt(e.target.value) || 4 })}
                min="1"
                max="48"
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

            <div style={{ marginBottom: '2rem' }}>
              <label style={{
                display: 'block',
                fontSize: '0.875rem',
                fontWeight: '500',
                color: '#a1a1aa',
                marginBottom: '0.5rem'
              }}>
                Description (optional)
              </label>
              <textarea
                value={newTimeBox.description}
                onChange={(e) => setNewTimeBox({ ...newTimeBox, description: e.target.value })}
                placeholder="Brief description of this time box..."
                rows={3}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '0.5rem',
                  color: '#ffffff',
                  fontSize: '0.875rem',
                  resize: 'vertical'
                }}
              />
            </div>

            <div style={{
              display: 'flex',
              gap: '1rem',
              justifyContent: 'flex-end'
            }}>
              <button
                onClick={() => setShowCreateForm(false)}
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
                Cancel
              </button>
              <button
                onClick={createTimeBox}
                disabled={!newTimeBox.name}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: newTimeBox.name ? 'rgba(34, 197, 94, 0.2)' : 'rgba(107, 114, 128, 0.2)',
                  border: `1px solid ${newTimeBox.name ? 'rgba(34, 197, 94, 0.3)' : 'rgba(107, 114, 128, 0.3)'}`,
                  borderRadius: '0.5rem',
                  color: newTimeBox.name ? '#22c55e' : '#6b7280',
                  cursor: newTimeBox.name ? 'pointer' : 'not-allowed',
                  fontSize: '0.875rem',
                  fontWeight: '500'
                }}
              >
                Create Time Box
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Time Box History */}
      {timeBoxes.length > 0 && (
        <div>
          <h3 style={{
            fontSize: '1.125rem',
            fontWeight: '600',
            color: '#ffffff',
            marginBottom: '1rem'
          }}>
            📅 Time Box History
          </h3>
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '0.75rem'
          }}>
            {timeBoxes.slice(0, 5).map((timeBox) => (
              <div
                key={timeBox.id}
                style={{
                  background: timeBox.is_active 
                    ? 'rgba(34, 197, 94, 0.1)' 
                    : 'rgba(255, 255, 255, 0.05)',
                  border: timeBox.is_active 
                    ? '1px solid rgba(34, 197, 94, 0.2)' 
                    : '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '0.5rem',
                  padding: '1rem',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <span style={{ fontSize: '1.25rem' }}>
                    {getPhaseInfo(timeBox.phase).icon}
                  </span>
                  <div>
                    <div style={{
                      fontSize: '0.875rem',
                      fontWeight: '500',
                      color: '#ffffff'
                    }}>
                      {timeBox.name}
                    </div>
                    <div style={{
                      fontSize: '0.75rem',
                      color: '#a1a1aa'
                    }}>
                      {getPhaseInfo(timeBox.phase).label} • {new Date(timeBox.start_time).toLocaleDateString()}
                    </div>
                  </div>
                </div>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}>
                  {timeBox.is_active && (
                    <span style={{
                      padding: '0.25rem 0.5rem',
                      background: 'rgba(34, 197, 94, 0.2)',
                      color: '#22c55e',
                      borderRadius: '0.25rem',
                      fontSize: '0.75rem',
                      fontWeight: '500'
                    }}>
                      Active
                    </span>
                  )}
                  <span style={{
                    fontSize: '0.75rem',
                    color: '#a1a1aa'
                  }}>
                    {timeBox.remaining_hours > 0 
                      ? `${timeBox.remaining_hours.toFixed(1)}h left`
                      : 'Completed'
                    }
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TimeBoxManager;