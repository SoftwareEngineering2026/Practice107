import os
import time

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from redis import Redis
from rq import Queue
from rq.job import Job
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from tasks import process_text_task


REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
QUEUE_NAME = os.getenv("QUEUE_NAME", "text_tasks")


app = Flask(__name__)
CORS(app)


REQUEST_COUNT = Counter(
    "ai_text_helper_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "http_status"]
)

TASKS_CREATED = Counter(
    "ai_text_helper_tasks_created_total",
    "Total number of created text processing tasks",
    ["mode"]
)

REQUEST_LATENCY = Histogram(
    "ai_text_helper_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"]
)


redis_conn = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=False)
queue = Queue(QUEUE_NAME, connection=redis_conn)


@app.before_request
def before_request():
    request.start_time = time.time()


@app.after_request
def after_request(response):
    endpoint = request.path

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=endpoint,
        http_status=response.status_code
    ).inc()

    if hasattr(request, "start_time"):
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=endpoint
        ).observe(time.time() - request.start_time)

    return response


@app.route("/metrics", methods=["GET"])
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "service": "backend"
    })


@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Request body must be JSON"
        }), 400

    text = data.get("text", "").strip()
    mode = data.get("mode", "improve").strip()

    if not text:
        return jsonify({
            "error": "Text is required"
        }), 400

    allowed_modes = ["improve", "formal", "friendly", "shorten", "fix"]

    if mode not in allowed_modes:
        return jsonify({
            "error": "Invalid mode",
            "allowed_modes": allowed_modes
        }), 400

    job = queue.enqueue(
        process_text_task,
        text,
        mode,
        job_timeout=300,
        result_ttl=3600,
        failure_ttl=3600
    )

    TASKS_CREATED.labels(mode=mode).inc()

    return jsonify({
        "task_id": job.id,
        "status": "queued"
    }), 202


@app.route("/api/tasks/<task_id>", methods=["GET"])
def get_task_status(task_id):
    try:
        job = Job.fetch(task_id, connection=redis_conn)
    except Exception:
        return jsonify({
            "error": "Task not found"
        }), 404

    if job.is_queued:
        return jsonify({
            "task_id": job.id,
            "status": "queued"
        })

    if job.is_started:
        return jsonify({
            "task_id": job.id,
            "status": "processing"
        })

    if job.is_finished:
        return jsonify({
            "task_id": job.id,
            "status": "done",
            "result": job.result
        })

    if job.is_failed:
        return jsonify({
            "task_id": job.id,
            "status": "failed",
            "error": str(job.exc_info)
        }), 500

    return jsonify({
        "task_id": job.id,
        "status": job.get_status()
    })


@app.route("/api/modes", methods=["GET"])
def get_modes():
    return jsonify({
        "modes": [
            {
                "id": "improve",
                "title": "Улучшить текст",
                "description": "Делает текст более понятным и грамотным"
            },
            {
                "id": "formal",
                "title": "Официальный стиль",
                "description": "Переписывает текст в более деловом стиле"
            },
            {
                "id": "friendly",
                "title": "Дружелюбный стиль",
                "description": "Делает текст более мягким и дружелюбным"
            },
            {
                "id": "shorten",
                "title": "Сократить текст",
                "description": "Сокращает текст, сохраняя основной смысл"
            },
            {
                "id": "fix",
                "title": "Исправить ошибки",
                "description": "Исправляет грамматику и орфографию"
            }
        ]
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)