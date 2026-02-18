"""
Unit Tests for Invoice Worker
pytest invoice-worker/tests/test_worker.py
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pdf_generator import generate_invoice_pdf


SAMPLE_ORDER = {
    'order_id': 1,
    'order_number': 'ORD-20260101-TEST01',
    'customer_id': 'CUST-001',
    'customer_name': 'Marko Markovic',
    'items': [
        {
            'product_code': 'PROD-001',
            'product_name': 'Laptop Dell XPS 15',
            'quantity': 1,
            'unit_price': 1299.99,
            'total_price': 1299.99
        },
        {
            'product_code': 'PROD-002',
            'product_name': 'Wireless Mouse Logitech',
            'quantity': 2,
            'unit_price': 99.99,
            'total_price': 199.98
        }
    ],
    'total_price': 1499.97,
    'created_at': '2026-01-01T10:00:00'
}


def test_pdf_generation_returns_bytes():
    """
    Test 1: generate_invoice_pdf treba da vrati bytes (PDF sadržaj)
    """
    pdf_bytes = generate_invoice_pdf(SAMPLE_ORDER)

    assert pdf_bytes is not None
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0

    # PDF fajlovi počinju sa '%PDF'
    assert pdf_bytes[:4] == b'%PDF', "Output is not a valid PDF"

    print(f"✅ Test 1 passed: PDF generated ({len(pdf_bytes)} bytes)")


def test_pdf_generation_with_multiple_items():
    """
    Test 2: PDF se generiše ispravno za narudžbinu sa više stavki
    """
    order_with_many_items = {
        **SAMPLE_ORDER,
        'order_number': 'ORD-20260101-TEST02',
        'items': [
            {
                'product_code': f'PROD-00{i}',
                'product_name': f'Proizvod {i}',
                'quantity': i,
                'unit_price': 10.00 * i,
                'total_price': 10.00 * i * i
            }
            for i in range(1, 6)  # 5 stavki
        ],
        'total_price': sum(10.00 * i * i for i in range(1, 6))
    }

    pdf_bytes = generate_invoice_pdf(order_with_many_items)

    assert pdf_bytes is not None
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    assert pdf_bytes[:4] == b'%PDF'

    print(f"✅ Test 2 passed: PDF with 5 items generated ({len(pdf_bytes)} bytes)")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
