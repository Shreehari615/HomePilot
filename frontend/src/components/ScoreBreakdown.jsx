const LABELS = {
  budget_match: 'Budget Match',
  commute: 'Commute & Transit',
  school: 'School Quality',
  safety: 'Safety & Security',
  amenities: 'Amenities',
};

const COLORS = {
  budget_match: '#6366f1',
  commute: '#8b5cf6',
  school: '#f59e0b',
  safety: '#10b981',
  amenities: '#ec4899',
};

export default function ScoreBreakdown({ breakdown, weights }) {
  if (!breakdown) return null;

  const entries = Object.entries(breakdown).filter(([key]) => LABELS[key]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
      <h4 style={{
        fontSize: 'var(--font-size-sm)',
        fontWeight: 700,
        color: 'var(--color-text)',
        marginBottom: '0.25rem',
      }}>
        Score Breakdown
      </h4>
      {entries.map(([key, value]) => {
        const pct = Math.round(value * 100);
        const weight = weights?.[key];
        return (
          <div key={key}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '0.25rem',
            }}>
              <span style={{
                fontSize: 'var(--font-size-xs)',
                fontWeight: 600,
                color: 'var(--color-text-secondary)',
              }}>
                {LABELS[key]}
                {weight != null && (
                  <span style={{ fontWeight: 400, color: 'var(--color-text-muted)', marginLeft: '0.375rem' }}>
                    ({Math.round(weight * 100)}% weight)
                  </span>
                )}
              </span>
              <span style={{
                fontSize: 'var(--font-size-xs)',
                fontWeight: 700,
                color: COLORS[key],
              }}>
                {pct}%
              </span>
            </div>
            <div className="score-bar-track">
              <div
                className="score-bar-fill"
                style={{
                  width: `${pct}%`,
                  background: COLORS[key],
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
