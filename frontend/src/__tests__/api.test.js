/**
 * Unit Tests for Frontend
 * Jest + React Testing Library
 */

import { render, screen } from '@testing-library/react';
import { catalogApi, orderApi } from '../services/api';

// Mock fetch
global.fetch = jest.fn();

describe('API Service Tests', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('catalogApi.getProducts should fetch products', async () => {
    const mockProducts = {
      success: true,
      count: 2,
      products: [
        { id: 1, name: 'Test Product 1' },
        { id: 2, name: 'Test Product 2' }
      ]
    };

    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockProducts,
    });

    const result = await catalogApi.getProducts();
    
    expect(result.success).toBe(true);
    expect(result.count).toBe(2);
    expect(result.products).toHaveLength(2);
  });

  test('orderApi.createOrder should post order data', async () => {
    const mockOrder = {
      success: true,
      order: {
        id: 1,
        order_number: 'ORD-TEST-001',
        total_price: 100.00
      }
    };

    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockOrder,
    });

    const orderData = {
      customer_id: 'CUST-001',
      customer_name: 'Test Customer',
      items: [{ product_id: 1, quantity: 1 }]
    };

    const result = await orderApi.createOrder(orderData);
    
    expect(result.success).toBe(true);
    expect(result.order.order_number).toBe('ORD-TEST-001');
  });
});
