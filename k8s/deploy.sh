
set -e

echo "Deploying Cloud Order System to AKS"
echo "========================================"


echo "Connected to cluster: $(kubectl config current-context)"
echo ""

# 1. Namespace
echo "Creating namespace..."
kubectl apply -f k8s/namespace.yaml

# 2. ConfigMaps
echo "Applying ConfigMaps..."
kubectl apply -f k8s/configmaps/

# 3. Secrets
echo "Applying Secrets..."
kubectl apply -f k8s/secrets/

# 4. Database init ConfigMaps
echo "Applying DB init scripts..."
kubectl apply -f k8s/database/db-init-configmaps.yaml

# 5. Databases (StatefulSets)
echo "Deploying databases..."
kubectl apply -f k8s/database/catalog-db.yaml
kubectl apply -f k8s/database/order-db.yaml

echo "Waiting for databases to be ready..."
kubectl rollout status statefulset/catalog-db -n cloud-order-system --timeout=120s
kubectl rollout status statefulset/order-db -n cloud-order-system --timeout=120s

# 6. Services
echo "Deploying services..."
kubectl apply -f k8s/catalog/deployment.yaml
kubectl apply -f k8s/order/deployment.yaml
kubectl apply -f k8s/frontend/deployment.yaml

echo "Waiting for services to be ready..."
kubectl rollout status deployment/catalog-service -n cloud-order-system --timeout=120s
kubectl rollout status deployment/order-service   -n cloud-order-system --timeout=120s
kubectl rollout status deployment/frontend        -n cloud-order-system --timeout=120s

# 7. Ingress
echo "Applying Ingress..."
kubectl apply -f k8s/ingress.yaml

echo ""
echo "Deployment complete!"
echo ""
echo "Pod status:"
kubectl get pods -n cloud-order-system

echo ""
echo "Services:"
kubectl get services -n cloud-order-system

echo ""
echo "Ingress:"
kubectl get ingress -n cloud-order-system
