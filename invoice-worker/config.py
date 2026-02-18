"""
Invoice Worker Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    ORDER_SERVICE_URL = os.getenv('ORDER_SERVICE_URL', 'http://order-service:5002')

    AZURE_STORAGE_CONNECTION_STRING = os.getenv(
        'AZURE_STORAGE_CONNECTION_STRING',
        'DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;'
        'AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;'
        'BlobEndpoint=http://localhost:10000/devstoreaccount1;'
        'QueueEndpoint=http://localhost:10001/devstoreaccount1;'
    )
    AZURE_QUEUE_NAME = os.getenv('AZURE_QUEUE_NAME', 'invoice-queue')
    AZURE_BLOB_CONTAINER = os.getenv('AZURE_BLOB_CONTAINER_INVOICES', 'invoices')

    POLL_INTERVAL_SECONDS = int(os.getenv('POLL_INTERVAL_SECONDS', '5'))
