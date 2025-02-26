#!/usr/bin/env bash

# permission denied -> chmod +x dev-teardown.sh

# Exit immediately on error
set -e

kubectl delete service xp-micro-flask-service || echo "xp-micro-flask-service not found or already deleted."

kubectl delete deployment xp-micro-flask-deployment || echo "xp-micro-flask-deployment not found or already deleted."

kubectl delete secrets dev-secrets || echo "dev-secrets not found or already deleted."

kubectl scale statefulset xp-micro-flask-postgres-postgresql --replicas=0 

helm uninstall xp-micro-flask-postgres
helm uninstall xp-micro-flask-kafka 
helm uninstall xp-micro-flask-redis

kubectl delete pvc data-xp-micro-flask-postgres-postgresql-0 

kubectl delete pvc data-xp-micro-flask-kafka-controller-0
kubectl delete pvc data-xp-micro-flask-kafka-controller-1
kubectl delete pvc data-xp-micro-flask-kafka-controller-2

kubectl delete pvc redis-data-xp-micro-flask-redis-master-0 
kubectl delete pvc redis-data-xp-micro-flask-redis-replicas-0
kubectl delete pvc redis-data-xp-micro-flask-redis-replicas-1
kubectl delete pvc redis-data-xp-micro-flask-redis-replicas-2

echo "Teardown complete."
