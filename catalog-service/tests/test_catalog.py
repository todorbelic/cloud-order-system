"""
Unit Tests for Catalog Service
Koristi mock-ove, ne pristupa pravoj bazi
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


@pytest.fixture
def client():
    """Test klijent za Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@patch('app.get_db_connection')
def test_health_endpoint(mock_db, client):
    """
    Unit Test 1: Health endpoint vraća status OK
    Mock-ujemo DB konekciju
    """
    # Mock connection
    mock_conn = MagicMock()
    mock_conn.close = MagicMock()
    mock_db.return_value = mock_conn
    
    # Request
    response = client.get('/health')
    
    # Assertions
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'catalog-service'
    
    # Proveri da je close() pozvan
    mock_conn.close.assert_called_once()


@patch('app.get_db_connection')
def test_get_products(mock_db, client):
    """
    Unit Test 2: GET /products vraća listu proizvoda
    Mock-ujemo DB da vrati test podatke
    """
    # Mock connection i cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    
    # Mock proizvodi (RealDictCursor vraća dict)
    mock_products = [
        {
            'id': 1,
            'code': 'PROD-001',
            'name': 'Test Product 1',
            'image_url': 'http://test.com/1.jpg',
            'price': 99.99,
            'stock_quantity': 10,
            'created_at': '2024-01-01',
            'updated_at': '2024-01-01'
        },
        {
            'id': 2,
            'code': 'PROD-002',
            'name': 'Test Product 2',
            'image_url': 'http://test.com/2.jpg',
            'price': 149.99,
            'stock_quantity': 5,
            'created_at': '2024-01-01',
            'updated_at': '2024-01-01'
        }
    ]
    
    # Setup mock chain
    mock_cursor.fetchall.return_value = mock_products
    mock_cursor.close = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.close = MagicMock()
    mock_db.return_value = mock_conn
    
    # Request
    response = client.get('/products')
    
    # Assertions
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['count'] == 2
    assert len(data['products']) == 2
    assert data['products'][0]['name'] == 'Test Product 1'
    assert data['products'][1]['name'] == 'Test Product 2'
    
    # Proveri da su close() metode pozvane
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()
