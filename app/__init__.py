import os

from flask import Flask
from app.extensions import init_middleware, init_pg, init_redis, init_kafka_producer, init_test_kafka_consumer
from app.routes import orders
from app.config import Config
import requests
import json

def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    pg_pool = init_pg(app)
    redis_client = init_redis(app)
    kafka_producer = init_kafka_producer(app)
    # init_test_kafka_consumer(app)

    app.extensions["PG_POOL"] = pg_pool
    app.extensions["REDIS_CLIENT"] = redis_client
    app.extensions["KAFKA_PRODUCER"] = kafka_producer

    app.register_blueprint(orders.orders)

    app.wsgi_app = init_middleware(app.wsgi_app)

    return app

def test_splunk(app):
    # 2. Your HEC token.
    splunk_hec_url = app.config["HEC_URL"]
    splunk_token = app.config["HEC_TOKEN"]

    print("splunk_hec_url", splunk_hec_url, "splunk_token", splunk_token)

    app.config

    # 3. Set the headers with Splunk authorization.
    headers = {
        "Authorization": f"Splunk {splunk_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "event": {
            "message": "Hello from inside Kubernetes!",
            "extra_info": "This is a sample Python POST request"
        }
    }

    try:
        # 5. Make the POST request to Splunk HEC.
        response = requests.post(splunk_hec_url, headers=headers, data=json.dumps(payload), timeout=5)

        # 6. Print the status and response.
        print("Status Code:", response.status_code)
        print("Response Body:", response.text)

    except requests.exceptions.RequestException as e:
        print("Error sending POST request:", str(e))