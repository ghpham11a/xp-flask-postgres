import os

# PostgreSQL
# from psycopg2 import pool

import psycopg2.pool


def init_pg(app):
    """
    Initialize a global connection pool for PostgreSQL using psycopg2.
    """
    try:
        user = app.config["POSTGRES_USER"]
        password = app.config["POSTGRES_PASSWORD"]
        host = app.config["POSTGRES_HOST"]
        port = int(app.config["POSTGRES_PORT"])
        database = app.config["POSTGRES_DATABASE"]

        pg_pool = psycopg2.pool.SimpleConnectionPool(
            1,             
            10,            
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
    except Exception as e:
        print(f"PostgreSQL connection pool failed on initialization. {e}")
        return None

    # Optionally, you could verify the pool is working by getting/returning a connection:
    if pg_pool:
        print("PostgreSQL connection pool created successfully!")
        return pg_pool

# Redis

import redis

def init_redis(app):

    # Pull redis configuration from your app config or environment variables
    redis_host = app.config["REDIS_HOST"]
    redis_port =  int(app.config["REDIS_PORT"])
    redis_password = app.config["REDIS_PASSWORD"]
    redis_client = redis.Redis(
        host=redis_host, 
        port=redis_port, 
        password=redis_password,
        decode_responses=True
    )

    try:
        result = redis_client.ping()
        print(f"Ping response from Redis: {result}")  # Should be True or "PONG"
        return redis_client
    except redis.exceptions.ConnectionError as e:
        print(f"Failed to connect to Redis: {e}")
        return None

# Kafka

from confluent_kafka import Producer

def init_kafka_producer(app):
    """
    Initialize a Kafka producer using confluent_kafka.
    """
    print(app.config)
    try:
        kafka_config = {
            "bootstrap.servers": app.config["KAFKA_BOOTSTRAP_SERVERS"],
            "security.protocol": "SASL_PLAINTEXT",
            "sasl.mechanisms": "PLAIN",
            "sasl.username": app.config["KAFKA_SASL_USERNAME"],
            "sasl.password": app.config["KAFKA_SASL_PASSWORD"]
        }
        kafka_producer = Producer(kafka_config)

        kafka_producer.produce(
            topic="orders",
            value=json.dumps({ "test_id": "test_id_id" }).encode("utf-8"),
            on_delivery=delivery_report  # Optional callback
        )
        kafka_producer.flush(timeout=30)

        print("Kafka producer created successfully!")
        return kafka_producer
    except Exception as e:
        print(f"Kafka producer failed on initialization. {e}")
        return None

def delivery_report(err, msg):
    """Delivery callback called once per message to report delivery result."""
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}")

# Middleware

def init_middleware(app):
    def middleware(environ, start_response):
        print("Incoming request path:", environ.get('PATH_INFO'))

        def custom_start_response(status, headers, exc_info=None):
            # Add or modify headers here
            headers.append(("X-Pod", os.getenv("POD_NAME", "")))
            return start_response(status, headers, exc_info)

        return app(environ, custom_start_response)

    return middleware

# Kafka Consumer (TESTING ONLY)

from confluent_kafka import Consumer
import threading
import time
import json

def init_kafka_consumer(app):
    """
    Continuously poll the 'orders' topic in a loop.
    For local testing only—NOT recommended for production in the same process.
    """
    conf = {
        "bootstrap.servers": app.config["KAFKA_BOOTSTRAP_SERVERS"],
        "group.id": "xp-flask-postgres-test-consumer-group",
        "auto.offset.reset": "earliest",
        "security.protocol": "SASL_PLAINTEXT",
        "sasl.mechanisms": "PLAIN",
        "sasl.username": app.config["KAFKA_SASL_USERNAME"],
        "sasl.password": app.config["KAFKA_SASL_PASSWORD"]
    }
    consumer = Consumer(conf)
    consumer.subscribe(["orders"])

    app.logger.info("Kafka Consumer started...")

    while True:
        if not getattr(app, "keep_consuming", True):
            # This allows us to break if we add a shutdown mechanism
            break

        msg = consumer.poll(1.0)  # Wait up to 1s for a new message
        if msg is None:
            continue  # No new messages
        if msg.error():
            app.logger.error(f"Consumer error: {msg.error()}")
            continue

        data = msg.value().decode("utf-8")
        try:
            json_data = json.loads(data)
        except json.JSONDecodeError:
            json_data = {"raw": data}

        app.logger.info(f"Consumed message from 'orders': {json_data}")

    consumer.close()

def init_test_kafka_consumer(app):
    """Launch the consumer loop in a background thread."""
    thread = threading.Thread(target=init_kafka_consumer, args=(app,), daemon=True)
    thread.start()
    app.logger.info("Consumer thread started.")