# Commands


###### Other useful commands during development

```sh
# Run your non-containerized application
flask --app app run --debug

# Run the docker container locally
docker run -p 80:80 xp-flask-postgres

# List running containers
docker ps

# Stop this container
docker stop <container_id_or_name>

# Encode string value in Powershell
[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes('secret-value'))

# Decode string value in Powershell
[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('encoded-value'))

# List running Kubernetes pods
kubectl get pods

# Inspect pod logs
kubectl describe pod <pod-name>

# List databases in psql
postgres=# \l

# List tables in database in psql
postgres=# \dt

# Connect to database in psql
postgres=# \c [DBNAME]

# Exit psql
postgres=# \dt
```

###### 1. Containerize the application

Ensure the requirements.txt file is up to date and that it is in the root directory

```sh
pip freeze > requirements.txt
```

Run this in the same folder where the Dockerfile is

```sh
docker build -t xp-flask-postgres .
```

###### 2. Add Helm repositories

Charts from Bitnami is needed for Neo4j

```sh
helm repo add bitnami https://charts.bitnami.com/bitnami
```

This repo from Splunk will give us the Splunk operator

```sh
helm repo add splunk https://splunk.github.io/splunk-operator/
```

Run this command to make sure Helm is using the most up to date resources

```sh
helm repo update
```

###### 3. Setup PostgreSQL

Setup PostgreSQL containers using values from dev-postgres-values.yaml. This is in the k8s folder.

```sh
helm install xp-postgres -f dev-postgres-config.yaml bitnami/postgresql
```

Connect to the PostgreSQL in the container via psql. First set the password.

```sh
# set admin password with Powershell
$POSTGRES_PASSWORD = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((kubectl get secret --namespace default xp-postgres-postgresql -o jsonpath="{.data.postgres-password}")))

# set admin password in bash
secret=$(kubectl get secret --namespace default xp-flask-postgres-postgres-postgresql -o jsonpath="{.data.postgres-password}")

POSTGRES_PASSWORD=$(echo "$secret" | base64 --decode)
```

Using the password from above, get into the container and launch psql

```sh
kubectl run xp-postgres-postgresql-client --rm --tty -i --restart='Never' --namespace default --image docker.io/bitnami/postgresql:17.0.0-debian-12-r6 --env="PGPASSWORD=$POSTGRES_PASSWORD" --command -- psql --host xp-postgres-postgresql -U postgres -d postgres -p 5432
```

Create the table

```sh
postgres=# CREATE TABLE orders (id SERIAL PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL);
```

To check that it was created successfully

```sh
postgres=# \dt
```

Quit psql

```sh
postgres=# \q
```

###### 3. Setup Kafka

Install Kafka Helm chart

```sh
helm install xp-kafka oci://registry-1.docker.io/bitnamicharts/kafka
```

To check that pods were spun up

```sh
kubectl get pods --selector app.kubernetes.io/instance=xp-kafka
```

To create the topics, we will start another pod that goes into the Kafka pods and creates the topics and shuts down. To do this, we need to find the Kafka password and update it's value in the dev-kafka-topics-admin.yaml. 

```sh
# This gets an encoded value
kubectl get secret xp-kafka-user-passwords -o jsonpath='{.data.client-passwords}'

# we need the decoded version to put into the yaml
# Powershell
[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((kubectl get secret xp-kafka-user-passwords -o jsonpath='{.data.client-passwords}')))

# bash
kubectl get secret xp-flask-postgres-kafka-user-passwords -o jsonpath='{.data.client-passwords}' | base64 -d
```

Get the password and update the password field in dev-kafka-topics-admin.yaml

```
... required username=\"user1\" password=\"zRycaPH3fQ\";" >> /tmp/kafka-client.properties ...
```

Then just run this command which applies the yaml updates

```sh
kubectl apply -f dev-kafka-topics-admin.yaml
```

###### 3. Setup Redis

Install Redis Helm chart

```sh
helm install xp-redis oci://registry-1.docker.io/bitnamicharts/redis
```

Optional: connect to Redis

```sh
# Store the password in Powershell
$REDIS_PASSWORD = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((kubectl get secret --namespace default xp-flask-postgres-redis -o jsonpath="{.data.redis-password}")))

kubectl run --namespace default redis-client --restart='Never' --env REDIS_PASSWORD=$REDIS_PASSWORD  --image docker.io/bitnami/redis:7.4.2-debian-12-r4 --command -- sleep infinity

kubectl exec --tty -i redis-client --namespace default -- bash

redis-cli -h xp-flask-postgres-redis-master -p 6379

AUTH [REDIS_PASSWORD]
```

# 4. Setup up application in k8s

Setup service to allow outside communication

```sh
kubectl apply -f dev-service.yaml
```

Setup configuration which will be used my application pods

```sh
kubectl apply -f dev-configmap.yaml
```

Setup secrets which will be used my application pods

```sh
kubectl apply -f dev-secrets.yaml
```

Setup deployment which is responsible for creating objects and manage the pods

```sh
kubectl apply -f dev-deployment.yaml
```

# Endpoints

localhost:80/todo