import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { catalogApi, orderApi } from '../services/api';

// ── Reusable Input ────────────────────────────────────────
function Field({ label, children, error }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      <label style={{ fontSize: 10, letterSpacing: '0.1em', color: 'var(--muted)', fontWeight: 500 }}>
        {label}
      </label>
      {children}
      {error && <span style={{ fontSize: 11, color: 'var(--danger)' }}>{error}</span>}
    </div>
  );
}

function Input({ style, ...props }) {
  return (
    <input
      {...props}
      style={{
        background: 'var(--bg3)',
        border: '1px solid var(--border)',
        borderRadius: 6,
        color: 'var(--text)',
        fontFamily: 'var(--font-mono)',
        fontSize: 13,
        padding: '0.6rem 0.875rem',
        outline: 'none',
        transition: 'border-color 0.15s',
        width: '100%',
        ...style,
      }}
      onFocus={e => e.target.style.borderColor = 'rgba(110,231,183,0.5)'}
      onBlur={e  => e.target.style.borderColor = 'var(--border)'}
    />
  );
}

// ── Product Row in order builder ──────────────────────────
function ProductRow({ product, item, onQtyChange, onRemove }) {
  const total = parseFloat(product.price) * item.quantity;
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: '1fr 90px 90px 32px',
      gap: '0.75rem',
      alignItems: 'center',
      padding: '0.75rem 1rem',
      background: 'var(--bg3)',
      border: '1px solid var(--border)',
      borderRadius: 6,
    }}>
      <div>
        <div style={{ fontSize: 12, fontWeight: 500, color: 'var(--text)' }}>{product.name}</div>
        <div style={{ fontSize: 10, color: 'var(--muted)', marginTop: 2 }}>
          {product.code} · ${parseFloat(product.price).toFixed(2)} each
        </div>
      </div>

      {/* Quantity stepper */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
        <button
          onClick={() => onQtyChange(Math.max(1, item.quantity - 1))}
          style={{
            width: 22, height: 22, border: '1px solid var(--border)',
            background: 'var(--bg2)', color: 'var(--text)',
            borderRadius: 4, cursor: 'pointer', fontSize: 14, lineHeight: 1,
          }}
        >−</button>
        <span style={{ width: 28, textAlign: 'center', fontSize: 13 }}>{item.quantity}</span>
        <button
          onClick={() => onQtyChange(Math.min(product.stock_quantity, item.quantity + 1))}
          style={{
            width: 22, height: 22, border: '1px solid var(--border)',
            background: 'var(--bg2)', color: 'var(--text)',
            borderRadius: 4, cursor: 'pointer', fontSize: 14, lineHeight: 1,
          }}
        >+</button>
      </div>

      <div style={{ fontSize: 13, color: 'var(--accent)', fontWeight: 500, textAlign: 'right' }}>
        ${total.toFixed(2)}
      </div>

      <button
        onClick={onRemove}
        style={{
          background: 'none', border: 'none', color: 'var(--muted)',
          cursor: 'pointer', fontSize: 16, padding: 0, lineHeight: 1,
          transition: 'color 0.15s',
        }}
        onMouseEnter={e => e.target.style.color = 'var(--danger)'}
        onMouseLeave={e => e.target.style.color = 'var(--muted)'}
      >×</button>
    </div>
  );
}

// ── Create Order Page ─────────────────────────────────────
export default function CreateOrder() {
  const navigate = useNavigate();

  const [products, setProducts]     = useState([]);
  const [loadingProds, setLoadingProds] = useState(true);

  const [customerId, setCustomerId]   = useState('');
  const [customerName, setCustomerName] = useState('');
  const [orderItems, setOrderItems]   = useState([]);   // [{product_id, quantity}]
  const [selectedPid, setSelectedPid] = useState('');

  const [submitting, setSubmitting] = useState(false);
  const [error, setError]           = useState(null);
  const [success, setSuccess]       = useState(null);

  useEffect(() => {
    catalogApi.getProducts()
      .then(d => setProducts(d.products || []))
      .finally(() => setLoadingProds(false));
  }, []);

  const productMap = Object.fromEntries(products.map(p => [p.id, p]));

  const addProduct = () => {
    if (!selectedPid) return;
    const pid = parseInt(selectedPid);
    if (orderItems.find(i => i.product_id === pid)) return; // Already added
    setOrderItems(prev => [...prev, { product_id: pid, quantity: 1 }]);
    setSelectedPid('');
  };

  const updateQty = (pid, qty) => {
    setOrderItems(prev => prev.map(i => i.product_id === pid ? { ...i, quantity: qty } : i));
  };

  const removeItem = (pid) => {
    setOrderItems(prev => prev.filter(i => i.product_id !== pid));
  };

  const total = orderItems.reduce((sum, item) => {
    const p = productMap[item.product_id];
    return sum + (p ? parseFloat(p.price) * item.quantity : 0);
  }, 0);

  const handleSubmit = async () => {
    setError(null);
    if (!customerId.trim()) return setError('Customer ID is required');
    if (!customerName.trim()) return setError('Customer name is required');
    if (orderItems.length === 0) return setError('Add at least one product');

    setSubmitting(true);
    try {
      const result = await orderApi.createOrder({
        customer_id: customerId.trim(),
        customer_name: customerName.trim(),
        items: orderItems,
      });
      setSuccess(result.order);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  // ── Success screen ───────────────────────────────────────
  if (success) {
    return (
      <div className="fade-up" style={{ maxWidth: 520 }}>
        <div style={{
          background: 'rgba(110,231,183,0.06)',
          border: '1px solid rgba(110,231,183,0.2)',
          borderRadius: 12,
          padding: '2rem',
          textAlign: 'center',
        }}>
          <div style={{ fontSize: 40, marginBottom: 12 }}>✓</div>
          <h2 style={{
            fontFamily: 'var(--font-head)',
            fontSize: 22,
            fontWeight: 700,
            color: 'var(--accent)',
            marginBottom: 8,
          }}>Order Created!</h2>
          <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 4 }}>
            {success.order_number}
          </div>
          <div style={{ fontSize: 20, color: 'var(--text)', margin: '1rem 0' }}>
            ${parseFloat(success.total_price).toFixed(2)}
          </div>
          <div style={{
            display: 'inline-block',
            fontSize: 11,
            padding: '3px 12px',
            borderRadius: 20,
            background: 'rgba(251,191,36,0.1)',
            color: 'var(--warning)',
            border: '1px solid rgba(251,191,36,0.2)',
            marginBottom: '1.5rem',
          }}>
            ● PENDING — Invoice generating...
          </div>
          <p style={{ fontSize: 12, color: 'var(--muted)', marginBottom: '1.5rem' }}>
            Your invoice is being generated asynchronously.<br />
            Check order status in the Orders page.
          </p>
          <div style={{ display: 'flex', gap: 8, justifyContent: 'center' }}>
            <button
              onClick={() => navigate('/orders')}
              style={{
                background: 'var(--accent)', color: 'var(--bg)',
                border: 'none', borderRadius: 6,
                padding: '0.6rem 1.25rem',
                fontSize: 12, fontFamily: 'var(--font-mono)',
                fontWeight: 500, cursor: 'pointer', letterSpacing: '0.05em',
              }}
            >
              VIEW ORDERS
            </button>
            <button
              onClick={() => { setSuccess(null); setOrderItems([]); setCustomerId(''); setCustomerName(''); }}
              style={{
                background: 'transparent', color: 'var(--muted)',
                border: '1px solid var(--border)', borderRadius: 6,
                padding: '0.6rem 1.25rem',
                fontSize: 12, fontFamily: 'var(--font-mono)',
                cursor: 'pointer', letterSpacing: '0.05em',
              }}
            >
              NEW ORDER
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ── Order Builder ────────────────────────────────────────
  return (
    <div className="fade-up">
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{
          fontFamily: 'var(--font-head)',
          fontSize: 32, fontWeight: 800,
          letterSpacing: '-0.03em',
        }}>New Order</h1>
        <p style={{ color: 'var(--muted)', fontSize: 13, marginTop: 6 }}>
          Fill in customer details and add products
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: '2rem', maxWidth: 900 }}>

        {/* Left column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

          {/* Customer info */}
          <section style={{
            background: 'var(--bg2)',
            border: '1px solid var(--border)',
            borderRadius: 10,
            padding: '1.5rem',
          }}>
            <div style={{
              fontSize: 10, letterSpacing: '0.1em',
              color: 'var(--accent)', marginBottom: '1.25rem', fontWeight: 600,
            }}>
              CUSTOMER DETAILS
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <Field label="CUSTOMER ID">
                <Input
                  placeholder="e.g. CUST-001"
                  value={customerId}
                  onChange={e => setCustomerId(e.target.value)}
                />
              </Field>
              <Field label="CUSTOMER NAME">
                <Input
                  placeholder="e.g. Marko Markovic"
                  value={customerName}
                  onChange={e => setCustomerName(e.target.value)}
                />
              </Field>
            </div>
          </section>

          {/* Product selector */}
          <section style={{
            background: 'var(--bg2)',
            border: '1px solid var(--border)',
            borderRadius: 10,
            padding: '1.5rem',
          }}>
            <div style={{
              fontSize: 10, letterSpacing: '0.1em',
              color: 'var(--accent)', marginBottom: '1.25rem', fontWeight: 600,
            }}>
              ADD PRODUCTS
            </div>

            <div style={{ display: 'flex', gap: 8, marginBottom: '1rem' }}>
              <select
                value={selectedPid}
                onChange={e => setSelectedPid(e.target.value)}
                disabled={loadingProds}
                style={{
                  flex: 1,
                  background: 'var(--bg3)',
                  border: '1px solid var(--border)',
                  borderRadius: 6,
                  color: selectedPid ? 'var(--text)' : 'var(--muted)',
                  fontFamily: 'var(--font-mono)',
                  fontSize: 13,
                  padding: '0.6rem 0.875rem',
                  outline: 'none',
                  cursor: 'pointer',
                }}
              >
                <option value="">Select a product...</option>
                {products.map(p => (
                  <option
                    key={p.id}
                    value={p.id}
                    disabled={p.stock_quantity === 0 || !!orderItems.find(i => i.product_id === p.id)}
                  >
                    {p.name} — ${parseFloat(p.price).toFixed(2)}
                    {p.stock_quantity === 0 ? ' (out of stock)' : ''}
                    {orderItems.find(i => i.product_id === p.id) ? ' (added)' : ''}
                  </option>
                ))}
              </select>
              <button
                onClick={addProduct}
                disabled={!selectedPid}
                style={{
                  background: selectedPid ? 'var(--accent)' : 'var(--bg3)',
                  color: selectedPid ? 'var(--bg)' : 'var(--muted)',
                  border: '1px solid var(--border)',
                  borderRadius: 6,
                  padding: '0 1.25rem',
                  fontSize: 12, fontFamily: 'var(--font-mono)',
                  fontWeight: 500, cursor: selectedPid ? 'pointer' : 'default',
                  transition: 'all 0.15s', letterSpacing: '0.05em',
                  whiteSpace: 'nowrap',
                }}
              >
                + ADD
              </button>
            </div>

            {/* Items list */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {orderItems.length === 0 ? (
                <div style={{
                  padding: '2rem',
                  textAlign: 'center',
                  color: 'var(--muted)',
                  fontSize: 12,
                  border: '1px dashed var(--border)',
                  borderRadius: 6,
                }}>
                  No products added yet
                </div>
              ) : (
                orderItems.map(item => (
                  <ProductRow
                    key={item.product_id}
                    product={productMap[item.product_id]}
                    item={item}
                    onQtyChange={qty => updateQty(item.product_id, qty)}
                    onRemove={() => removeItem(item.product_id)}
                  />
                ))
              )}
            </div>
          </section>
        </div>

        {/* Right column - Summary */}
        <div>
          <div style={{
            background: 'var(--bg2)',
            border: '1px solid var(--border)',
            borderRadius: 10,
            padding: '1.5rem',
            position: 'sticky',
            top: 0,
          }}>
            <div style={{
              fontSize: 10, letterSpacing: '0.1em',
              color: 'var(--accent)', marginBottom: '1.25rem', fontWeight: 600,
            }}>
              ORDER SUMMARY
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: '1.5rem' }}>
              {orderItems.length === 0 ? (
                <div style={{ fontSize: 12, color: 'var(--muted)' }}>No items yet</div>
              ) : (
                orderItems.map(item => {
                  const p = productMap[item.product_id];
                  return (
                    <div key={item.product_id} style={{
                      display: 'flex', justifyContent: 'space-between',
                      fontSize: 12, color: 'var(--text)',
                    }}>
                      <span style={{ color: 'var(--muted)' }}>
                        {p?.name?.split(' ').slice(0, 2).join(' ')} ×{item.quantity}
                      </span>
                      <span>${(parseFloat(p?.price || 0) * item.quantity).toFixed(2)}</span>
                    </div>
                  );
                })
              )}
            </div>

            {/* Divider */}
            <div style={{ height: 1, background: 'var(--border)', margin: '1rem 0' }} />

            <div style={{
              display: 'flex', justifyContent: 'space-between',
              marginBottom: '1.5rem',
            }}>
              <span style={{ fontSize: 11, color: 'var(--muted)', letterSpacing: '0.08em' }}>TOTAL</span>
              <span style={{
                fontFamily: 'var(--font-head)',
                fontSize: 22, fontWeight: 700,
                color: 'var(--accent)',
              }}>
                ${total.toFixed(2)}
              </span>
            </div>

            {/* Error */}
            {error && (
              <div style={{
                fontSize: 12, color: 'var(--danger)',
                background: 'rgba(248,113,113,0.08)',
                border: '1px solid rgba(248,113,113,0.2)',
                borderRadius: 6, padding: '0.75rem',
                marginBottom: '1rem',
              }}>
                ✕ {error}
              </div>
            )}

            <button
              onClick={handleSubmit}
              disabled={submitting || orderItems.length === 0}
              style={{
                width: '100%',
                background: (submitting || orderItems.length === 0)
                  ? 'var(--bg3)' : 'var(--accent)',
                color: (submitting || orderItems.length === 0)
                  ? 'var(--muted)' : 'var(--bg)',
                border: 'none',
                borderRadius: 6,
                padding: '0.75rem',
                fontSize: 12, fontFamily: 'var(--font-mono)',
                fontWeight: 500, cursor: submitting || orderItems.length === 0
                  ? 'default' : 'pointer',
                letterSpacing: '0.08em',
                transition: 'all 0.15s',
              }}
            >
              {submitting ? 'CREATING...' : 'PLACE ORDER'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
