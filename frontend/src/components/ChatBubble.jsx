import ReactMarkdown from 'react-markdown';
import { Bot, User } from 'lucide-react';

export default function ChatBubble({ message }) {
  const isUser = message.role === 'user';
  const isError = message.isError;

  return (
    <div
      className={isUser ? 'animate-slide-right' : 'animate-slide-left'}
      style={{
        display: 'flex',
        gap: '0.75rem',
        maxWidth: '85%',
        alignSelf: isUser ? 'flex-end' : 'flex-start',
        flexDirection: isUser ? 'row-reverse' : 'row',
      }}
    >
      {/* Avatar */}
      <div style={{
        width: 36,
        height: 36,
        borderRadius: 'var(--radius-lg)',
        background: isUser ? 'var(--gradient-accent)' : 'var(--gradient-primary)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
      }}>
        {isUser ? <User size={18} color="white" /> : <Bot size={18} color="white" />}
      </div>

      {/* Bubble */}
      <div style={{
        padding: '0.875rem 1.125rem',
        borderRadius: isUser
          ? 'var(--radius-xl) var(--radius-xl) var(--radius-sm) var(--radius-xl)'
          : 'var(--radius-xl) var(--radius-xl) var(--radius-xl) var(--radius-sm)',
        background: isUser
          ? 'var(--gradient-primary)'
          : isError
            ? 'rgba(239, 68, 68, 0.08)'
            : 'var(--color-bg-secondary)',
        color: isUser ? 'white' : 'var(--color-text)',
        border: isUser ? 'none' : `1px solid ${isError ? 'rgba(239,68,68,0.2)' : 'var(--color-border)'}`,
        fontSize: 'var(--font-size-sm)',
        lineHeight: 1.7,
        boxShadow: 'var(--shadow-sm)',
        wordBreak: 'break-word',
      }}>
        <div className="markdown-content" style={{
          ...(isUser ? { color: 'white' } : {}),
        }}>
          <ReactMarkdown
            components={{
              p: ({ children }) => <p style={{ margin: '0.25rem 0' }}>{children}</p>,
              ul: ({ children }) => <ul style={{ paddingLeft: '1.25rem', margin: '0.5rem 0' }}>{children}</ul>,
              ol: ({ children }) => <ol style={{ paddingLeft: '1.25rem', margin: '0.5rem 0' }}>{children}</ol>,
              li: ({ children }) => <li style={{ margin: '0.2rem 0' }}>{children}</li>,
              strong: ({ children }) => <strong style={{ fontWeight: 700 }}>{children}</strong>,
              h3: ({ children }) => <h3 style={{ fontSize: 'var(--font-size-base)', fontWeight: 700, margin: '0.75rem 0 0.25rem' }}>{children}</h3>,
              h4: ({ children }) => <h4 style={{ fontSize: 'var(--font-size-sm)', fontWeight: 700, margin: '0.5rem 0 0.25rem' }}>{children}</h4>,
              code: ({ children }) => (
                <code style={{
                  background: isUser ? 'rgba(255,255,255,0.15)' : 'var(--color-bg-tertiary)',
                  padding: '0.125rem 0.375rem',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: 'var(--font-size-xs)',
                }}>{children}</code>
              ),
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>

        {/* Timestamp */}
        <div style={{
          fontSize: 'var(--font-size-xs)',
          opacity: 0.6,
          marginTop: '0.5rem',
          textAlign: isUser ? 'right' : 'left',
        }}>
          {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  );
}
