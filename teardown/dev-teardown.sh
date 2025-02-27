#!/usr/bin/env bash

# permission denied -> chmod +x dev-teardown.sh

# Exit immediately on error
set -e

kubectl delete service xp-flask-postgres-service || echo "xp-flask-postgres-service not found or already deleted."

kubectl delete deployment xp-flask-postgres-deployment || echo "xp-flask-postgres-deployment not found or already deleted."

kubectl delete secrets xp-flask-postgres-secrets || echo "xp-flask-postgres-secrets not found or already deleted."

kubectl scale statefulset xp-flask-postgres-postgres-postgresql --replicas=0 

helm uninstall xp-flask-postgres-postgres
helm uninstall xp-flask-postgres-kafka 
helm uninstall xp-flask-postgres-redis

kubectl delete pvc data-xp-flask-postgres-postgres-postgresql-0 

kubectl delete pvc data-xp-flask-postgres-kafka-controller-0
kubectl delete pvc data-xp-flask-postgres-kafka-controller-1
kubectl delete pvc data-xp-flask-postgres-kafka-controller-2

kubectl delete pvc redis-data-xp-flask-postgres-redis-master-0 
kubectl delete pvc redis-data-xp-flask-postgres-redis-replicas-0
kubectl delete pvc redis-data-xp-flask-postgres-redis-replicas-1
kubectl delete pvc redis-data-xp-flask-postgres-redis-replicas-2

echo "Teardown complete."
