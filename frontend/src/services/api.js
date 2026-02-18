const CATALOG_API = process.env.REACT_APP_CATALOG_API_URL || '/api/catalog';
const ORDER_API   = process.env.REACT_APP_ORDER_API_URL   || '/api/orders';

async function handleResponse(res) {
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Request failed');
  return data;
}

// ── Catalog Service ──────────────────────────────
export const catalogApi = {
  getProducts: () =>
    fetch(`${CATALOG_API}/products`).then(handleResponse),

  getProduct: (id) =>
    fetch(`${CATALOG_API}/products/${id}`).then(handleResponse),
};

// ── Order Service ────────────────────────────────
export const orderApi = {
  getOrders: () =>
    fetch(`${ORDER_API}/orders`).then(handleResponse),

  getOrder: (id) =>
    fetch(`${ORDER_API}/orders/${id}`).then(handleResponse),

  createOrder: (orderData) =>
    fetch(`${ORDER_API}/orders`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(orderData),
    }).then(handleResponse),
};
