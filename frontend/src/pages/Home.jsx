import { Link } from 'react-router-dom';
import { MessageSquare, Search, Brain, Shield, TrendingUp, Sparkles, ArrowRight, Star, Zap, BarChart3 } from 'lucide-react';

export default function Home() {
  return (
    <div>
      {/* Hero Section */}
      <section style={{
        minHeight: 'calc(100vh - var(--navbar-height))',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Animated background */}
        <div style={{
          position: 'absolute',
          inset: 0,
          background: 'var(--gradient-hero)',
          opacity: 0.03,
        }} />
        <div style={{
          position: 'absolute',
          top: '10%',
          right: '5%',
          width: 400,
          height: 400,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%)',
          filter: 'blur(40px)',
        }} className="animate-float" />
        <div style={{
          position: 'absolute',
          bottom: '10%',
          left: '10%',
          width: 300,
          height: 300,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(168,85,247,0.12) 0%, transparent 70%)',
          filter: 'blur(40px)',
        }} className="animate-float" />

        <div style={{
          textAlign: 'center',
          maxWidth: 800,
          position: 'relative',
          zIndex: 1,
        }} className="animate-fade-in">
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.375rem 1rem',
            background: 'var(--color-primary-50)',
            borderRadius: 'var(--radius-full)',
            fontSize: 'var(--font-size-sm)',
            fontWeight: 600,
            color: 'var(--color-primary)',
            marginBottom: '1.5rem',
          }}>
            <Sparkles size={16} />
            Powered by AI · LangGraph · GPT-4o
          </div>

          <h1 style={{
            fontSize: 'clamp(2.5rem, 6vw, 4rem)',
            fontWeight: 900,
            lineHeight: 1.1,
            letterSpacing: '-0.03em',
            marginBottom: '1.5rem',
          }}>
            Find Your <span className="gradient-text">Perfect Home</span>
            <br />With AI Intelligence
          </h1>

          <p style={{
            fontSize: 'var(--font-size-lg)',
            color: 'var(--color-text-secondary)',
            maxWidth: 600,
            margin: '0 auto 2.5rem',
            lineHeight: 1.7,
          }}>
            Tell our autonomous AI agent what you're looking for in natural language.
            It analyzes schools, safety, commute, prices, and amenities to find and rank
            the best properties for you.
          </p>

          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link to="/chat" className="btn btn-primary" style={{
              padding: '0.875rem 2rem',
              fontSize: 'var(--font-size-base)',
              borderRadius: 'var(--radius-xl)',
            }}>
              <MessageSquare size={20} />
              Start Chatting
              <ArrowRight size={18} />
            </Link>
            <a href="#features" className="btn btn-secondary" style={{
              padding: '0.875rem 2rem',
              fontSize: 'var(--font-size-base)',
              borderRadius: 'var(--radius-xl)',
            }}>
              Learn More
            </a>
          </div>

          {/* Example queries */}
          <div style={{
            marginTop: '3rem',
            display: 'flex',
            flexWrap: 'wrap',
            gap: '0.5rem',
            justifyContent: 'center',
          }}>
            <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)', marginRight: '0.25rem', alignSelf: 'center' }}>Try:</span>
            {[
              '"Find me a 3BHK in Mumbai under 1.5 crore"',
              '"Safest neighborhoods in Bangalore"',
              '"Near metro with good schools"',
            ].map((q) => (
              <Link
                key={q}
                to="/chat"
                style={{
                  padding: '0.375rem 0.875rem',
                  background: 'var(--color-bg-secondary)',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--radius-full)',
                  fontSize: 'var(--font-size-xs)',
                  color: 'var(--color-text-secondary)',
                  cursor: 'pointer',
                  transition: 'all var(--transition-fast)',
                  textDecoration: 'none',
                }}
              >
                {q}
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" style={{
        padding: '5rem 2rem',
        background: 'var(--color-bg-secondary)',
      }}>
        <div style={{ maxWidth: 1100, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '3.5rem' }}>
            <h2 style={{
              fontSize: 'var(--font-size-3xl)',
              fontWeight: 800,
              letterSpacing: '-0.02em',
              marginBottom: '1rem',
            }}>
              Why <span className="gradient-text">HomePilot AI</span>?
            </h2>
            <p style={{
              fontSize: 'var(--font-size-base)',
              color: 'var(--color-text-secondary)',
              maxWidth: 500,
              margin: '0 auto',
            }}>
              Our autonomous agent does the research so you don't have to.
            </p>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '1.5rem',
          }}>
            <FeatureCard
              icon={Brain}
              title="Autonomous AI Agent"
              description="Powered by LangGraph, the agent autonomously decides which tools to use — property search, schools, safety, commute — based on your needs."
              color="#6366f1"
            />
            <FeatureCard
              icon={BarChart3}
              title="Smart Ranking"
              description="Dynamic weighted scoring adapts to your priorities. Say 'I need the safest area' and watch safety weight jump to 35%+."
              color="#8b5cf6"
            />
            <FeatureCard
              icon={Search}
              title="Deep Property Analysis"
              description="Every recommendation is backed by data from 6 specialized tools covering schools, crime, commute, price history, and amenities."
              color="#ec4899"
            />
            <FeatureCard
              icon={Zap}
              title="Natural Language"
              description="Just describe what you want: '3BHK near metro in Bangalore under 1 crore with good schools.' The AI handles the rest."
              color="#f59e0b"
            />
            <FeatureCard
              icon={Shield}
              title="Full Transparency"
              description="Every recommendation includes detailed pros, cons, score breakdown, and the specific evidence behind each score."
              color="#10b981"
            />
            <FeatureCard
              icon={Star}
              title="Conversation Memory"
              description="Follow up naturally — 'What about near metro?' — and the agent remembers your budget, city, bedrooms, and all prior context."
              color="#ef4444"
            />
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section style={{ padding: '5rem 2rem' }}>
        <div style={{ maxWidth: 900, margin: '0 auto', textAlign: 'center' }}>
          <h2 style={{
            fontSize: 'var(--font-size-3xl)',
            fontWeight: 800,
            letterSpacing: '-0.02em',
            marginBottom: '3rem',
          }}>
            How It <span className="gradient-text">Works</span>
          </h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '2rem',
          }}>
            {[
              { step: '01', title: 'Describe', desc: 'Tell the AI what you want in plain English' },
              { step: '02', title: 'Analyze', desc: 'Agent autonomously queries 6 specialized tools' },
              { step: '03', title: 'Rank', desc: 'Properties scored on budget, safety, schools & more' },
              { step: '04', title: 'Recommend', desc: 'Get transparent, explainable recommendations' },
            ].map((item) => (
              <div key={item.step} style={{ textAlign: 'center' }}>
                <div style={{
                  width: 56,
                  height: 56,
                  borderRadius: 'var(--radius-xl)',
                  background: 'var(--gradient-primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 1rem',
                  fontSize: 'var(--font-size-lg)',
                  fontWeight: 800,
                  color: 'white',
                }}>
                  {item.step}
                </div>
                <h3 style={{ fontWeight: 700, marginBottom: '0.5rem' }}>{item.title}</h3>
                <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section style={{
        padding: '4rem 2rem',
        textAlign: 'center',
        background: 'var(--gradient-primary)',
        borderRadius: 'var(--radius-2xl) var(--radius-2xl) 0 0',
      }}>
        <h2 style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 800, color: 'white', marginBottom: '1rem' }}>
          Ready to Find Your Dream Home?
        </h2>
        <p style={{ color: 'rgba(255,255,255,0.8)', marginBottom: '2rem', fontSize: 'var(--font-size-lg)' }}>
          Start a conversation with our AI agent today.
        </p>
        <Link to="/chat" className="btn" style={{
          background: 'white',
          color: 'var(--color-primary)',
          padding: '1rem 2.5rem',
          fontSize: 'var(--font-size-base)',
          fontWeight: 700,
          borderRadius: 'var(--radius-xl)',
          boxShadow: '0 4px 14px rgba(0,0,0,0.15)',
        }}>
          <MessageSquare size={20} />
          Start Chatting
          <ArrowRight size={18} />
        </Link>
      </section>
    </div>
  );
}

function FeatureCard({ icon: Icon, title, description, color }) {
  return (
    <div className="card" style={{
      padding: '1.75rem',
      display: 'flex',
      flexDirection: 'column',
      gap: '1rem',
    }}>
      <div style={{
        width: 48,
        height: 48,
        borderRadius: 'var(--radius-lg)',
        background: `${color}12`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        <Icon size={24} color={color} />
      </div>
      <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 700 }}>{title}</h3>
      <p style={{
        fontSize: 'var(--font-size-sm)',
        color: 'var(--color-text-secondary)',
        lineHeight: 1.7,
      }}>
        {description}
      </p>
    </div>
  );
}
