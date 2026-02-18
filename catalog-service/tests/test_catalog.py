"""
Unit Tests for Catalog Service
pytest catalog-service/tests/test_catalog.py
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Dodaj parent direktorijum u path
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
    # Mock database connection i cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {'version': 'PostgreSQL 15.0'}
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn
    
    # Request
    response = client.get('/health')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'database' in data


@patch('app.get_db_connection')
def test_get_products(mock_db, client):
    """
    Unit Test 2: GET /products vraća listu proizvoda
    Mock-ujemo DB da vrati test podatke
    """
    # Mock database response
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    
    # Mock proizvodi
    mock_products = [
        {
            'id': 1,
            'code': 'PROD-001',
            'name': 'Test Product 1',
            'price': 99.99,
            'stock_quantity': 10
        },
        {
            'id': 2,
            'code': 'PROD-002',
            'name': 'Test Product 2',
            'price': 149.99,
            'stock_quantity': 5
        }
    ]
    
    mock_cursor.fetchall.return_value = mock_products
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_db.return_value = mock_conn
    
    # Request
    response = client.get('/products')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert len(data['products']) == 2
    assert data['products'][0]['name'] == 'Test Product 1'

