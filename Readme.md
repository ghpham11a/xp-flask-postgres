# Commands

### Running locally

```sh
flask --app app run --debug
```

### Freeze requirements

```sh
pip freeze > requirements.txt
```

### Build Docker image

```sh
docker build -t xp-micro-flask .
```

### Run the Docker container

```sh
docker run -p 80:80 xp-micro-flask
```

### List running containers

```sh
docker ps
```

### Stop container

```sh
docker stop <container_id_or_name>
```

### Apply Kubernetes resources (inside k8s)

```sh
kubectl apply -f dev-deployment.yaml
kubectl apply -f dev-service.yaml
kubectl apply -f dev-secrets.yaml
```

### List running Kubernetes pods

```sh
kubectl get pods
```

### Inspect pod logs

```sh
kubectl describe pod <pod-name>
```

### Delete resoruces

```sh
kubectl delete service xp-micro-flask-service
kubectl delete deployment xp-micro-flask-deployment
kubectl delete secrets dev-secrets
kubectl delete pvc data-xp-micro-flask-postgres-postgresql-0
kubectl delete pod redis-client
```

### Update Helm charts

```sh
helm repo update
```

### Install PostgreSQL, Kafka, Redis Helm chart with custom values

```sh
helm install xp-micro-flask-postgres -f dev-postgres-values.yaml bitnami/postgresql
helm install xp-micro-flask-kafka oci://registry-1.docker.io/bitnamicharts/kafka
helm install xp-micro-flask-redis oci://registry-1.docker.io/bitnamicharts/redis
```

```sh
helm upgrade --install xp-micro-flask-kafka oci://registry-1.docker.io/bitnamicharts/kafka --set auth.clientProtocol=sasl --set auth.saslMechanism=scram-sha-256 --set autoCreateTopics.enable=true
```

### Delete Helm charts

```sh
helm uninstall xp-micro-flask-postgres
helm uninstall xp-micro-flask-kafka
helm uninstall xp-micro-flask-redis
```

### Connect to redis in Powershell

```sh
$REDIS_PASSWORD = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((kubectl get secret --namespace default xp-micro-flask-redis -o jsonpath="{.data.redis-password}")))

kubectl run --namespace default redis-client --restart='Never'  --env REDIS_PASSWORD=$REDIS_PASSWORD  --image docker.io/bitnami/redis:7.4.2-debian-12-r4 --command -- sleep infinity

kubectl exec --tty -i redis-client --namespace default -- bash

redis-cli -h xp-micro-flask-redis-master -p 6379

AUTH [REDIS_PASSWORD]
```

### Connect to psql in Powershell

```sh
$POSTGRES_PASSWORD = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((kubectl get secret --namespace default xp-micro-flask-postgres-postgresql -o jsonpath="{.data.postgres-password}")))

kubectl run xp-micro-flask-postgres-postgresql-client --rm --tty -i --restart='Never' --namespace default --image docker.io/bitnami/postgresql:17.0.0-debian-12-r6 --env="PGPASSWORD=$POSTGRES_PASSWORD" --command -- psql --host xp-micro-flask-postgres-postgresql -U postgres -d postgres -p 5432
```

### Connect to psql in bash

```sh
secret=$(kubectl get secret --namespace default xp-micro-flask-postgres-postgresql -o jsonpath="{.data.postgres-password}")

POSTGRES_PASSWORD=$(echo "$secret" | base64 --decode)

kubectl run -i --tty temp-psql-client --rm --restart='Never' \
  --image docker.io/bitnami/postgresql:17.0.0-debian-12-r6 \
  --env="PGPASSWORD=$POSTGRES_PASSWORD" \
  --command -- psql --host xp-micro-flask-postgres-postgresql -U postgres -d postgres -p 5432
```

### Get Kafka password 

```sh
# bash
kubectl get secret xp-micro-flask-kafka-user-passwords -o jsonpath='{.data.client-passwords}' | base64 -d
```

### List topics on broker

```sh
kafka-topics.sh --list --bootstrap-server xp-micro-flask-kafka.default.svc.cluster.local:9092 --command-config /tmp/kafka-client.properties
```

### Creating a topic in Kafka

```sh
kubectl get pods --selector app.kubernetes.io/instance=xp-micro-flask-kafka
```

```sh
kubectl exec -it xp-micro-flask-kafka-controller-0 -- bash
```

```sh
kubectl exec -it xp-micro-flask-kafka-controller-0 -- kafka-topics.sh --list --bootstrap-server xp-micro-flask-kafka.default.svc.cluster.local:9092 --command-config /tmp/kafka-client.properties
```

```sh
kafka-topics.sh \
  --create \
  --topic orders \
  --partitions 3 \
  --replication-factor 3 \
  --bootstrap-server xp-micro-flask-kafka.default.svc.cluster.local:9092 \
  --command-config /tmp/kafka-client.properties
```

### Encode secret in PowerShell for k8s secrets

```sh
[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes('secret-value'))
```

### Decode secret in Powershell

```sh
[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('encoded-value'))
```

### Create table in psql

```sh
CREATE TABLE orders (id SERIAL PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL);
```

### list databases psql

```sh
\l
```

### Connect to database in psql

```sh
\c [DBNAME]
```

### Exit psql

```sh
\q
```

# Endpoints

localhost:80/todo