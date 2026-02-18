import React, { useEffect, useState, useCallback } from 'react';
import { orderApi } from '../services/api';

// ── Status Badge ──────────────────────────────────────────
function StatusBadge({ status }) {
  const config = {
    pending:    { color: '#fbbf24', bg: 'rgba(251,191,36,0.1)',    dot: '●', label: 'PENDING' },
    processing: { color: '#818cf8', bg: 'rgba(129,140,248,0.1)',   dot: '◌', label: 'PROCESSING' },
    completed:  { color: '#6ee7b7', bg: 'rgba(110,231,183,0.1)',   dot: '◉', label: 'COMPLETED' },
  }[status] || { color: 'var(--muted)', bg: 'transparent', dot: '○', label: status?.toUpperCase() };

  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 5,
      fontSize: 10, fontWeight: 500, letterSpacing: '0.08em',
      color: config.color, background: config.bg,
      border: `1px solid ${config.color}33`,
      padding: '3px 8px', borderRadius: 20,
      animation: status === 'processing' ? 'pulse 1.5s infinite' : 'none',
    }}>
      {config.dot} {config.label}
    </span>
  );
}

// ── Order Card ────────────────────────────────────────────
function OrderCard({ order, index }) {
  const [expanded, setExpanded] = useState(false);

  const handleDownload = (e) => {
    e.stopPropagation();
    if (order.pdf_url) window.open(order.pdf_url, '_blank');
  };

  return (
    <div
      className="fade-up"
      style={{
        animationDelay: `${index * 50}ms`,
        background: 'var(--bg2)',
        border: '1px solid var(--border)',
        borderRadius: 10,
        overflow: 'hidden',
        transition: 'border-color 0.2s',
      }}
      onMouseEnter={e => e.currentTarget.style.borderColor = 'rgba(129,140,248,0.3)'}
      onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
    >
      {/* Order Header - clickable to expand */}
      <div
        onClick={() => setExpanded(v => !v)}
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr auto auto auto',
          alignItems: 'center',
          gap: '1rem',
          padding: '1rem 1.25rem',
          cursor: 'pointer',
        }}
      >
        {/* Left: order info */}
        <div>
          <div style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 13, fontWeight: 500,
            color: 'var(--text)', marginBottom: 3,
          }}>
            {order.order_number}
          </div>
          <div style={{ fontSize: 11, color: 'var(--muted)' }}>
            {order.customer_name}
            <span style={{ margin: '0 6px', opacity: 0.4 }}>·</span>
            {new Date(order.created_at).toLocaleString('sr-RS')}
          </div>
        </div>

        {/* Status */}
        <StatusBadge status={order.status} />

        {/* Total */}
        <span style={{
          fontFamily: 'var(--font-head)',
          fontSize: 16, fontWeight: 700,
          color: 'var(--accent)',
        }}>
          ${parseFloat(order.total_price).toFixed(2)}
        </span>

        {/* PDF button or expand arrow */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {order.pdf_url && (
            <button
              onClick={handleDownload}
              style={{
                background: 'rgba(110,231,183,0.1)',
                border: '1px solid rgba(110,231,183,0.2)',
                borderRadius: 5,
                color: 'var(--accent)',
                fontSize: 11, fontFamily: 'var(--font-mono)',
                padding: '4px 10px', cursor: 'pointer',
                transition: 'all 0.15s', letterSpacing: '0.05em',
              }}
              onMouseEnter={e => e.target.style.background = 'rgba(110,231,183,0.2)'}
              onMouseLeave={e => e.target.style.background = 'rgba(110,231,183,0.1)'}
            >
              ↓ PDF
            </button>
          )}
          <span style={{
            color: 'var(--muted)', fontSize: 12,
            transform: expanded ? 'rotate(90deg)' : 'rotate(0deg)',
            transition: 'transform 0.2s',
            display: 'inline-block',
          }}>▶</span>
        </div>
      </div>

      {/* Expanded items */}
      {expanded && (
        <div style={{
          borderTop: '1px solid var(--border)',
          background: 'var(--bg)',
          padding: '1rem 1.25rem',
        }}>
          {/* Items table header */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '2fr 60px 90px 90px',
            gap: '0.5rem',
            fontSize: 10, color: 'var(--muted)',
            letterSpacing: '0.08em',
            marginBottom: 8,
            paddingBottom: 8,
            borderBottom: '1px solid var(--border)',
          }}>
            <span>PRODUCT</span>
            <span style={{ textAlign: 'center' }}>QTY</span>
            <span style={{ textAlign: 'right' }}>UNIT</span>
            <span style={{ textAlign: 'right' }}>TOTAL</span>
          </div>

          {(order.items || []).map(item => (
            <div key={item.id} style={{
              display: 'grid',
              gridTemplateColumns: '2fr 60px 90px 90px',
              gap: '0.5rem',
              fontSize: 12,
              padding: '5px 0',
              borderBottom: '1px solid rgba(42,42,58,0.5)',
            }}>
              <div>
                <span style={{ color: 'var(--text)' }}>{item.product_name}</span>
                <span style={{ color: 'var(--muted)', marginLeft: 6, fontSize: 10 }}>{item.product_code}</span>
              </div>
              <span style={{ textAlign: 'center', color: 'var(--muted)' }}>{item.quantity}</span>
              <span style={{ textAlign: 'right', color: 'var(--muted)' }}>
                ${parseFloat(item.unit_price).toFixed(2)}
              </span>
              <span style={{ textAlign: 'right', color: 'var(--text)' }}>
                ${parseFloat(item.total_price).toFixed(2)}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Orders Page ───────────────────────────────────────────
export default function Orders() {
  const [orders, setOrders]         = useState([]);
  const [loading, setLoading]       = useState(true);
  const [error, setError]           = useState(null);
  const [lastRefresh, setLastRefresh] = useState(null);

  const fetchOrders = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      const data = await orderApi.getOrders();
      setOrders(data.orders || []);
      setLastRefresh(new Date());
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => { fetchOrders(); }, [fetchOrders]);

  // Auto-refresh ogni 5s se ci sono ordini pending/processing
  useEffect(() => {
    const hasPending = orders.some(o => ['pending', 'processing'].includes(o.status));
    if (!hasPending) return;

    const interval = setInterval(() => fetchOrders(true), 5000);
    return () => clearInterval(interval);
  }, [orders, fetchOrders]);

  // Stats
  const stats = orders.reduce((acc, o) => {
    acc[o.status] = (acc[o.status] || 0) + 1;
    return acc;
  }, {});

  if (loading && orders.length === 0) return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12, color: 'var(--muted)', padding: '3rem 0' }}>
      <div style={{
        width: 18, height: 18,
        border: '2px solid var(--border)',
        borderTop: '2px solid var(--accent2)',
        borderRadius: '50%',
        animation: 'spin 0.8s linear infinite',
      }} />
      Loading orders...
    </div>
  );

  return (
    <div className="fade-up">
      {/* Header */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
          <h1 style={{
            fontFamily: 'var(--font-head)',
            fontSize: 32, fontWeight: 800, letterSpacing: '-0.03em',
          }}>Orders</h1>

          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            {lastRefresh && (
              <span style={{ fontSize: 10, color: 'var(--muted)' }}>
                Updated {lastRefresh.toLocaleTimeString('sr-RS')}
              </span>
            )}
            <button
              onClick={() => fetchOrders()}
              style={{
                background: 'transparent', color: 'var(--muted)',
                border: '1px solid var(--border)', borderRadius: 5,
                padding: '4px 12px', fontSize: 11,
                fontFamily: 'var(--font-mono)', cursor: 'pointer',
                letterSpacing: '0.05em', transition: 'color 0.15s',
              }}
              onMouseEnter={e => e.target.style.color = 'var(--text)'}
              onMouseLeave={e => e.target.style.color = 'var(--muted)'}
            >
              ↻ REFRESH
            </button>
          </div>
        </div>

        {/* Stats row */}
        {orders.length > 0 && (
          <div style={{ display: 'flex', gap: 12, marginTop: 12 }}>
            {[
              { key: 'pending',    label: 'Pending',    color: '#fbbf24' },
              { key: 'processing', label: 'Processing', color: '#818cf8' },
              { key: 'completed',  label: 'Completed',  color: '#6ee7b7' },
            ].map(({ key, label, color }) => (
              <div key={key} style={{
                fontSize: 11, color,
                background: `${color}11`,
                border: `1px solid ${color}33`,
                padding: '3px 10px', borderRadius: 4,
              }}>
                {stats[key] || 0} {label}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <div style={{
          padding: '1rem',
          background: 'rgba(248,113,113,0.08)',
          border: '1px solid rgba(248,113,113,0.2)',
          borderRadius: 8, color: 'var(--danger)',
          fontSize: 13, marginBottom: '1rem',
        }}>
          ✕ {error} — Make sure Order Service is running on :5002
        </div>
      )}

      {/* Orders list */}
      {orders.length === 0 && !error ? (
        <div style={{
          padding: '4rem', textAlign: 'center',
          border: '1px dashed var(--border)', borderRadius: 10,
          color: 'var(--muted)',
        }}>
          <div style={{ fontSize: 32, marginBottom: 12, opacity: 0.4 }}>◉</div>
          <div style={{ fontSize: 13 }}>No orders yet</div>
          <div style={{ fontSize: 11, marginTop: 6 }}>
            Create one from the <strong style={{ color: 'var(--accent2)' }}>New Order</strong> page
          </div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {orders.map((order, i) => (
            <OrderCard key={order.id} order={order} index={i} />
          ))}
        </div>
      )}

      {/* Auto-refresh notice */}
      {orders.some(o => ['pending', 'processing'].includes(o.status)) && (
        <div style={{
          marginTop: '1.5rem', fontSize: 11, color: 'var(--muted)',
          display: 'flex', alignItems: 'center', gap: 6,
        }}>
          <div style={{
            width: 6, height: 6, borderRadius: '50%',
            background: 'var(--accent2)',
            animation: 'pulse 1.5s infinite',
          }} />
          Auto-refreshing every 5s while orders are processing...
        </div>
      )}
    </div>
  );
}
