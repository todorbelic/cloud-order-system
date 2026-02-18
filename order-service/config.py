"""
Order Service Configuration
Čita environment varijable i definiše konfiguraciju
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""

    # Order Database
    DB_HOST = os.getenv('ORDER_DB_HOST', 'localhost')
    DB_PORT = os.getenv('ORDER_DB_PORT', '5433')
    DB_NAME = os.getenv('ORDER_DB_NAME', 'orderdb')
    DB_USER = os.getenv('ORDER_DB_USER', 'orderuser')
    DB_PASSWORD = os.getenv('ORDER_DB_PASSWORD', 'orderpass123')

    CATALOG_SERVICE_URL = os.getenv('CATALOG_SERVICE_URL', 'http://localhost:5001')

    # Azure Storage Queue
    AZURE_STORAGE_CONNECTION_STRING = os.getenv(
        'AZURE_STORAGE_CONNECTION_STRING',
        'DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;'
        'AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;'
        'BlobEndpoint=http://localhost:10000/devstoreaccount1;'
        'QueueEndpoint=http://localhost:10001/devstoreaccount1;'
    )
    AZURE_QUEUE_NAME = os.getenv('AZURE_QUEUE_NAME', 'invoice-queue')

    # Flask
    SERVICE_HOST = os.getenv('ORDER_SERVICE_HOST', '0.0.0.0')
    SERVICE_PORT = int(os.getenv('ORDER_SERVICE_PORT', '5002'))
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    @staticmethod
    def get_db_params():
        return {
            'host': Config.DB_HOST,
            'port': Config.DB_PORT,
            'dbname': Config.DB_NAME,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD
        }
