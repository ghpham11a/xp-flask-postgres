# If UnauthorizedAccess (Temporary) -> powershell.exe -ExecutionPolicy Bypass -File ./dev-teardown.ps1
# If UnauthorizedAccess (Permanent) -> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

kubectl delete service xp-micro-flask-service
kubectl delete deployment xp-micro-flask-deployment
kubectl delete secrets dev-secrets
kubectl delete pod redis-client
kubectl delete pod kafka-admin

# Need to scale down or resource will replicate and prevent helm uninstall
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