import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, MapPin, Bed, Bath, Maximize, Heart, Star, Train, Shield, TrendingUp, TreePine, UtensilsCrossed, ShoppingCart, Loader2 } from 'lucide-react';
import { getPropertyDetail, getPropertyHistory } from '../services/api';
import ScoreBreakdown from '../components/ScoreBreakdown';

export default function PropertyDetails() {
  const { id } = useParams();
  const [property, setProperty] = useState(null);
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isFavorite, setIsFavorite] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [propRes, histRes] = await Promise.all([
          getPropertyDetail(id),
          getPropertyHistory(id).catch(() => null),
        ]);
        setProperty(propRes.property);
        setHistory(histRes);
      } catch (err) {
        setError(err.message || 'Failed to load property');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '50vh' }}>
        <Loader2 size={32} className="animate-spin" style={{ color: 'var(--color-primary)', animation: 'spin 1s linear infinite' }} />
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (error || !property) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem 2rem' }}>
        <h2 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, marginBottom: '1rem' }}>Property Not Found</h2>
        <p style={{ color: 'var(--color-text-secondary)', marginBottom: '2rem' }}>{error || 'The property you are looking for does not exist.'}</p>
        <Link to="/chat" className="btn btn-primary">Back to Chat</Link>
      </div>
    );
  }

  const imageUrl = property.images?.[0]?.url || 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800';

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto', padding: '1.5rem' }}>
      {/* Back */}
      <Link to="/chat" style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.375rem',
        color: 'var(--color-text-secondary)',
        fontSize: 'var(--font-size-sm)',
        marginBottom: '1.5rem',
        textDecoration: 'none',
      }}>
        <ArrowLeft size={16} /> Back to Chat
      </Link>

      {/* Hero Image */}
      <div style={{
        position: 'relative',
        borderRadius: 'var(--radius-2xl)',
        overflow: 'hidden',
        height: 360,
        marginBottom: '2rem',
      }}>
        <img src={imageUrl} alt={property.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }}
          onError={(e) => { e.target.src = 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800'; }} />
        <div style={{
          position: 'absolute',
          inset: 0,
          background: 'linear-gradient(to top, rgba(0,0,0,0.5) 0%, transparent 50%)',
        }} />
        <div style={{ position: 'absolute', bottom: 24, left: 24, color: 'white' }}>
          <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 800, marginBottom: '0.25rem' }}>
            {property.title}
          </h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', opacity: 0.9 }}>
            <MapPin size={14} /> {property.address || `${property.locality}, ${property.city}`}
          </div>
        </div>
        <div style={{ position: 'absolute', bottom: 24, right: 24 }}>
          <div style={{
            background: 'rgba(255,255,255,0.95)',
            padding: '0.5rem 1.25rem',
            borderRadius: 'var(--radius-xl)',
            fontWeight: 800,
            fontSize: 'var(--font-size-xl)',
            color: 'var(--color-primary-dark)',
          }}>
            {property.formatted_price || `₹${(property.price / 100000).toFixed(0)} Lakh`}
          </div>
        </div>
        <button onClick={() => setIsFavorite(!isFavorite)} style={{
          position: 'absolute', top: 16, right: 16, width: 44, height: 44, borderRadius: '50%',
          background: 'rgba(255,255,255,0.9)', border: 'none', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <Heart size={22} fill={isFavorite ? '#ef4444' : 'none'} color={isFavorite ? '#ef4444' : '#64748b'} />
        </button>
      </div>

      {/* Content Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '2rem', alignItems: 'start' }}>
        {/* Left Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Specs Row */}
          <div className="card" style={{ padding: '1.25rem', display: 'flex', justifyContent: 'space-around' }}>
            <SpecItem icon={Bed} value={property.bedrooms} label="Bedrooms" />
            <Divider />
            <SpecItem icon={Bath} value={property.bathrooms} label="Bathrooms" />
            <Divider />
            <SpecItem icon={Maximize} value={property.area_sqft} label="Sq. Ft." />
          </div>

          {/* About */}
          <div className="card" style={{ padding: '1.5rem' }}>
            <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 700, marginBottom: '1rem' }}>About this Property</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: 'var(--font-size-sm)' }}>
              <InfoRow label="Type" value={property.property_type || 'Apartment'} />
              <InfoRow label="Furnishing" value={property.furnishing || 'Semi-Furnished'} />
              <InfoRow label="Floor" value={property.floor || 'N/A'} />
              <InfoRow label="City" value={property.city} />
            </div>
            {property.amenities?.length > 0 && (
              <div style={{ marginTop: '1rem' }}>
                <h4 style={{ fontSize: 'var(--font-size-sm)', fontWeight: 600, marginBottom: '0.5rem' }}>Amenities</h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.375rem' }}>
                  {property.amenities.map((a) => (
                    <span key={a} className="badge badge-primary">{a}</span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Price History */}
          {history?.price_history?.length > 0 && (
            <div className="card" style={{ padding: '1.5rem' }}>
              <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 700, marginBottom: '0.5rem' }}>
                Price History
              </h3>
              <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-success)', fontWeight: 600, marginBottom: '1rem' }}>
                <TrendingUp size={14} style={{ verticalAlign: 'middle', marginRight: 4 }} />
                {history.appreciation_rate}% annual appreciation
              </p>
              <div style={{
                display: 'flex',
                alignItems: 'flex-end',
                gap: 2,
                height: 120,
                padding: '0.5rem 0',
              }}>
                {history.price_history.filter((_, i) => i % 6 === 0).map((point, idx, arr) => {
                  const prices = arr.map((p) => p.price);
                  const minP = Math.min(...prices);
                  const maxP = Math.max(...prices);
                  const range = maxP - minP || 1;
                  const height = ((point.price - minP) / range) * 100 + 10;
                  return (
                    <div key={idx} title={`${point.date}: ₹${(point.price / 100000).toFixed(0)}L`}
                      style={{
                        flex: 1,
                        height: `${height}%`,
                        background: 'var(--gradient-primary)',
                        borderRadius: '3px 3px 0 0',
                        opacity: 0.7 + (idx / arr.length) * 0.3,
                        transition: 'all var(--transition-fast)',
                        cursor: 'pointer',
                        minWidth: 6,
                      }}
                      onMouseOver={(e) => { e.currentTarget.style.opacity = '1'; }}
                      onMouseOut={(e) => { e.currentTarget.style.opacity = `${0.7 + (idx / arr.length) * 0.3}`; }}
                    />
                  );
                })}
              </div>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: 'var(--font-size-xs)',
                color: 'var(--color-text-muted)',
                marginTop: '0.25rem',
              }}>
                <span>{history.price_history[0]?.date}</span>
                <span>{history.price_history[history.price_history.length - 1]?.date}</span>
              </div>
            </div>
          )}

          {/* Nearby */}
          <div className="card" style={{ padding: '1.5rem' }}>
            <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 700, marginBottom: '1rem' }}>Neighborhood</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <NearbyMetric icon={Train} label="Metro" value={property.metro_distance_km ? `${property.metro_distance_km} km` : 'N/A'} sub={property.nearest_metro} />
              <NearbyMetric icon={Shield} label="Safety" value={property.crime_score ? `${property.crime_score}/100` : 'N/A'} />
              <NearbyMetric icon={Star} label="Schools" value={property.school_rating ? `${property.school_rating}/10` : 'N/A'} />
              <NearbyMetric icon={TreePine} label="Parks" value={property.parks_nearby || 0} />
              <NearbyMetric icon={UtensilsCrossed} label="Restaurants" value={property.restaurants_nearby || 0} />
              <NearbyMetric icon={ShoppingCart} label="Supermarkets" value={property.supermarkets_nearby || 0} />
            </div>
          </div>
        </div>

        {/* Right Column — Score */}
        <div style={{ position: 'sticky', top: 'calc(var(--navbar-height) + 1.5rem)' }}>
          {property.overall_score != null && (
            <div className="card" style={{ padding: '1.5rem', marginBottom: '1rem' }}>
              <div style={{ textAlign: 'center', marginBottom: '1.25rem' }}>
                <div style={{
                  width: 80,
                  height: 80,
                  borderRadius: '50%',
                  background: property.overall_score >= 75 ? 'rgba(16,185,129,0.1)' : property.overall_score >= 50 ? 'rgba(245,158,11,0.1)' : 'rgba(239,68,68,0.1)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 0.75rem',
                }}>
                  <span style={{
                    fontSize: 'var(--font-size-2xl)',
                    fontWeight: 800,
                    color: property.overall_score >= 75 ? 'var(--color-success)' : property.overall_score >= 50 ? 'var(--color-accent)' : 'var(--color-error)',
                  }}>
                    {property.overall_score.toFixed(0)}
                  </span>
                </div>
                <h4 style={{ fontWeight: 700, fontSize: 'var(--font-size-sm)' }}>Overall Score</h4>
                {property.confidence && (
                  <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)' }}>
                    {(property.confidence * 100).toFixed(0)}% confidence
                  </span>
                )}
              </div>
              <ScoreBreakdown breakdown={property.score_breakdown} weights={null} />
            </div>
          )}

          <Link to="/chat" className="btn btn-primary" style={{
            width: '100%',
            padding: '0.875rem',
            justifyContent: 'center',
            borderRadius: 'var(--radius-xl)',
          }}>
            Ask about this property
          </Link>
        </div>
      </div>
    </div>
  );
}

function SpecItem({ icon: Icon, value, label }) {
  return (
    <div style={{ textAlign: 'center' }}>
      <Icon size={20} color="var(--color-primary)" style={{ marginBottom: '0.375rem' }} />
      <div style={{ fontSize: 'var(--font-size-xl)', fontWeight: 800 }}>{value}</div>
      <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)' }}>{label}</div>
    </div>
  );
}

function Divider() {
  return <div style={{ width: 1, background: 'var(--color-border)', alignSelf: 'stretch' }} />;
}

function InfoRow({ label, value }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
      <span style={{ color: 'var(--color-text-muted)' }}>{label}</span>
      <span style={{ fontWeight: 600 }}>{value}</span>
    </div>
  );
}

function NearbyMetric({ icon: Icon, label, value, sub }) {
  return (
    <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
      <div style={{
        width: 40, height: 40, borderRadius: 'var(--radius-md)',
        background: 'var(--color-bg-tertiary)', display: 'flex',
        alignItems: 'center', justifyContent: 'center',
      }}>
        <Icon size={18} color="var(--color-primary)" />
      </div>
      <div>
        <div style={{ fontSize: 'var(--font-size-sm)', fontWeight: 700 }}>{value}</div>
        <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)' }}>{sub || label}</div>
      </div>
    </div>
  );
}
