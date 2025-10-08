import React, { useState, useEffect } from 'react';

interface CountdownTimerProps {
  targetDate: string;
  label?: string;
  onExpired?: () => void;
  showProgress?: boolean;
  startDate?: string;
}

interface TimeRemaining {
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
  total: number;
}

const CountdownTimer: React.FC<CountdownTimerProps> = ({
  targetDate,
  label = "Time Remaining",
  onExpired,
  showProgress = false,
  startDate
}) => {
  const [timeRemaining, setTimeRemaining] = useState<TimeRemaining>({
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0,
    total: 0
  });
  const [isExpired, setIsExpired] = useState(false);
  const [progressPercentage, setProgressPercentage] = useState(0);

  useEffect(() => {
    const calculateTimeRemaining = () => {
      const now = new Date().getTime();
      const target = new Date(targetDate).getTime();
      const difference = target - now;

      if (difference <= 0) {
        setTimeRemaining({ days: 0, hours: 0, minutes: 0, seconds: 0, total: 0 });
        if (!isExpired) {
          setIsExpired(true);
          onExpired?.();
        }
        return;
      }

      const days = Math.floor(difference / (1000 * 60 * 60 * 24));
      const hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((difference % (1000 * 60)) / 1000);

      setTimeRemaining({ days, hours, minutes, seconds, total: difference });

      // Calculate progress if start date is provided
      if (startDate && showProgress) {
        const start = new Date(startDate).getTime();
        const totalDuration = target - start;
        const elapsed = now - start;
        const progress = Math.max(0, Math.min(100, (elapsed / totalDuration) * 100));
        setProgressPercentage(progress);
      }
    };

    calculateTimeRemaining();
    const interval = setInterval(calculateTimeRemaining, 1000);

    return () => clearInterval(interval);
  }, [targetDate, startDate, showProgress, isExpired, onExpired]);

  const getUrgencyColor = () => {
    const totalHours = timeRemaining.total / (1000 * 60 * 60);
    
    if (isExpired) {
      return { bg: 'rgba(239, 68, 68, 0.2)', text: '#ef4444', border: '#dc2626' };
    } else if (totalHours < 2) {
      return { bg: 'rgba(245, 158, 11, 0.2)', text: '#f59e0b', border: '#d97706' };
    } else if (totalHours < 6) {
      return { bg: 'rgba(59, 130, 246, 0.2)', text: '#3b82f6', border: '#2563eb' };
    } else {
      return { bg: 'rgba(34, 197, 94, 0.2)', text: '#22c55e', border: '#16a34a' };
    }
  };

  const colors = getUrgencyColor();

  const formatTimeUnit = (value: number, unit: string) => {
    if (value === 0) return null;
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        minWidth: '3rem'
      }}>
        <div style={{
          fontSize: '1.5rem',
          fontWeight: '700',
          color: colors.text,
          lineHeight: '1'
        }}>
          {value.toString().padStart(2, '0')}
        </div>
        <div style={{
          fontSize: '0.75rem',
          color: '#a1a1aa',
          textTransform: 'uppercase',
          letterSpacing: '0.05em'
        }}>
          {unit}
        </div>
      </div>
    );
  };

  return (
    <div style={{
      background: colors.bg,
      border: `1px solid ${colors.border}`,
      borderRadius: '0.75rem',
      padding: '1rem',
      backdropFilter: 'blur(10px)'
    }}>
      {/* Label */}
      <div style={{
        fontSize: '0.875rem',
        fontWeight: '500',
        color: colors.text,
        marginBottom: '0.5rem',
        textAlign: 'center'
      }}>
        {isExpired ? '⏰ Expired' : `⏱️ ${label}`}
      </div>

      {/* Countdown Display */}
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        gap: '1rem',
        marginBottom: showProgress ? '0.75rem' : '0'
      }}>
        {isExpired ? (
          <div style={{
            fontSize: '1.25rem',
            fontWeight: '600',
            color: colors.text,
            textAlign: 'center'
          }}>
            Time's Up!
          </div>
        ) : (
          <>
            {formatTimeUnit(timeRemaining.days, 'days')}
            {(timeRemaining.days > 0 || timeRemaining.hours > 0) && formatTimeUnit(timeRemaining.hours, 'hrs')}
            {timeRemaining.days === 0 && formatTimeUnit(timeRemaining.minutes, 'min')}
            {timeRemaining.days === 0 && timeRemaining.hours === 0 && formatTimeUnit(timeRemaining.seconds, 'sec')}
          </>
        )}
      </div>

      {/* Progress Bar */}
      {showProgress && startDate && (
        <div>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '0.25rem'
          }}>
            <span style={{ fontSize: '0.75rem', color: '#a1a1aa' }}>
              Progress
            </span>
            <span style={{ fontSize: '0.75rem', color: '#a1a1aa' }}>
              {Math.round(progressPercentage)}%
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
              width: `${progressPercentage}%`,
              height: '100%',
              background: colors.text,
              borderRadius: '2px',
              transition: 'width 0.3s ease'
            }} />
          </div>
        </div>
      )}

      {/* Urgency Indicator */}
      {!isExpired && (
        <div style={{
          marginTop: '0.5rem',
          textAlign: 'center',
          fontSize: '0.75rem',
          color: '#a1a1aa'
        }}>
          {timeRemaining.total / (1000 * 60 * 60) < 2 ? '🚨 Critical' :
           timeRemaining.total / (1000 * 60 * 60) < 6 ? '⚠️ Urgent' : '✅ On Track'}
        </div>
      )}
    </div>
  );
};

export default CountdownTimer;