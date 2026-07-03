import { Bot } from 'lucide-react';

export default function TypingIndicator() {
  return (
    <div className="animate-fade-in" style={{
      display: 'flex',
      gap: '0.75rem',
      alignSelf: 'flex-start',
      maxWidth: '85%',
    }}>
      <div style={{
        width: 36,
        height: 36,
        borderRadius: 'var(--radius-lg)',
        background: 'var(--gradient-primary)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
      }}>
        <Bot size={18} color="white" />
      </div>
      <div style={{
        padding: '1rem 1.25rem',
        borderRadius: 'var(--radius-xl) var(--radius-xl) var(--radius-xl) var(--radius-sm)',
        background: 'var(--color-bg-secondary)',
        border: '1px solid var(--color-border)',
        display: 'flex',
        alignItems: 'center',
        gap: '0.375rem',
        boxShadow: 'var(--shadow-sm)',
      }}>
        <span className="typing-dot" />
        <span className="typing-dot" />
        <span className="typing-dot" />
        <span style={{
          marginLeft: '0.5rem',
          fontSize: 'var(--font-size-xs)',
          color: 'var(--color-text-muted)',
          fontStyle: 'italic',
        }}>
          Analyzing properties...
        </span>
      </div>
    </div>
  );
}
