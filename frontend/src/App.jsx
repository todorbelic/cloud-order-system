import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, NavLink, useLocation } from 'react-router-dom';
import Products from './pages/Products';
import CreateOrder from './pages/CreateOrder';
import Orders from './pages/Orders';

// ── Global Styles ─────────────────────────────────────────
const globalStyles = `
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:        #0a0a0f;
    --bg2:       #111118;
    --bg3:       #1a1a26;
    --border:    #2a2a3a;
    --accent:    #6ee7b7;
    --accent2:   #818cf8;
    --text:      #e2e8f0;
    --muted:     #64748b;
    --danger:    #f87171;
    --warning:   #fbbf24;
    --font-head: 'Syne', sans-serif;
    --font-mono: 'DM Mono', monospace;
  }

  html, body, #root {
    height: 100%;
    background: var(--bg);
    color: var(--text);
    font-family: var(--font-mono);
    font-size: 14px;
  }

  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
  }
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  .fade-up { animation: fadeUp 0.4s ease both; }
`;

// ── Layout ────────────────────────────────────────────────
function Layout({ children }) {
  const location = useLocation();

  const navItems = [
    { to: '/',             label: 'PRODUCTS',      icon: '◈' },
    { to: '/create-order', label: 'NEW ORDER',     icon: '◎' },
    { to: '/orders',       label: 'ORDERS',        icon: '◉' },
  ];

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      {/* Sidebar */}
      <aside style={{
        width: 220,
        minWidth: 220,
        background: 'var(--bg2)',
        borderRight: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        padding: '2rem 0',
      }}>
        {/* Logo */}
        <div style={{ padding: '0 1.5rem 2rem' }}>
          <div style={{
            fontFamily: 'var(--font-head)',
            fontSize: 18,
            fontWeight: 800,
            color: 'var(--accent)',
            letterSpacing: '-0.02em',
            lineHeight: 1.1,
          }}>
            CLOUD<br />
            <span style={{ color: 'var(--accent2)' }}>ORDER</span>
          </div>
          <div style={{ fontSize: 10, color: 'var(--muted)', marginTop: 4 }}>
            SYSTEM v1.0
          </div>
        </div>

        {/* Divider */}
        <div style={{ height: 1, background: 'var(--border)', marginBottom: '1.5rem' }} />

        {/* Nav */}
        <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 4, padding: '0 0.75rem' }}>
          {navItems.map(({ to, label, icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                padding: '0.625rem 0.75rem',
                borderRadius: 6,
                textDecoration: 'none',
                fontSize: 11,
                fontWeight: 500,
                letterSpacing: '0.08em',
                transition: 'all 0.15s',
                background: isActive ? 'rgba(110,231,183,0.08)' : 'transparent',
                color: isActive ? 'var(--accent)' : 'var(--muted)',
                borderLeft: isActive ? '2px solid var(--accent)' : '2px solid transparent',
              })}
            >
              <span style={{ fontSize: 16 }}>{icon}</span>
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div style={{ padding: '1.5rem', borderTop: '1px solid var(--border)' }}>
          <div style={{ fontSize: 10, color: 'var(--muted)', lineHeight: 1.6 }}>
            <div style={{ color: 'var(--accent)', marginBottom: 2 }}>● MICROSERVICES</div>
            <div>Catalog :5001</div>
            <div>Orders  :5002</div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main style={{
        flex: 1,
        overflow: 'auto',
        background: 'var(--bg)',
        padding: '2rem 2.5rem',
      }}>
        {children}
      </main>
    </div>
  );
}

// ── App ───────────────────────────────────────────────────
export default function App() {
  return (
    <>
      <style>{globalStyles}</style>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/"             element={<Products />} />
            <Route path="/create-order" element={<CreateOrder />} />
            <Route path="/orders"       element={<Orders />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </>
  );
}
