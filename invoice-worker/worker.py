import json
import time
import logging
import requests
from datetime import datetime, timezone, timedelta
from azure.storage.queue import QueueClient
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from config import Config
from pdf_generator import generate_invoice_pdf

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_connection_string(conn_str):
    parts = {}
    for segment in conn_str.split(';'):
        if '=' in segment:
            key, value = segment.split('=', 1)
            parts[key.strip()] = value.strip()
    return parts


def upload_pdf_to_blob(pdf_bytes, order_number):
    blob_name = f"{order_number}.pdf"

    blob_service = BlobServiceClient.from_connection_string(
        Config.AZURE_STORAGE_CONNECTION_STRING
    )

    container_client = blob_service.get_container_client(Config.AZURE_BLOB_CONTAINER)
    try:
        container_client.create_container()
        logger.info(f"Container '{Config.AZURE_BLOB_CONTAINER}' created")
    except Exception:
        pass

    blob_client = blob_service.get_blob_client(
        container=Config.AZURE_BLOB_CONTAINER,
        blob=blob_name
    )
    blob_client.upload_blob(pdf_bytes, overwrite=True)
    logger.info(f"PDF uploaded: {blob_client.url}")

    conn_parts = parse_connection_string(Config.AZURE_STORAGE_CONNECTION_STRING)
    account_name = conn_parts.get('AccountName', 'devstoreaccount1')
    account_key  = conn_parts.get('AccountKey', '')

    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=Config.AZURE_BLOB_CONTAINER,
        blob_name=blob_name,
        account_key=account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.now(timezone.utc) + timedelta(days=365),
    )

    pdf_url = f"{blob_client.url}?{sas_token}"
    logger.info(f"SAS URL generated successfully")
    return pdf_url


def update_order_invoice(order_id, pdf_url):

    try:
        response = requests.post(
            f"{Config.ORDER_SERVICE_URL}/orders/{order_id}/invoice",
            json={
                'pdf_url': pdf_url,
                'status': 'completed'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"Order {order_id} invoice updated successfully via API")
            return True
        else:
            logger.error(f"Failed to update order {order_id}: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error calling Order Service API: {e}")
        raise


def process_message(message_data):
    order_id     = message_data['order_id']
    order_number = message_data['order_number']

    logger.info(f"Processing order {order_number} (ID: {order_id})")

    logger.info(f"Generating PDF for order {order_number}...")
    pdf_bytes = generate_invoice_pdf(message_data)

    logger.info(f"Uploading PDF to blob storage...")
    pdf_url = upload_pdf_to_blob(pdf_bytes, order_number)

    logger.info(f"Updating order invoice via API...")
    update_order_invoice(order_id, pdf_url)

    logger.info(f"✅ Order {order_number} processed successfully.")
    return pdf_url


def ensure_queue_exists(queue_client):
    try:
        queue_client.create_queue()
        logger.info(f"Queue '{Config.AZURE_QUEUE_NAME}' created")
    except Exception:
        pass


def run_worker():
    logger.info("=" * 50)
    logger.info("Invoice Worker started")
    logger.info(f"Queue:          {Config.AZURE_QUEUE_NAME}")
    logger.info(f"Blob container: {Config.AZURE_BLOB_CONTAINER}")
    logger.info(f"Order Service:  {Config.ORDER_SERVICE_URL}")
    logger.info(f"Poll interval:  {Config.POLL_INTERVAL_SECONDS}s")
    logger.info("=" * 50)

    queue_client = QueueClient.from_connection_string(
        Config.AZURE_STORAGE_CONNECTION_STRING,
        Config.AZURE_QUEUE_NAME
    )
    ensure_queue_exists(queue_client)

    while True:
        try:
            messages = queue_client.receive_messages(
                messages_per_page=1,
                visibility_timeout=30
            )

            processed = False
            for message in messages:
                try:
                    message_data = json.loads(message.content)
                    logger.info(f"📨 Received message for order: {message_data.get('order_number')}")

                    process_message(message_data)

                    queue_client.delete_message(message)
                    logger.info(f"🗑️  Message deleted from queue")
                    processed = True

                except Exception as e:
                    logger.error(f"Failed to process message: {e}")

            if not processed:
                logger.debug(f"No messages, waiting {Config.POLL_INTERVAL_SECONDS}s...")

        except KeyboardInterrupt:
            logger.info("Worker stopped by user")
            break
        except Exception as e:
            logger.error(f"Worker error: {e}")

        time.sleep(Config.POLL_INTERVAL_SECONDS)


if __name__ == '__main__':
    run_worker()
