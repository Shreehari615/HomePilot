import { Link, useLocation } from 'react-router-dom';
import { Home, MessageSquare, Clock, Sun, Moon, Sparkles } from 'lucide-react';

export default function Navbar({ isDark, toggleDark }) {
  const location = useLocation();

  const navLinks = [
    { path: '/', label: 'Home', icon: Home },
    { path: '/chat', label: 'Chat', icon: MessageSquare },
    { path: '/history', label: 'History', icon: Clock },
  ];

  return (
    <nav className="glass" style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      height: 'var(--navbar-height)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 1.5rem',
      zIndex: 1000,
    }}>
      {/* Logo */}
      <Link to="/" style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem',
        textDecoration: 'none',
      }}>
        <div style={{
          width: 36,
          height: 36,
          borderRadius: 'var(--radius-lg)',
          background: 'var(--gradient-primary)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}>
          <Sparkles size={20} color="white" />
        </div>
        <span style={{
          fontSize: 'var(--font-size-xl)',
          fontWeight: 800,
          background: 'var(--gradient-primary)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          letterSpacing: '-0.02em',
        }}>
          HomePilot
        </span>
        <span style={{
          fontSize: 'var(--font-size-xs)',
          fontWeight: 600,
          color: 'var(--color-accent)',
          background: 'rgba(245, 158, 11, 0.1)',
          padding: '0.125rem 0.5rem',
          borderRadius: 'var(--radius-full)',
        }}>
          AI
        </span>
      </Link>

      {/* Nav Links */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
        {navLinks.map(({ path, label, icon: Icon }) => {
          const isActive = location.pathname === path;
          return (
            <Link
              key={path}
              to={path}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.375rem',
                padding: '0.5rem 1rem',
                borderRadius: 'var(--radius-lg)',
                fontSize: 'var(--font-size-sm)',
                fontWeight: isActive ? 600 : 500,
                color: isActive ? 'var(--color-primary)' : 'var(--color-text-secondary)',
                background: isActive ? 'var(--color-primary-50)' : 'transparent',
                transition: 'all var(--transition-fast)',
                textDecoration: 'none',
              }}
            >
              <Icon size={16} />
              {label}
            </Link>
          );
        })}

        {/* Dark Mode Toggle */}
        <button
          onClick={toggleDark}
          className="btn-ghost"
          style={{
            width: 40,
            height: 40,
            borderRadius: 'var(--radius-lg)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: 'none',
            cursor: 'pointer',
            marginLeft: '0.5rem',
            color: 'var(--color-text-secondary)',
            background: 'transparent',
            transition: 'all var(--transition-fast)',
          }}
          aria-label="Toggle dark mode"
        >
          {isDark ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>
    </nav>
  );
}
