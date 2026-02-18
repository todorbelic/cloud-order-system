"""
Unit Tests for Catalog Service
pytest catalog-service/tests/test_catalog.py
"""
import pytest
import sys
import os

# Add parent directory to path
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
    Test 1: Health endpoint treba da vrati status 200 i 'healthy' status
    """
    response = client.get('/health')
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data is not None
    assert 'status' in data
    assert data['status'] == 'healthy'
    assert data['service'] == 'catalog-service'
    
    print("✅ Test 1 passed: Health endpoint is working")


def test_get_products(client):
    """
    Test 2: GET /products treba da vrati listu proizvoda
    """
    response = client.get('/products')
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data is not None
    assert 'success' in data
    assert data['success'] is True
    assert 'products' in data
    assert 'count' in data
    assert isinstance(data['products'], list)
    assert data['count'] > 0  # Trebalo bi da ima bar nekoliko proizvoda iz init.sql
    
    # Provera strukture prvog proizvoda
    if len(data['products']) > 0:
        product = data['products'][0]
        assert 'id' in product
        assert 'code' in product
        assert 'name' in product
        assert 'price' in product
        assert 'stock_quantity' in product
    
    print(f"✅ Test 2 passed: Retrieved {data['count']} products")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
