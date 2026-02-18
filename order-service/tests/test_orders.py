import pytest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


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
    assert data['service'] == 'order-service'
    
    mock_conn.close.assert_called_once()


def test_create_order_validation(client):
    """
    Unit Test 2: Validacija input podataka za kreiranje narudžbine
    Ne šalje request ka bazi - samo testira validaciju
    """
    # Test 1: Bez customer_id
    response = client.post('/orders', 
        json={
            'customer_name': 'Test Customer',
            'items': [{'product_id': 1, 'quantity': 1}]
        },
        content_type='application/json'
    )
    assert response.status_code == 400
    data = response.get_json()
    assert 'customer_id' in data['error'].lower()
    
    # Test 2: Bez customer_name
    response = client.post('/orders',
        json={
            'customer_id': 'CUST-001',
            'items': [{'product_id': 1, 'quantity': 1}]
        },
        content_type='application/json'
    )
    assert response.status_code == 400
    data = response.get_json()
    assert 'customer_name' in data['error'].lower()
    
    # Test 3: Bez items
    response = client.post('/orders',
        json={
            'customer_id': 'CUST-001',
            'customer_name': 'Test Customer'
        },
        content_type='application/json'
    )
    assert response.status_code == 400
    data = response.get_json()
    assert 'items' in data['error'].lower() or 'item' in data['error'].lower()
    
    # Test 4: Prazna lista items
    response = client.post('/orders',
        json={
            'customer_id': 'CUST-001',
            'customer_name': 'Test Customer',
            'items': []
        },
        content_type='application/json'
    )
    assert response.status_code == 400
    data = response.get_json()
    assert 'item' in data['error'].lower()
