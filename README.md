# Cloud Order System

## Opis projekta

Cloud-native aplikacija za kreiranje narudžbina i asinhrono generisanje PDF faktura. Sistem je implementiran kao mikroservisna arhitektura deployovana na Azure Kubernetes Service (AKS) i Azure Container Apps.

## Arhitektura

### Servisi
- **Catalog Service** (Python/Flask) - Upravljanje proizvodima i zalihama
- **Order Service** (Python/Flask) - Kreiranje i praćenje narudžbina
- **Invoice Worker** (Python) - Asinhrono generisanje PDF faktura
- **Frontend** (React) - Korisnički interfejs
- **PostgreSQL** - Relaciona baza podataka

### Azure Servisi
- Azure Kubernetes Service (AKS)
- Azure Container Apps
- Azure Container Registry (ACR)
- Azure Storage Account (Queue + Blob)
- Azure Key Vault

## Lokalno pokretanje

### Preduslov
- Docker i Docker Compose
- Python 3.11+
- Node.js 18+

### Pokretanje PostgreSQL baze
```bash
docker-compose up -d postgres
```

### Pokretanje servisa
```bash
# Catalog Service
cd catalog-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py

# Order Service
cd order-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py

# Invoice Worker
cd invoice-worker
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python worker.py

# Frontend
cd frontend
npm install
npm start
```

## Testiranje

```bash
# Unit testovi
pytest catalog-service/tests/
pytest order-service/tests/
pytest invoice-worker/tests/

# Integracioni testovi (nakon deploy-a)
pytest tests/integration/
```

## Deployment

Automatski deployment preko GitHub Actions na svaki push na `main` granu.
