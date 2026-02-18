import requests
import logging
from config import Config

logger = logging.getLogger(__name__)


class CatalogClient:

    def __init__(self):
        self.base_url = Config.CATALOG_SERVICE_URL

    def get_product(self, product_id):
        try:
            response = requests.get(
                f"{self.base_url}/products/{product_id}",
                timeout=5
            )
            if response.status_code == 200:
                return response.json().get('product')
            elif response.status_code == 404:
                return None
            else:
                logger.error(f"Catalog Service returned {response.status_code} for product {product_id}")
                return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to Catalog Service at {self.base_url}")
            raise Exception("Catalog Service is unavailable")
        except Exception as e:
            logger.error(f"Error calling Catalog Service: {e}")
            raise

    def check_stock(self, items):
        try:
            response = requests.post(
                f"{self.base_url}/products/check-stock",
                json=items,
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Stock check failed: {response.text}")
                raise Exception(f"Stock check failed: {response.text}")
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to Catalog Service at {self.base_url}")
            raise Exception("Catalog Service is unavailable")

    def reserve_stock(self, items):
        try:
            response = requests.post(
                f"{self.base_url}/products/reserve",
                json=items,
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Stock reservation failed: {response.text}")
                raise Exception(f"Stock reservation failed: {response.text}")
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to Catalog Service at {self.base_url}")
            raise Exception("Catalog Service is unavailable")

    def release_stock(self, items):
        try:
            response = requests.post(
                f"{self.base_url}/products/release",
                json=items,
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Stock release failed: {response.text}")
                raise Exception(f"Stock release failed: {response.text}")
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to Catalog Service at {self.base_url}")
            raise Exception("Catalog Service is unavailable")
