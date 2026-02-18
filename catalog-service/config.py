import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration"""
    
    # Database Configuration
    DB_HOST = os.getenv('CATALOG_DB_HOST', 'localhost')
    DB_PORT = os.getenv('CATALOG_DB_PORT', '5432')
    DB_NAME = os.getenv('CATALOG_DB_NAME', 'catalogdb')
    DB_USER = os.getenv('CATALOG_DB_USER', 'cataloguser')
    DB_PASSWORD = os.getenv('CATALOG_DB_PASSWORD', 'catalogpass123')
    
    # Service Configuration
    SERVICE_HOST = os.getenv('CATALOG_SERVICE_HOST', '0.0.0.0')
    SERVICE_PORT = int(os.getenv('CATALOG_SERVICE_PORT', '5001'))
    
    # Flask Configuration
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    @staticmethod
    def get_db_connection_string():
        return f"host={Config.DB_HOST} port={Config.DB_PORT} dbname={Config.DB_NAME} user={Config.DB_USER} password={Config.DB_PASSWORD}"
    
    @staticmethod
    def get_db_params():
        return {
            'host': Config.DB_HOST,
            'port': Config.DB_PORT,
            'dbname': Config.DB_NAME,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD
        }
