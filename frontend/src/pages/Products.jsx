import React, { useEffect, useState } from 'react';
import { catalogApi } from '../services/api';

// ── Shared UI ─────────────────────────────────────────────
function PageHeader({ title, subtitle, count }) {
  return (
    <div style={{ marginBottom: '2rem' }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '1rem' }}>
        <h1 style={{
          fontFamily: 'var(--font-head)',
          fontSize: 32,
          fontWeight: 800,
          color: 'var(--text)',
          letterSpacing: '-0.03em',
        }}>{title}</h1>
        {count !== undefined && (
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 12,
            color: 'var(--accent)',
            background: 'rgba(110,231,183,0.1)',
            border: '1px solid rgba(110,231,183,0.2)',
            padding: '2px 8px',
            borderRadius: 4,
          }}>{count} items</span>
        )}
      </div>
      {subtitle && (
        <p style={{ color: 'var(--muted)', fontSize: 13, marginTop: 6 }}>{subtitle}</p>
      )}
    </div>
  );
}

function Spinner() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12, color: 'var(--muted)', padding: '3rem 0' }}>
      <div style={{
        width: 18, height: 18,
        border: '2px solid var(--border)',
        borderTop: '2px solid var(--accent)',
        borderRadius: '50%',
        animation: 'spin 0.8s linear infinite',
      }} />
      Loading...
    </div>
  );
}

function StockBadge({ qty }) {
  if (qty === 0) return (
    <span style={{ fontSize: 10, color: 'var(--danger)', background: 'rgba(248,113,113,0.1)', padding: '2px 8px', borderRadius: 3 }}>
      OUT OF STOCK
    </span>
  );
  if (qty <= 5) return (
    <span style={{ fontSize: 10, color: 'var(--warning)', background: 'rgba(251,191,36,0.1)', padding: '2px 8px', borderRadius: 3 }}>
      LOW · {qty}
    </span>
  );
  return (
    <span style={{ fontSize: 10, color: 'var(--accent)', background: 'rgba(110,231,183,0.08)', padding: '2px 8px', borderRadius: 3 }}>
      IN STOCK · {qty}
    </span>
  );
}

// ── Product Card ──────────────────────────────────────────
function ProductCard({ product, index }) {
  return (
    <div
      className="fade-up"
      style={{
        animationDelay: `${index * 40}ms`,
        background: 'var(--bg2)',
        border: '1px solid var(--border)',
        borderRadius: 10,
        overflow: 'hidden',
        transition: 'border-color 0.2s, transform 0.2s',
        cursor: 'default',
      }}
      onMouseEnter={e => {
        e.currentTarget.style.borderColor = 'rgba(110,231,183,0.3)';
        e.currentTarget.style.transform = 'translateY(-2px)';
      }}
      onMouseLeave={e => {
        e.currentTarget.style.borderColor = 'var(--border)';
        e.currentTarget.style.transform = 'translateY(0)';
      }}
    >
      {/* Product Image */}
      <div style={{
        height: 140,
        background: 'var(--bg3)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        borderBottom: '1px solid var(--border)',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.name}
            style={{ width: '100%', height: '100%', objectFit: 'cover', opacity: 0.8 }}
            onError={e => { e.target.style.display = 'none'; }}
          />
        ) : (
          <span style={{ fontSize: 36, opacity: 0.3 }}>◈</span>
        )}
        {/* Code badge top-right */}
        <div style={{
          position: 'absolute', top: 8, right: 8,
          fontSize: 9, fontFamily: 'var(--font-mono)',
          color: 'var(--muted)',
          background: 'rgba(10,10,15,0.8)',
          padding: '2px 6px', borderRadius: 3,
          letterSpacing: '0.05em',
        }}>
          {product.code}
        </div>
      </div>

      {/* Product Info */}
      <div style={{ padding: '1rem' }}>
        <div style={{
          fontFamily: 'var(--font-head)',
          fontWeight: 600,
          fontSize: 14,
          color: 'var(--text)',
          marginBottom: 8,
          lineHeight: 1.3,
        }}>
          {product.name}
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 16,
            fontWeight: 500,
            color: 'var(--accent)',
          }}>
            ${parseFloat(product.price).toFixed(2)}
          </span>
          <StockBadge qty={product.stock_quantity} />
        </div>
      </div>
    </div>
  );
}

// ── Products Page ─────────────────────────────────────────
export default function Products() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState(null);

  useEffect(() => {
    catalogApi.getProducts()
      .then(data => setProducts(data.products || []))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spinner />;

  if (error) return (
    <div style={{
      padding: '1.5rem',
      background: 'rgba(248,113,113,0.08)',
      border: '1px solid rgba(248,113,113,0.2)',
      borderRadius: 8,
      color: 'var(--danger)',
      fontSize: 13,
    }}>
      ✕ {error} — Make sure Catalog Service is running on :5001
    </div>
  );

  return (
    <div className="fade-up">
      <PageHeader
        title="Product Catalog"
        subtitle="Browse available products and stock levels"
        count={products.length}
      />

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
        gap: '1rem',
      }}>
        {products.map((p, i) => (
          <ProductCard key={p.id} product={p} index={i} />
        ))}
      </div>

      {products.length === 0 && (
        <div style={{ color: 'var(--muted)', padding: '3rem 0', textAlign: 'center' }}>
          No products found.
        </div>
      )}
    </div>
  );
}
