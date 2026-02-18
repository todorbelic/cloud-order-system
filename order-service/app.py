from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import uuid
from datetime import datetime
from config import Config
from catalog_client import CatalogClient
from queue_client import QueueMessageClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

catalog_client = CatalogClient()
queue_client = QueueMessageClient()


def get_db_connection():
    try:
        conn = psycopg2.connect(**Config.get_db_params())
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise


def generate_order_number():
    date_part = datetime.utcnow().strftime('%Y%m%d')
    unique_part = str(uuid.uuid4())[:8].upper()
    return f"ORD-{date_part}-{unique_part}"


@app.route('/health', methods=['GET'])
def health():
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({
            'status': 'healthy',
            'service': 'order-service'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'order-service',
            'error': str(e)
        }), 503

@app.route('/orders', methods=['GET'])
def get_orders():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT id, order_number, customer_id, customer_name,
                   status, total_price, pdf_url, created_at, updated_at
            FROM orders
            ORDER BY created_at DESC
        """)
        orders = cursor.fetchall()

        # Za svaku narudžbinu dohvati stavke
        result = []
        for order in orders:
            cursor.execute("""
                SELECT id, product_id, product_code, product_name,
                       quantity, unit_price, total_price
                FROM order_items
                WHERE order_id = %s
            """, (order['id'],))
            items = cursor.fetchall()

            order_dict = dict(order)
            order_dict['items'] = [dict(item) for item in items]
            result.append(order_dict)

        cursor.close()
        conn.close()

        logger.info(f"Retrieved {len(result)} orders")
        return jsonify({
            'success': True,
            'count': len(result),
            'orders': result
        }), 200

    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT id, order_number, customer_id, customer_name,
                   status, total_price, pdf_url, created_at, updated_at
            FROM orders
            WHERE id = %s
        """, (order_id,))
        order = cursor.fetchone()

        if not order:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Order not found'}), 404

        cursor.execute("""
            SELECT id, product_id, product_code, product_name,
                   quantity, unit_price, total_price
            FROM order_items
            WHERE order_id = %s
        """, (order_id,))
        items = cursor.fetchall()

        cursor.close()
        conn.close()

        order_dict = dict(order)
        order_dict['items'] = [dict(item) for item in items]

        return jsonify({'success': True, 'order': order_dict}), 200

    except Exception as e:
        logger.error(f"Error fetching order {order_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/orders', methods=['POST'])
def create_order():
    try:
        data = request.json

        if not data:
            return jsonify({'success': False, 'error': 'Request body is required'}), 400

        customer_id = data.get('customer_id', '').strip()
        customer_name = data.get('customer_name', '').strip()
        items = data.get('items', [])

        if not customer_id:
            return jsonify({'success': False, 'error': 'customer_id is required'}), 400
        if not customer_name:
            return jsonify({'success': False, 'error': 'customer_name is required'}), 400
        if not items or len(items) == 0:
            return jsonify({'success': False, 'error': 'At least one item is required'}), 400

        for item in items:
            if not item.get('product_id'):
                return jsonify({'success': False, 'error': 'product_id is required for each item'}), 400
            if not item.get('quantity') or int(item['quantity']) < 1:
                return jsonify({'success': False, 'error': 'quantity must be at least 1'}), 400

        logger.info(f"Checking stock for order from {customer_name}...")
        stock_check = catalog_client.check_stock([
            {'product_id': item['product_id'], 'quantity': item['quantity']}
            for item in items
        ])

        if not stock_check.get('all_available'):
            unavailable = [
                i for i in stock_check.get('items', [])
                if not i.get('available')
            ]
            return jsonify({
                'success': False,
                'error': 'Insufficient stock for one or more products',
                'unavailable_items': unavailable
            }), 400

        product_info = {
            i['product_id']: i
            for i in stock_check.get('items', [])
        }

        logger.info("Reserving stock in Catalog Service...")
        catalog_client.reserve_stock([
            {'product_id': item['product_id'], 'quantity': item['quantity']}
            for item in items
        ])

        reserved_items = []
        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            order_number = generate_order_number()

            total_price = sum(
                product_info[item['product_id']]['price'] * item['quantity']
                for item in items
            )

            cursor.execute("""
                INSERT INTO orders (order_number, customer_id, customer_name,
                                    status, total_price)
                VALUES (%s, %s, %s, 'pending', %s)
                RETURNING id, order_number, status, total_price, created_at
            """, (order_number, customer_id, customer_name, total_price))

            new_order = cursor.fetchone()
            order_id = new_order['id']

            for item in items:
                info = product_info[item['product_id']]
                unit_price = info['price']
                quantity = item['quantity']
                item_total = unit_price * quantity

                cursor.execute("""
                    INSERT INTO order_items (order_id, product_id, product_code,
                                            product_name, quantity, unit_price, total_price)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, product_id, product_code, product_name,
                              quantity, unit_price, total_price
                """, (
                    order_id,
                    item['product_id'],
                    info['product_code'],
                    info['product_name'],
                    quantity,
                    unit_price,
                    item_total
                ))
                reserved_items.append({
                    'product_id': item['product_id'],
                    'quantity': quantity
                })

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"Order {order_number} created in database")

        except Exception as db_error:
            logger.error(f"Database error, releasing stock: {db_error}")
            try:
                catalog_client.release_stock(reserved_items)
            except Exception as release_error:
                logger.error(f"Failed to release stock: {release_error}")
            raise db_error

        try:
            queue_items = [
                {
                    'product_id': item['product_id'],
                    'product_code': product_info[item['product_id']]['product_code'],
                    'product_name': product_info[item['product_id']]['product_name'],
                    'quantity': item['quantity'],
                    'unit_price': product_info[item['product_id']]['price'],
                    'total_price': product_info[item['product_id']]['price'] * item['quantity']
                }
                for item in items
            ]

            queue_client.send_invoice_message(
                order_id=order_id,
                order_number=order_number,
                customer_id=customer_id,
                customer_name=customer_name,
                items=queue_items,
                total_price=float(total_price)
            )
            logger.info(f"Invoice message sent to queue for order {order_number}")

        except Exception as queue_error:
            logger.error(f"Failed to send queue message (order still created): {queue_error}")

        return jsonify({
            'success': True,
            'message': 'Order created successfully',
            'order': {
                'id': order_id,
                'order_number': order_number,
                'customer_id': customer_id,
                'customer_name': customer_name,
                'status': 'pending',
                'total_price': float(total_price),
                'items': [
                    {
                        'product_id': item['product_id'],
                        'product_code': product_info[item['product_id']]['product_code'],
                        'product_name': product_info[item['product_id']]['product_name'],
                        'quantity': item['quantity'],
                        'unit_price': product_info[item['product_id']]['price'],
                        'total_price': product_info[item['product_id']]['price'] * item['quantity']
                    }
                    for item in items
                ]
            }
        }), 201

    except Exception as e:
        logger.error(f"Error creating order: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/orders/<int:order_id>/status', methods=['PATCH'])
def update_order_status(order_id):
    try:
        data = request.json
        new_status = data.get('status')
        pdf_url = data.get('pdf_url')

        valid_statuses = ['pending', 'processing', 'completed']
        if new_status not in valid_statuses:
            return jsonify({
                'success': False,
                'error': f'Invalid status. Must be one of: {valid_statuses}'
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            UPDATE orders
            SET status = %s, pdf_url = COALESCE(%s, pdf_url)
            WHERE id = %s
            RETURNING id, order_number, status, pdf_url, updated_at
        """, (new_status, pdf_url, order_id))

        updated_order = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        if not updated_order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404

        logger.info(f"Order {order_id} status updated to {new_status}")
        return jsonify({
            'success': True,
            'order': dict(updated_order)
        }), 200

    except Exception as e:
        logger.error(f"Error updating order status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    logger.info(f"Starting Order Service on {Config.SERVICE_HOST}:{Config.SERVICE_PORT}")
    app.run(
        host=Config.SERVICE_HOST,
        port=Config.SERVICE_PORT,
        debug=Config.DEBUG
    )


@app.route('/orders/<int:order_id>/invoice', methods=['POST'])
def update_invoice(order_id):
    try:
        data = request.json
        
        if not data or not data.get('pdf_url'):
            return jsonify({
                'success': False,
                'error': 'pdf_url is required'
            }), 400
        
        pdf_url = data.get('pdf_url')
        new_status = data.get('status', 'completed')
        
        valid_statuses = ['pending', 'processing', 'completed']
        if new_status not in valid_statuses:
            return jsonify({
                'success': False,
                'error': f'Invalid status. Must be one of: {valid_statuses}'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            UPDATE orders
            SET status = %s, pdf_url = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id, order_number, status, pdf_url, updated_at
        """, (new_status, pdf_url, order_id))
        
        updated_order = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        if not updated_order:
            return jsonify({
                'success': False,
                'error': 'Order not found'
            }), 404
        
        logger.info(f"Invoice updated for order {order_id}: {pdf_url}")
        
        return jsonify({
            'success': True,
            'message': 'Invoice updated successfully',
            'order': dict(updated_order)
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating invoice for order {order_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
