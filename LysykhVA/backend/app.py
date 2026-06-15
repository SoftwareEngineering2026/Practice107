from flask import Flask, request, jsonify, Response
import os
import time
import logging

from prometheus_client import Counter
from prometheus_client import generate_latest
from prometheus_client import CONTENT_TYPE_LATEST

app = Flask(__name__)

# логирование
logging.basicConfig(level=logging.INFO)

# метрика
REQUEST_COUNTER = Counter(
    "user_requests_total",
    "Количество запросов к сервису анализа текста"
)

# ДОБАВИТЬ СЮДА
@app.route("/")
def home():

    REQUEST_COUNTER.inc()

    app.logger.info("User opened main page")

    return "Hello"


@app.route("/analyze", methods=["POST"])
def analyze():

    REQUEST_COUNTER.inc()

    app.logger.info("Получен запрос на анализ текста")

    data = request.json
    text = data["text"]

    with open("/data/task.txt", "w", encoding="utf-8") as f:
        f.write(text)

    while not os.path.exists("/data/result.txt"):
        time.sleep(1)

    with open("/data/result.txt", "r", encoding="utf-8") as f:
        result = f.read()

    os.remove("/data/result.txt")

    return jsonify({
        "result": result
    })


@app.route("/metrics")
def metrics():
    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST
    )


app.run(
    host="0.0.0.0",
    port=5000
)