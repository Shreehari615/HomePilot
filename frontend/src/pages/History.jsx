import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Clock, MapPin, Bed, Heart, Loader2 } from 'lucide-react';
import { getAllProperties } from '../services/api';

export default function History() {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const data = await getAllProperties();
        setProperties(data.properties || []);
      } catch (err) {
        console.error('Failed to load properties:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, []);

  const cities = ['all', ...new Set(properties.map((p) => p.city))];
  const filtered = filter === 'all' ? properties : properties.filter((p) => p.city === filter);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '50vh' }}>
        <Loader2 size={32} style={{ color: 'var(--color-primary)', animation: 'spin 1s linear infinite' }} />
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto', padding: '2rem 1.5rem' }}>
      {/* Header */}
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 800, marginBottom: '0.5rem' }}>
          Browse Properties
        </h1>
        <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--font-size-sm)' }}>
          {filtered.length} properties available across {cities.length - 1} cities
        </p>
      </div>

      {/* City Filters */}
      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1.5rem' }}>
        {cities.map((city) => (
          <button
            key={city}
            onClick={() => setFilter(city)}
            style={{
              padding: '0.375rem 1rem',
              borderRadius: 'var(--radius-full)',
              border: '1px solid',
              borderColor: filter === city ? 'var(--color-primary)' : 'var(--color-border)',
              background: filter === city ? 'var(--color-primary)' : 'var(--color-bg-secondary)',
              color: filter === city ? 'white' : 'var(--color-text-secondary)',
              fontSize: 'var(--font-size-sm)',
              fontWeight: 600,
              cursor: 'pointer',
              fontFamily: 'var(--font-family)',
              transition: 'all var(--transition-fast)',
              textTransform: 'capitalize',
            }}
          >
            {city === 'all' ? 'All Cities' : city}
          </button>
        ))}
      </div>

      {/* Property Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
        gap: '1.25rem',
      }}>
        {filtered.map((property) => (
          <Link
            key={property.id}
            to={`/property/${property.id}`}
            className="card animate-fade-in"
            style={{
              overflow: 'hidden',
              textDecoration: 'none',
              color: 'inherit',
            }}
          >
            {/* Image */}
            <div style={{ height: 180, overflow: 'hidden', position: 'relative' }}>
              <img
                src={property.image_url || 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800'}
                alt={property.title}
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                onError={(e) => { e.target.src = 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800'; }}
              />
              <div style={{
                position: 'absolute',
                bottom: 10,
                left: 10,
                background: 'rgba(15,23,42,0.85)',
                backdropFilter: 'blur(8px)',
                color: 'white',
                fontWeight: 700,
                padding: '0.25rem 0.75rem',
                borderRadius: 'var(--radius-md)',
                fontSize: 'var(--font-size-base)',
              }}>
                {property.formatted_price}
              </div>
            </div>

            {/* Content */}
            <div style={{ padding: '1rem' }}>
              <h3 style={{ fontSize: 'var(--font-size-sm)', fontWeight: 700, marginBottom: '0.25rem' }}>
                {property.title}
              </h3>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.25rem',
                color: 'var(--color-text-muted)',
                fontSize: 'var(--font-size-xs)',
                marginBottom: '0.625rem',
              }}>
                <MapPin size={12} />
                {property.locality}, {property.city}
              </div>
              <div style={{
                display: 'flex',
                gap: '1rem',
                fontSize: 'var(--font-size-xs)',
                color: 'var(--color-text-secondary)',
              }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <Bed size={13} /> {property.bedrooms} Beds
                </span>
                <span>{property.bathrooms} Baths</span>
                <span>{property.area_sqft} sqft</span>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {filtered.length === 0 && (
        <div style={{
          textAlign: 'center',
          padding: '4rem 2rem',
          color: 'var(--color-text-muted)',
        }}>
          <p>No properties found for this city.</p>
        </div>
      )}
    </div>
  );
}
