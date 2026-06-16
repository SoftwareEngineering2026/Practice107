from flask import Flask, request, jsonify
import requests
import time
from prometheus_client import Counter, generate_latest, REGISTRY

app = Flask(__name__)

# Создаём свою метрику (число запросов)
request_counter = Counter('qr_requests_total', 'Total QR code generation requests')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    text = data.get('text')
    
    # Увеличиваем счётчик запросов
    request_counter.inc()
    
    # Отправляем задачу воркеру
    response = requests.post(
        'http://worker:5001/generate',
        json={'text': text}
    )
    
    return jsonify(response.json())

@app.route('/metrics', methods=['GET'])
def metrics():
    # Эндпоинт для сбора метрик Prometheus
    return generate_latest(REGISTRY), 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)