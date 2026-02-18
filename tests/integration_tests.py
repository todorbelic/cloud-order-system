#!/usr/bin/env python3
"""
Integration Tests - Post-Deployment
"""
import requests
import sys
import os
import time
import json

# Base URLs
CATALOG_URL = os.getenv('CATALOG_URL', 'http://localhost:5001')
ORDER_URL = os.getenv('ORDER_URL', 'http://localhost:5002')

# ANSI boje
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_test_header(test_num, description):
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}🧪 Integration Test {test_num}: {description}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")


def print_success(message):
    print(f"{GREEN}   ✅ {message}{RESET}")


def print_error(message):
    print(f"{RED}   ❌ {message}{RESET}")


def print_info(message):
    print(f"{YELLOW}   ℹ️  {message}{RESET}")


def test_catalog_service_health():
    """
    Integration Test 1: Catalog Service - Get Products
    """
    print_test_header(1, "Catalog Service - Get Products")
    
    try:
        print_info(f"Requesting: GET {CATALOG_URL}/products")
        
        response = requests.get(f"{CATALOG_URL}/products", timeout=10)
        
        if response.status_code != 200:
            print_error(f"Expected HTTP 200, got {response.status_code}")
            return False
        
        print_success(f"HTTP 200 OK")
        
        data = response.json()
        
        if not data.get('success'):
            print_error("'success' field is not True")
            return False
        
        print_success("Response has 'success: true'")
        
        if 'products' not in data:
            print_error("Response missing 'products' field")
            return False
        
        products = data['products']
        
        if len(products) == 0:
            print_error("No products returned")
            return False
        
        print_success(f"Found {len(products)} products in catalog")
        
        first_product = products[0]
        required_fields = ['id', 'code', 'name', 'price', 'stock_quantity']
        
        for field in required_fields:
            if field not in first_product:
                print_error(f"Product missing field: '{field}'")
                return False
        
        print_success(f"Product structure valid")
        print_info(f"Sample: {first_product['name']} - ${first_product['price']}")
        
        print_success("TEST PASSED")
        return True
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_order_service_create_and_check():
    """
    Integration Test 2: Order Service - Create and Verify Order
    """
    print_test_header(2, "Order Service - Create and Verify Order")
    
    try:
        print_info("Step 1: Fetching products")
        
        catalog_response = requests.get(f"{CATALOG_URL}/products", timeout=10)
        
        if catalog_response.status_code != 200:
            print_error("Cannot fetch products")
            return False
        
        products = catalog_response.json()['products']
        
        if len(products) == 0:
            print_error("No products available")
            return False
        
        available_product = None
        for product in products:
            if product.get('stock_quantity', 0) > 0:
                available_product = product
                break
        
        if not available_product:
            print_error("No products with stock")
            return False
        
        print_success(f"Using: {available_product['name']}")
        
        print_info("Step 2: Creating test order")
        
        order_data = {
            "customer_id": "TEST-INT-001",
            "customer_name": "Integration Test",
            "items": [{"product_id": available_product['id'], "quantity": 1}]
        }
        
        response = requests.post(f"{ORDER_URL}/orders", json=order_data, timeout=10)
        
        if response.status_code != 201:
            print_error(f"Expected 201, got {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
        
        print_success("HTTP 201 Created")
        
        data = response.json()
        
        if not data.get('success'):
            print_error(f"Order creation failed: {data.get('error')}")
            return False
        
        order = data['order']
        order_id = order['id']
        order_number = order['order_number']
        
        print_success(f"Order created: {order_number}")
        print_info(f"Total: ${order['total_price']}")
        
        print_info("Step 3: Verifying order in database")
        
        time.sleep(2)
        
        get_response = requests.get(f"{ORDER_URL}/orders/{order_id}", timeout=10)
        
        if get_response.status_code != 200:
            print_error("Order not found")
            return False
        
        retrieved_order = get_response.json()['order']
        
        if retrieved_order['id'] != order_id:
            print_error("Order ID mismatch")
            return False
        
        print_success("Order verified in database")
        
        if len(retrieved_order.get('items', [])) == 0:
            print_error("Order has no items")
            return False
        
        print_success(f"Order has {len(retrieved_order['items'])} item(s)")
        
        print_success("TEST PASSED")
        return True
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def main():
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}🚀 Post-Deployment Integration Tests{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    print(f"Catalog: {CATALOG_URL}")
    print(f"Order:   {ORDER_URL}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    results = []
    results.append(test_catalog_service_health())
    results.append(test_order_service_create_and_check())
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}📊 Results{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {GREEN}{passed}/{total}{RESET}")
    
    if all(results):
        print(f"\n{GREEN}✅ ALL TESTS PASSED{RESET}\n")
        sys.exit(0)
    else:
        print(f"\n{RED}❌ TESTS FAILED{RESET}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
