import os

from flask import Flask
from app.extensions import init_middleware, init_pg, init_redis, init_kafka_producer, init_test_kafka_consumer
from app.routes import orders
from app.config import Config

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