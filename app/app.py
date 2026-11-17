import os
import time
import psycopg2
from flask import Flask, jsonify, request
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)  # exposes /metrics


def get_conn():
    return psycopg2.connect(os.environ["DATABASE_URL"])


def init_db():
    for _ in range(10):
        try:
            conn = get_conn()
            with conn, conn.cursor() as cur:
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS tasks ("
                    "id SERIAL PRIMARY KEY, title TEXT NOT NULL, "
                    "done BOOLEAN DEFAULT FALSE)"
                )
            conn.close()
            return
        except psycopg2.OperationalError:
            time.sleep(2)


if os.environ.get("DATABASE_URL"):
    init_db()


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/tasks")
def list_tasks():
    conn = get_conn()
    with conn, conn.cursor() as cur:
        cur.execute("SELECT id, title, done FROM tasks ORDER BY id")
        rows = cur.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "title": r[1], "done": r[2]} for r in rows])


@app.post("/tasks")
def create_task():
    title = (request.get_json(silent=True) or {}).get("title")
    if not title:
        return jsonify(error="title required"), 400
    conn = get_conn()
    with conn, conn.cursor() as cur:
        cur.execute("INSERT INTO tasks (title) VALUES (%s) RETURNING id", (title,))
        new_id = cur.fetchone()[0]
    conn.close()
    return jsonify(id=new_id, title=title, done=False), 201