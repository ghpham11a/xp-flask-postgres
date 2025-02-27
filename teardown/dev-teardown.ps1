# If UnauthorizedAccess (Temporary) -> powershell.exe -ExecutionPolicy Bypass -File ./dev-teardown.ps1
# If UnauthorizedAccess (Permanent) -> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

kubectl delete service xp-flask-postgres-service
kubectl delete deployment xp-flask-postgres-deployment
kubectl delete secrets xp-flask-postgres-secrets
kubectl delete pod redis-client
kubectl delete pod kafka-admin

# Need to scale down or resource will replicate and prevent helm uninstall
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