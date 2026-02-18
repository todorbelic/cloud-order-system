from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)


def get_db_connection():
    try:
        conn = psycopg2.connect(**Config.get_db_params())
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise


@app.route('/health', methods=['GET'])
def health():
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({
            'status': 'healthy',
            'service': 'catalog-service'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'catalog-service',
            'error': str(e)
        }), 503


@app.route('/products', methods=['GET'])
def get_products():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT id, code, name, image_url, price, stock_quantity, 
                   created_at, updated_at
            FROM products
            ORDER BY id
        """)
        
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        
        logger.info(f"Retrieved {len(products)} products")
        
        return jsonify({
            'success': True,
            'count': len(products),
            'products': products
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT id, code, name, image_url, price, stock_quantity,
                   created_at, updated_at
            FROM products
            WHERE id = %s
        """, (product_id,))
        
        product = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not product:
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
        
        logger.info(f"Retrieved product ID {product_id}")
        
        return jsonify({
            'success': True,
            'product': product
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/products/code/<string:product_code>', methods=['GET'])
def get_product_by_code(product_code):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT id, code, name, image_url, price, stock_quantity,
                   created_at, updated_at
            FROM products
            WHERE code = %s
        """, (product_code,))
        
        product = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not product:
            return jsonify({
                'success': False,
                'error': f'Product with code {product_code} not found'
            }), 404
        
        logger.info(f"Retrieved product with code {product_code}")
        
        return jsonify({
            'success': True,
            'product': product
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching product by code {product_code}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/products/check-stock', methods=['POST'])
def check_stock():
    try:
        items = request.json
        
        if not items or not isinstance(items, list):
            return jsonify({
                'success': False,
                'error': 'Invalid request body. Expected array of items.'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        results = []
        all_available = True
        
        for item in items:
            product_id = item.get('product_id')
            requested_quantity = item.get('quantity', 0)
            
            cursor.execute("""
                SELECT id, code, name, price, stock_quantity
                FROM products
                WHERE id = %s
            """, (product_id,))
            
            product = cursor.fetchone()
            
            if not product:
                results.append({
                    'product_id': product_id,
                    'available': False,
                    'reason': 'Product not found'
                })
                all_available = False
            elif product['stock_quantity'] < requested_quantity:
                results.append({
                    'product_id': product_id,
                    'product_code': product['code'],
                    'product_name': product['name'],
                    'requested_quantity': requested_quantity,
                    'available_quantity': product['stock_quantity'],
                    'available': False,
                    'reason': f'Insufficient stock. Available: {product["stock_quantity"]}, Requested: {requested_quantity}'
                })
                all_available = False
            else:
                results.append({
                    'product_id': product_id,
                    'product_code': product['code'],
                    'product_name': product['name'],
                    'price': float(product['price']),
                    'requested_quantity': requested_quantity,
                    'available_quantity': product['stock_quantity'],
                    'available': True
                })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'all_available': all_available,
            'items': results
        }), 200
        
    except Exception as e:
        logger.error(f"Error checking stock: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/products/reserve', methods=['POST'])
def reserve_stock():
    try:
        items = request.json
        
        if not items or not isinstance(items, list):
            return jsonify({
                'success': False,
                'error': 'Invalid request body. Expected array of items.'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            for item in items:
                product_id = item.get('product_id')
                quantity = item.get('quantity', 0)
                
                cursor.execute("""
                    SELECT stock_quantity FROM products WHERE id = %s FOR UPDATE
                """, (product_id,))
                
                product = cursor.fetchone()
                
                if not product:
                    conn.rollback()
                    return jsonify({
                        'success': False,
                        'error': f'Product {product_id} not found'
                    }), 404
                
                if product['stock_quantity'] < quantity:
                    conn.rollback()
                    return jsonify({
                        'success': False,
                        'error': f'Insufficient stock for product {product_id}'
                    }), 400
            
            updated_products = []
            for item in items:
                product_id = item.get('product_id')
                quantity = item.get('quantity', 0)
                
                cursor.execute("""
                    UPDATE products
                    SET stock_quantity = stock_quantity - %s
                    WHERE id = %s
                    RETURNING id, code, name, stock_quantity
                """, (quantity, product_id))
                
                updated_product = cursor.fetchone()
                updated_products.append({
                    'product_id': updated_product['id'],
                    'product_code': updated_product['code'],
                    'product_name': updated_product['name'],
                    'reserved_quantity': quantity,
                    'remaining_stock': updated_product['stock_quantity']
                })
            
            conn.commit()
            logger.info(f"Reserved stock for {len(updated_products)} products")
            
            return jsonify({
                'success': True,
                'message': 'Stock reserved successfully',
                'products': updated_products
            }), 200
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
        
    except Exception as e:
        logger.error(f"Error reserving stock: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/products/release', methods=['POST'])
def release_stock():
    try:
        items = request.json
        
        if not items or not isinstance(items, list):
            return jsonify({
                'success': False,
                'error': 'Invalid request body. Expected array of items.'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            released_products = []
            for item in items:
                product_id = item.get('product_id')
                quantity = item.get('quantity', 0)
                
                cursor.execute("""
                    UPDATE products
                    SET stock_quantity = stock_quantity + %s
                    WHERE id = %s
                    RETURNING id, code, name, stock_quantity
                """, (quantity, product_id))
                
                updated_product = cursor.fetchone()
                
                if updated_product:
                    released_products.append({
                        'product_id': updated_product['id'],
                        'product_code': updated_product['code'],
                        'product_name': updated_product['name'],
                        'released_quantity': quantity,
                        'new_stock': updated_product['stock_quantity']
                    })
            
            conn.commit()
            logger.info(f"Released stock for {len(released_products)} products")
            
            return jsonify({
                'success': True,
                'message': 'Stock released successfully',
                'products': released_products
            }), 200
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
        
    except Exception as e:
        logger.error(f"Error releasing stock: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    logger.info(f"Starting Catalog Service on {Config.SERVICE_HOST}:{Config.SERVICE_PORT}")
    app.run(
        host=Config.SERVICE_HOST,
        port=Config.SERVICE_PORT,
        debug=Config.DEBUG
    )
