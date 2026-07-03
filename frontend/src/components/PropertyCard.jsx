import { Heart, MapPin, Bed, Bath, Maximize, Star, Train, Shield, TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function PropertyCard({ property, explanation, onFavorite, isFavorite, style }) {
  const score = property.overall_score ?? property.overallScore;
  const scoreColor = score >= 75 ? 'var(--color-success)' : score >= 50 ? 'var(--color-accent)' : 'var(--color-error)';

  const imageUrl = property.images?.[0]?.url || property.image_url || 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800';

  return (
    <div className="card animate-fade-in" style={{
      overflow: 'hidden',
      display: 'flex',
      flexDirection: 'column',
      ...style,
    }}>
      {/* Image Section */}
      <div style={{ position: 'relative', height: 200, overflow: 'hidden' }}>
        <img
          src={imageUrl}
          alt={property.title}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            transition: 'transform var(--transition-slow)',
          }}
          onError={(e) => { e.target.src = 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800'; }}
        />

        {/* Score Badge */}
        {score != null && (
          <div style={{
            position: 'absolute',
            top: 12,
            left: 12,
            background: scoreColor,
            color: 'white',
            fontWeight: 700,
            fontSize: 'var(--font-size-sm)',
            padding: '0.25rem 0.75rem',
            borderRadius: 'var(--radius-full)',
            boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
          }}>
            {score.toFixed(0)}/100
          </div>
        )}

        {/* Rank Badge */}
        {property.rank && (
          <div style={{
            position: 'absolute',
            top: 12,
            right: 52,
            background: 'var(--gradient-accent)',
            color: 'white',
            fontWeight: 700,
            fontSize: 'var(--font-size-xs)',
            padding: '0.25rem 0.625rem',
            borderRadius: 'var(--radius-full)',
          }}>
            #{property.rank}
          </div>
        )}

        {/* Favorite Button */}
        <button
          onClick={(e) => { e.preventDefault(); onFavorite?.(property.id); }}
          style={{
            position: 'absolute',
            top: 10,
            right: 10,
            width: 36,
            height: 36,
            borderRadius: '50%',
            background: 'rgba(255,255,255,0.9)',
            border: 'none',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all var(--transition-fast)',
          }}
        >
          <Heart
            size={18}
            fill={isFavorite ? '#ef4444' : 'none'}
            color={isFavorite ? '#ef4444' : '#64748b'}
          />
        </button>

        {/* Price Tag */}
        <div style={{
          position: 'absolute',
          bottom: 12,
          left: 12,
          background: 'rgba(15, 23, 42, 0.85)',
          backdropFilter: 'blur(8px)',
          color: 'white',
          fontWeight: 700,
          fontSize: 'var(--font-size-lg)',
          padding: '0.375rem 0.875rem',
          borderRadius: 'var(--radius-lg)',
        }}>
          {property.formatted_price || property.formattedPrice || `₹${(property.price / 100000).toFixed(0)}L`}
        </div>
      </div>

      {/* Content */}
      <div style={{ padding: '1rem', flex: 1, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {/* Title & Location */}
        <div>
          <Link to={`/property/${property.id}`} style={{
            fontSize: 'var(--font-size-base)',
            fontWeight: 700,
            color: 'var(--color-text)',
            textDecoration: 'none',
            lineHeight: 1.3,
          }}>
            {property.title}
          </Link>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.25rem',
            marginTop: '0.25rem',
            color: 'var(--color-text-muted)',
            fontSize: 'var(--font-size-sm)',
          }}>
            <MapPin size={13} />
            {property.locality}, {property.city}
          </div>
        </div>

        {/* Specs */}
        <div style={{
          display: 'flex',
          gap: '1rem',
          padding: '0.5rem 0',
          borderTop: '1px solid var(--color-border-light)',
          borderBottom: '1px solid var(--color-border-light)',
        }}>
          <Spec icon={Bed} value={property.bedrooms} label="Beds" />
          <Spec icon={Bath} value={property.bathrooms} label="Baths" />
          <Spec icon={Maximize} value={property.area_sqft || property.areaSqft} label="sqft" />
        </div>

        {/* Metrics */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {property.school_rating != null && (
            <MetricBadge icon={Star} value={`${property.school_rating}/10`} label="School" color="var(--color-accent)" />
          )}
          {property.metro_distance_km != null && (
            <MetricBadge icon={Train} value={`${property.metro_distance_km}km`} label="Metro" color="var(--color-primary)" />
          )}
          {property.crime_score != null && (
            <MetricBadge icon={Shield} value={`${property.crime_score}/100`} label="Safety" color="var(--color-success)" />
          )}
          {property.appreciation_rate != null && (
            <MetricBadge icon={TrendingUp} value={`${property.appreciation_rate}%`} label="Growth" color="#8b5cf6" />
          )}
        </div>

        {/* Explanation */}
        {explanation && (
          <div style={{
            padding: '0.625rem',
            background: 'var(--gradient-card)',
            borderRadius: 'var(--radius-md)',
            fontSize: 'var(--font-size-xs)',
            color: 'var(--color-text-secondary)',
            lineHeight: 1.5,
          }}>
            <div style={{ fontWeight: 600, marginBottom: '0.25rem', color: 'var(--color-primary)' }}>
              Why Recommended
            </div>
            {explanation.recommendation_reason || explanation.recommendationReason}
          </div>
        )}
      </div>
    </div>
  );
}

function Spec({ icon: Icon, value, label }) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '0.25rem',
      fontSize: 'var(--font-size-sm)',
      color: 'var(--color-text-secondary)',
    }}>
      <Icon size={14} color="var(--color-text-muted)" />
      <span style={{ fontWeight: 600, color: 'var(--color-text)' }}>{value}</span>
      <span>{label}</span>
    </div>
  );
}

function MetricBadge({ icon: Icon, value, label, color }) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '0.25rem',
      padding: '0.2rem 0.5rem',
      borderRadius: 'var(--radius-full)',
      fontSize: 'var(--font-size-xs)',
      fontWeight: 600,
      background: `${color}11`,
      color: color,
    }}>
      <Icon size={12} />
      <span>{value}</span>
    </div>
  );
}
