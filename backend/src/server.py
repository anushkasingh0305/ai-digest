"""
AI Digest Backend API Server
Flask REST API with JWT authentication
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from pathlib import Path
import sys

# Add backend to Python path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from services.auth import AuthService, token_required
from services.config import ConfigService
from services.storage import StorageService
from services.webhooks import WebhookService
from services.scheduler import SchedulerService
from services.metrics import MetricsService

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Initialize services
auth_service = AuthService()
config_service = ConfigService()
storage_service = StorageService()
webhook_service = WebhookService()
scheduler_service = SchedulerService()
metrics_service = MetricsService()


# ============= Health & Info =============
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'ai-digest',
        'version': '0.1.0'
    })


@app.route('/info', methods=['GET'])
def info():
    return jsonify({
        'name': 'AI Digest',
        'version': '0.1.0',
        'description': 'AI-powered content digest system',
        'endpoints': 38
    })


# ============= Authentication =============
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    result = auth_service.login(username, password)
    if result['success']:
        return jsonify({
            'token': result['token'],
            'user': username,
            'expires_in_hours': 24
        })
    
    return jsonify({'error': result['message']}), 401


# ============= Configuration =============
@app.route('/api/config', methods=['GET'])
@token_required
def get_config():
    return jsonify(config_service.get_config())


@app.route('/api/config', methods=['POST'])
@token_required
def update_config():
    config_service.update_config(request.json)
    return jsonify({'success': True})


@app.route('/api/config/adapters', methods=['GET'])
@token_required
def get_adapters_config():
    return jsonify(config_service.get_adapters_config())


@app.route('/api/config/adapters/<name>', methods=['POST'])
@token_required
def update_adapter_config(name):
    config_service.update_adapter_config(name, request.json)
    return jsonify({'success': True})


@app.route('/api/config/delivery', methods=['GET'])
@token_required
def get_delivery_config():
    return jsonify(config_service.get_delivery_config())


@app.route('/api/config/delivery', methods=['POST'])
@token_required
def update_delivery_config():
    config_service.update_delivery_config(request.json)
    return jsonify({'success': True})


@app.route('/api/config/scheduler', methods=['GET'])
@token_required
def get_scheduler_config():
    return jsonify(config_service.get_scheduler_config())


@app.route('/api/config/scheduler', methods=['POST'])
@token_required
def update_scheduler_config():
    config_service.update_scheduler_config(request.json)
    return jsonify({'success': True})


@app.route('/api/config/logging', methods=['GET'])
@token_required
def get_logging_config():
    return jsonify(config_service.get_logging_config())


@app.route('/api/config/logging', methods=['POST'])
@token_required
def update_logging_config():
    config_service.update_logging_config(request.json)
    return jsonify({'success': True})


# ============= Pipeline =============
@app.route('/api/pipeline/run', methods=['POST'])
@token_required
def run_pipeline():
    data = request.json
    deliver = data.get('deliver', False)
    # Implementation would go here
    return jsonify({'success': True, 'message': 'Pipeline started', 'deliver': deliver})


# ============= Scheduler =============
@app.route('/api/scheduler/status', methods=['GET'])
@token_required
def get_scheduler_status():
    return jsonify(scheduler_service.get_status())


@app.route('/api/scheduler/start', methods=['POST'])
@token_required
def start_scheduler():
    data = request.json
    scheduler_service.start(
        deliver=data.get('deliver', True),
        hour=data.get('hour', 6),
        minute=data.get('minute', 0)
    )
    return jsonify({'success': True, 'message': 'Scheduler started'})


@app.route('/api/scheduler/stop', methods=['POST'])
@token_required
def stop_scheduler():
    scheduler_service.stop()
    return jsonify({'success': True, 'message': 'Scheduler stopped'})


# ============= Digests =============
@app.route('/api/digests', methods=['GET'])
@token_required
def list_digests():
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    days = request.args.get('days', None, type=int)
    
    digests = storage_service.list_digests(limit, offset, days)
    return jsonify(digests)


@app.route('/api/digests/<digest_id>', methods=['GET'])
@token_required
def get_digest(digest_id):
    digest = storage_service.get_digest(digest_id)
    if digest:
        return jsonify(digest)
    return jsonify({'error': 'Digest not found'}), 404


@app.route('/api/digests/<digest_id>', methods=['DELETE'])
@token_required
def delete_digest(digest_id):
    storage_service.delete_digest(digest_id)
    return jsonify({'success': True})


# ============= Webhooks =============
@app.route('/api/webhooks', methods=['GET'])
@token_required
def list_webhooks():
    return jsonify(webhook_service.list_webhooks())


@app.route('/api/webhooks', methods=['POST'])
@token_required
def create_webhook():
    webhook = webhook_service.create_webhook(request.json)
    return jsonify(webhook)


@app.route('/api/webhooks/<webhook_id>', methods=['GET'])
@token_required
def get_webhook(webhook_id):
    webhook = webhook_service.get_webhook(webhook_id)
    if webhook:
        return jsonify(webhook)
    return jsonify({'error': 'Webhook not found'}), 404


@app.route('/api/webhooks/<webhook_id>', methods=['PUT'])
@token_required
def update_webhook(webhook_id):
    webhook = webhook_service.update_webhook(webhook_id, request.json)
    return jsonify(webhook)


@app.route('/api/webhooks/<webhook_id>', methods=['DELETE'])
@token_required
def delete_webhook(webhook_id):
    webhook_service.delete_webhook(webhook_id)
    return jsonify({'success': True})


@app.route('/api/webhooks/<webhook_id>/test', methods=['POST'])
@token_required
def test_webhook(webhook_id):
    result = webhook_service.test_webhook(webhook_id)
    return jsonify(result)


# ============= Metrics =============
@app.route('/metrics', methods=['GET'])
def metrics():
    return metrics_service.export_prometheus()


if __name__ == '__main__':
    print("🚀 AI Digest Backend API Server")
    print("📍 Running on http://localhost:5000")
    print("📚 API endpoints: /api/*")
    print("❤️  Health check: /health")
    app.run(host='0.0.0.0', port=5000, debug=True)
