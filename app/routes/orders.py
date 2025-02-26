import os
import json
from flask import Blueprint, request, jsonify, current_app
from app.models import Order, CreateResponse, ReadResponse, UpdateResponse, DeleteResponse, ErrorResponse

orders = Blueprint("order", __name__)

@orders.route("/order", methods=["POST"])
def create_order():

    pg_pool = current_app.extensions["PG_POOL"]
    kafka_producer = current_app.extensions["KAFKA_PRODUCER"]

    conn = pg_pool.getconn()
    try:
        with conn.cursor() as cur:

            new_order = request.json
            title = new_order["title"]
            description = new_order["description"]

            cur.execute("INSERT INTO orders (title, description) VALUES (%s, %s) RETURNING id;", (title, description))
            order_id = str(cur.fetchone()[0])
            conn.commit()

            # Produce the message to topic "orders"
            kafka_producer.produce(
                topic="orders",
                value=json.dumps({ "order_id": order_id }).encode("utf-8"),
                on_delivery=delivery_report  # Optional callback
            )
            kafka_producer.flush(timeout=30)

            return jsonify(CreateResponse(order_id=order_id).model_dump()), 201
    except Exception as e:
        return ErrorResponse(message=str(e)).model_dump(), 500
    finally:
        pg_pool.putconn(conn)

@orders.route("/order", methods=["GET"])
def read_orders():

    pg_pool = current_app.extensions["PG_POOL"]
    redis_client = current_app.extensions["REDIS_CLIENT"]

    # 1) Check Redis first
    if redis_client:
        cached_json = redis_client.get("orders")
        if cached_json:
            # Reconstruct the ReadResponse (assuming Pydantic v2 or similar)
            response = ReadResponse.model_validate_json(cached_json)
            # Mark that we fetched it from cache:
            response.from_cache = True
            return jsonify(response.model_dump()), 200

    # 2) If no cache hit, fetch from PostgreSQL
    conn = pg_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, description FROM orders")
            rows = cur.fetchall()

            items = [Order(id=row[0], title=row[1], description=row[2]) for row in rows]
            response = ReadResponse(items=items)

            # 3) Write the entire response to Redis so future lookups avoid the DB
            redis_client.set("orders", response.model_dump_json(), ex=60)

            return jsonify(response.model_dump()), 200
    except Exception as e:
        return ErrorResponse(message=str(e)).model_dump(), 500
    finally:
        pg_pool.putconn(conn)

@orders.route("/order/<int:order_id>", methods=["GET"])
def read_order(order_id):

    pg_pool = current_app.extensions["PG_POOL"]
    redis_client = current_app.extensions["REDIS_CLIENT"]

    # 1) Check Redis first
    if redis_client:
        cached_json = redis_client.get(f"order:{order_id}")
        if cached_json:
            # Reconstruct the Order (assuming you have a Pydantic model or similar)
            item = Order.model_validate_json(cached_json)
            
            response = ReadResponse(items=[item], from_cache=True)
            return jsonify(response.model_dump()), 200

    # 2) If not in Redis, fetch from PostgreSQL
    conn = pg_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, description FROM orders WHERE id = %s", (order_id,))
            row = cur.fetchone()

            if row:
                # Build the Order model
                item = Order(id=row[0], title=row[1], description=row[2])
                response = ReadResponse(items=[item])
                
                # 3) Write to Redis for future lookups
                redis_client.set(
                    f"order:{order_id}",
                    item.model_dump_json(),
                    ex=60
                )

                return jsonify(response.model_dump()), 200
            else:
                # If no row found in the database
                return jsonify(ErrorResponse(message="Order not found").model_dump()), 404
    except Exception as e:
        return ErrorResponse(message=str(e)).model_dump(), 500
    finally:
        pg_pool.putconn(conn)
    
@orders.route("/order/<int:order_id>", methods=["PUT"])
def update_order(order_id):

    pg_pool = current_app.extensions["PG_POOL"]
    redis_client = current_app.extensions["REDIS_CLIENT"]

    conn = pg_pool.getconn()
    try:
        with conn.cursor() as cur:

            updated_order = request.json
            title = updated_order.get("title")
            description = updated_order.get("description")

            cur.execute("UPDATE orders SET title = %s, description = %s WHERE id = %s RETURNING id, title, description", (title, description, order_id))
            order = cur.fetchone()
            conn.commit()
            if order:
                return jsonify(UpdateResponse(order_id=order_id).model_dump()), 201
            else:
                return jsonify(ErrorResponse(message="Order not found").model_dump()), 404
    except:
        return ErrorResponse(message="Error creating order").model_dump(), 500
    finally:
        pg_pool.putconn(conn)

@orders.route("/order/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):

    pg_pool = current_app.extensions["PG_POOL"]

    conn = pg_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM orders WHERE id = %s RETURNING id", (order_id,))
            order = cur.fetchone()
            conn.commit()
            if order:
                return jsonify(DeleteResponse(order_id=order_id).model_dump()), 201
            else:
                return jsonify(ErrorResponse(message="Order not found").model_dump()), 404
    except:
        return ErrorResponse(message="Error creating order").model_dump(), 500
    finally:
        pg_pool.putconn(conn)

# Kafka delivery report callback

def delivery_report(err, msg):
    """Delivery callback called once per message to report delivery result."""
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(
            f"Message delivered to {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}"
        )

    
