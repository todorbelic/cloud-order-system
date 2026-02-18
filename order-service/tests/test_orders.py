import pytest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """
    Test 1: Health endpoint treba da vrati 200 i 'healthy' status
    """
    response = client.get('/health')

    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'order-service'

    print("✅ Test 1 passed: Health endpoint is working")


def test_create_order_missing_fields(client):
    """
    Test 2: Kreiranje narudžbine bez obaveznih polja treba da vrati 400
    """
    # Slučaj 1: Prazan body
    response = client.post('/orders',
                            json={},
                            content_type='application/json')
    assert response.status_code == 400

    # Slučaj 2: Nedostaje customer_id
    response = client.post('/orders',
                            json={
                                'customer_name': 'Marko Markovic',
                                'items': [{'product_id': 1, 'quantity': 1}]
                            },
                            content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'customer_id' in data['error']

    # Slučaj 3: Prazna lista proizvoda
    response = client.post('/orders',
                            json={
                                'customer_id': 'CUST-001',
                                'customer_name': 'Marko Markovic',
                                'items': []
                            },
                            content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False

    print("✅ Test 2 passed: Validation correctly rejects invalid orders")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
