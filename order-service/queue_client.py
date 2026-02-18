import json
import logging
from datetime import datetime
from azure.storage.queue import QueueClient, QueueServiceClient
from config import Config

logger = logging.getLogger(__name__)


class QueueMessageClient:

    def __init__(self):
        self.connection_string = Config.AZURE_STORAGE_CONNECTION_STRING
        self.queue_name = Config.AZURE_QUEUE_NAME
        self._ensure_queue_exists()

    def _ensure_queue_exists(self):
        try:
            service_client = QueueServiceClient.from_connection_string(
                self.connection_string
            )
            queue_client = service_client.get_queue_client(self.queue_name)
            queue_client.create_queue()
            logger.info(f"Queue '{self.queue_name}' is ready")
        except Exception as e:
            if "QueueAlreadyExists" not in str(e):
                logger.warning(f"Could not ensure queue exists: {e}")

    def send_invoice_message(self, order_id, order_number, customer_id,
                              customer_name, items, total_price):

        try:
            message = {
                'order_id': order_id,
                'order_number': order_number,
                'customer_id': customer_id,
                'customer_name': customer_name,
                'items': items,
                'total_price': total_price,
                'created_at': datetime.utcnow().isoformat()
            }

            queue_client = QueueClient.from_connection_string(
                self.connection_string,
                self.queue_name
            )

            message_json = json.dumps(message)
            queue_client.send_message(message_json)

            logger.info(f"Invoice message sent for order {order_number}")
            return True

        except Exception as e:
            logger.error(f"Failed to send invoice message for order {order_number}: {e}")
            raise
