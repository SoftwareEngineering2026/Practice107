from flask import Flask, request, jsonify
import qrcode
import io
import base64
import time
import logging
from prometheus_client import Counter, generate_latest, REGISTRY

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Метрика для числа ошибок
error_counter = Counter('qr_errors_total', 'Total QR generation errors')

@app.route('/generate', methods=['POST'])
def generate_qr():
    data = request.get_json()
    text = data.get('text')
    
    logger.info(f"Generating QR for text: {text[:50]}...")
    
    try:
        time.sleep(2)
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(text)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        logger.info(f"QR generated successfully for text: {text[:50]}...")
        
        return jsonify({'qr': img_base64})
    
    except Exception as e:
        error_counter.inc()
        logger.error(f"Error generating QR: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/metrics', methods=['GET'])
def metrics():
    return generate_latest(REGISTRY), 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)