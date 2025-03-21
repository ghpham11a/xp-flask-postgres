import os

class Config:
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
    POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE", "postgres")

    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = os.getenv("REDIS_PORT", 6379)
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "password")

    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_SASL_USERNAME = os.getenv("KAFKA_SASL_USERNAME", "user1")
    KAFKA_SASL_PASSWORD = os.getenv("KAFKA_SASL_PASSWORD", "defautpass")

    HEC_URL = os.getenv("HEC_URL", "")
    HEC_TOKEN = os.getenv("HEC_TOKEN", "")