import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navbar: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'ダッシュボード', icon: '🏠' },
    { path: '/features', label: 'タスク管理', icon: '📋' },
    { path: '/gantt', label: 'プロジェクト計画', icon: '📅' },
    { path: '/team', label: 'チーム', icon: '👥' },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav style={{
      background: 'rgba(0, 0, 0, 0.8)',
      backdropFilter: 'blur(20px)',
      borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
      position: 'sticky',
      top: 0,
      zIndex: 50
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', height: '5rem' }}>
          {/* Logo */}
          <Link to="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{
              width: '2.5rem',
              height: '2.5rem',
              background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
              borderRadius: '0.75rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.25rem'
            }}>
              🚀
            </div>
            <div>
              <div style={{ 
                fontSize: '1.5rem', 
                fontWeight: '700', 
                color: '#ffffff',
                letterSpacing: '-0.02em',
                lineHeight: '1'
              }}>
                Keel Project
              </div>
              <div style={{
                fontSize: '0.75rem',
                color: '#a1a1aa',
                fontWeight: '500'
              }}>
                Hackathon Dashboard
              </div>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                style={{
                  textDecoration: 'none',
                  padding: '0.75rem 1.25rem',
                  borderRadius: '1.5rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  fontSize: '0.95rem',
                  fontWeight: '500',
                  transition: 'all 0.3s ease',
                  background: isActive(item.path) ? 'rgba(255, 255, 255, 0.15)' : 'transparent',
                  color: isActive(item.path) ? '#ffffff' : '#a1a1aa',
                  backdropFilter: isActive(item.path) ? 'blur(10px)' : 'none'
                }}
                onMouseEnter={(e) => {
                  if (!isActive(item.path)) {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
                    e.currentTarget.style.color = '#ffffff';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive(item.path)) {
                    e.currentTarget.style.background = 'transparent';
                    e.currentTarget.style.color = '#a1a1aa';
                  }
                }}
              >
                <span style={{ fontSize: '1rem' }}>{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            ))}
            
            {/* GitHub Link */}
            <a
              href="https://github.com/yut0takagi/Keel"
              target="_blank"
              rel="noopener noreferrer"
              style={{
                textDecoration: 'none',
                padding: '0.75rem',
                borderRadius: '1.5rem',
                display: 'flex',
                alignItems: 'center',
                fontSize: '1.25rem',
                transition: 'all 0.3s ease',
                background: 'transparent',
                color: '#a1a1aa',
                marginLeft: '0.5rem'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
                e.currentTarget.style.color = '#ffffff';
                e.currentTarget.style.transform = 'scale(1.1)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'transparent';
                e.currentTarget.style.color = '#a1a1aa';
                e.currentTarget.style.transform = 'scale(1)';
              }}
              title="GitHub Repository"
            >
              📁
            </a>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            style={{
              display: 'none',
              padding: '0.5rem',
              borderRadius: '0.375rem',
              border: 'none',
              backgroundColor: 'transparent',
              cursor: 'pointer'
            }}
          >
            <span style={{ fontSize: '1.5rem' }}>☰</span>
          </button>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div style={{
            display: 'block',
            paddingBottom: '1rem',
            borderTop: '1px solid #374151',
            marginTop: '1rem'
          }}>
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setIsMenuOpen(false)}
                style={{
                  textDecoration: 'none',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  padding: '0.75rem 1rem',
                  borderRadius: '0.5rem',
                  margin: '0.25rem 0',
                  fontSize: '1rem',
                  fontWeight: '500',
                  backgroundColor: isActive(item.path) ? '#374151' : 'transparent',
                  color: isActive(item.path) ? '#f8fafc' : '#9ca3af'
                }}
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            ))}
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;