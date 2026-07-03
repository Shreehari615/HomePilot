import { useState, useRef } from 'react';
import { Send, Trash2, Wrench, Sparkles } from 'lucide-react';
import { useChat } from '../hooks/useChat';
import ChatBubble from '../components/ChatBubble';
import TypingIndicator from '../components/TypingIndicator';
import PropertyCard from '../components/PropertyCard';

const SUGGESTIONS = [
  'Find me a 3BHK in Mumbai under 1.5 crore with good schools',
  'Show me safe 2BHK apartments in Bangalore near metro',
  'Best family homes in Pune under 80 lakh',
  'Compare properties in Koramangala vs Whitefield',
  'Affordable 3BHK in Hyderabad with high appreciation',
];

export default function Chat() {
  const {
    messages,
    isLoading,
    sendMessage,
    clearChat,
    toolsCalled,
    messagesEndRef,
  } = useChat();
  const [input, setInput] = useState('');
  const [favorites, setFavorites] = useState(new Set());
  const inputRef = useRef(null);

  const handleSend = () => {
    if (!input.trim() || isLoading) return;
    sendMessage(input);
    setInput('');
    inputRef.current?.focus();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const toggleFavorite = (id) => {
    setFavorites((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  return (
    <div style={{
      height: 'calc(100vh - var(--navbar-height))',
      display: 'flex',
      flexDirection: 'column',
      maxWidth: 'var(--chat-max-width)',
      margin: '0 auto',
      padding: '0 1rem',
    }}>
      {/* Chat Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '1rem 0',
        borderBottom: '1px solid var(--color-border)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: 40,
            height: 40,
            borderRadius: 'var(--radius-lg)',
            background: 'var(--gradient-primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <Sparkles size={20} color="white" />
          </div>
          <div>
            <h2 style={{ fontSize: 'var(--font-size-base)', fontWeight: 700 }}>
              HomePilot Agent
            </h2>
            <span style={{
              fontSize: 'var(--font-size-xs)',
              color: isLoading ? 'var(--color-accent)' : 'var(--color-success)',
              fontWeight: 500,
            }}>
              {isLoading ? '● Thinking...' : '● Online'}
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          {toolsCalled.length > 0 && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.375rem',
              padding: '0.25rem 0.75rem',
              background: 'var(--color-bg-tertiary)',
              borderRadius: 'var(--radius-full)',
              fontSize: 'var(--font-size-xs)',
              color: 'var(--color-text-muted)',
            }}>
              <Wrench size={12} />
              {toolsCalled.length} tools used
            </div>
          )}
          <button onClick={clearChat} className="btn btn-ghost" style={{ padding: '0.5rem' }} title="Clear chat">
            <Trash2 size={16} />
          </button>
        </div>
      </div>

      {/* Messages Area */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '1.5rem 0',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.25rem',
      }}>
        {/* Empty State */}
        {messages.length === 0 && (
          <div style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '2rem',
            padding: '2rem',
          }}>
            <div className="animate-float" style={{
              width: 80,
              height: 80,
              borderRadius: 'var(--radius-2xl)',
              background: 'var(--gradient-primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 8px 30px rgba(99,102,241,0.3)',
            }}>
              <Sparkles size={36} color="white" />
            </div>
            <div style={{ textAlign: 'center' }}>
              <h3 style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, marginBottom: '0.5rem' }}>
                How can I help you find a home?
              </h3>
              <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-muted)', maxWidth: 400 }}>
                Describe your ideal property in natural language. I'll search, analyze, rank, and explain.
              </p>
            </div>
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '0.5rem',
              width: '100%',
              maxWidth: 500,
            }}>
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => { setInput(s); inputRef.current?.focus(); }}
                  style={{
                    padding: '0.75rem 1rem',
                    background: 'var(--color-bg-secondary)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-lg)',
                    fontSize: 'var(--font-size-sm)',
                    color: 'var(--color-text-secondary)',
                    cursor: 'pointer',
                    textAlign: 'left',
                    transition: 'all var(--transition-fast)',
                    fontFamily: 'var(--font-family)',
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.borderColor = 'var(--color-primary)';
                    e.currentTarget.style.background = 'var(--color-primary-50)';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.borderColor = 'var(--color-border)';
                    e.currentTarget.style.background = 'var(--color-bg-secondary)';
                  }}
                >
                  💬 {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Messages */}
        {messages.map((msg) => (
          <div key={msg.id}>
            <ChatBubble message={msg} />

            {/* Inline property cards */}
            {msg.properties && msg.properties.length > 0 && (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                gap: '1rem',
                marginTop: '1rem',
                padding: '0 2.75rem',
              }}>
                {msg.properties.slice(0, 5).map((prop) => {
                  const explanation = msg.explanations?.find(
                    (e) => (e.property_id || e.propertyId) === prop.id
                  );
                  return (
                    <PropertyCard
                      key={prop.id}
                      property={prop}
                      explanation={explanation}
                      isFavorite={favorites.has(prop.id)}
                      onFavorite={toggleFavorite}
                    />
                  );
                })}
              </div>
            )}
          </div>
        ))}

        {isLoading && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div style={{
        padding: '1rem 0',
        borderTop: '1px solid var(--color-border)',
      }}>
        <div style={{
          display: 'flex',
          gap: '0.75rem',
          alignItems: 'flex-end',
          background: 'var(--color-bg-secondary)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-xl)',
          padding: '0.5rem',
          transition: 'border-color var(--transition-fast)',
        }}>
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe your dream home..."
            disabled={isLoading}
            rows={1}
            style={{
              flex: 1,
              border: 'none',
              outline: 'none',
              resize: 'none',
              background: 'transparent',
              fontFamily: 'var(--font-family)',
              fontSize: 'var(--font-size-sm)',
              color: 'var(--color-text)',
              padding: '0.5rem',
              lineHeight: 1.5,
              maxHeight: 120,
              overflowY: 'auto',
            }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="btn btn-primary"
            style={{
              width: 42,
              height: 42,
              padding: 0,
              borderRadius: 'var(--radius-lg)',
              flexShrink: 0,
            }}
          >
            <Send size={18} />
          </button>
        </div>
        <p style={{
          fontSize: 'var(--font-size-xs)',
          color: 'var(--color-text-muted)',
          textAlign: 'center',
          marginTop: '0.5rem',
        }}>
          HomePilot AI uses mock data for demonstration. Not financial advice.
        </p>
      </div>
    </div>
  );
}
