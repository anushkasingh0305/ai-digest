"""
AI Digest Backend API Server - Simplified Version
Flask REST API with JWT authentication
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import jwt
import os
import uuid
import requests
from datetime import datetime, timedelta
from functools import wraps

# In-memory storage for digests
digests_store = {}

# Telegram Configuration
TELEGRAM_BOT_TOKEN = '8411332355:AAFtW2tvGJVbXRhtJU_46Q3Ihasp1eu545c'
TELEGRAM_CHAT_ID = 6614642154  # Must be integer, not string


def send_telegram_message(message: str) -> bool:
    """Send a message via Telegram bot."""
    try:
        url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message
        }
        response = requests.post(url, json=payload, timeout=10)
        print(f'Telegram response: {response.status_code} - {response.text}')
        return response.status_code == 200
    except Exception as e:
        print(f'Telegram send error: {e}')
        return False


def format_digest_for_telegram(digest: dict) -> str:
    """Format digest items for Telegram message."""
    lines = ['🤖 AI Digest Update\n']
    lines.append(f'📅 {datetime.now().strftime("%Y-%m-%d %H:%M")}\n')
    lines.append(f'📊 {len(digest.get("items", []))} items\n')
    lines.append('─' * 20 + '\n')
    
    for item in digest.get('items', []):
        score = item.get('score', 0)
        stars = '⭐' * int(score * 5)
        title = item.get("title", "Untitled")
        lines.append(f'\n📌 {title}')
        lines.append(f'{stars} ({int(score*100)}%)')
        lines.append(f'📰 {item.get("source", "Unknown")}')
        text = item.get("text", "")[:100]
        lines.append(f'{text}...')
        lines.append(f'🔗 {item.get("url", "")}')
    
    return '\n'.join(lines)

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {"origins": ["http://localhost:3000", "http://localhost:3001"]},
    r"/health": {"origins": ["http://localhost:3000", "http://localhost:3001"]},
    r"/info": {"origins": ["http://localhost:3000", "http://localhost:3001"]}
})

# Configuration
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'admin'


# Token decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated


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
    
    if username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD:
        token = jwt.encode({
            'user': username,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'token': token,
            'user': username,
            'expires_in_hours': 24
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401


# ============= Configuration =============
@app.route('/api/config', methods=['GET'])
@token_required
def get_config():
    return jsonify({
        'adapters': [],
        'delivery': {},
        'scheduler': {}
    })


@app.route('/api/config', methods=['POST'])
@token_required
def update_config():
    return jsonify({'success': True})


@app.route('/api/config/adapters', methods=['GET'])
@token_required
def get_adapters_config():
    return jsonify([])


@app.route('/api/config/adapters/<name>', methods=['POST'])
@token_required
def update_adapter_config(name):
    return jsonify({'success': True})


@app.route('/api/config/delivery', methods=['GET'])
@token_required
def get_delivery_config():
    return jsonify({})


@app.route('/api/config/delivery', methods=['POST'])
@token_required
def update_delivery_config():
    return jsonify({'success': True})


@app.route('/api/config/scheduler', methods=['GET'])
@token_required
def get_scheduler_config():
    return jsonify({})


@app.route('/api/config/scheduler', methods=['POST'])
@token_required
def update_scheduler_config():
    return jsonify({'success': True})


@app.route('/api/config/logging', methods=['GET'])
@token_required
def get_logging_config():
    return jsonify({})


@app.route('/api/config/logging', methods=['POST'])
@token_required
def update_logging_config():
    return jsonify({'success': True})


# ============= Pipeline =============
@app.route('/api/pipeline/run', methods=['POST'])
@token_required
def run_pipeline():
    data = request.json or {}
    deliver = data.get('deliver', False)
    
    # Create a new digest with sample items
    digest_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    # Sample items that would come from adapters
    items = [
        {
            'id': 'item-1',
            'title': 'OpenAI Announces GPT-5 with Enhanced Reasoning',
            'url': 'https://example.com/openai-gpt5',
            'text': 'OpenAI has announced GPT-5, featuring significant improvements in reasoning capabilities and reduced hallucinations.',
            'source': 'TechNews',
            'score': 0.95
        },
        {
            'id': 'item-2',
            'title': 'Google DeepMind Achieves Breakthrough in Protein Folding',
            'url': 'https://example.com/deepmind-protein',
            'text': 'DeepMind researchers have developed a new AI model that can predict protein structures with unprecedented accuracy.',
            'source': 'Science Daily',
            'score': 0.92
        },
        {
            'id': 'item-3',
            'title': 'Microsoft Copilot Gets Major Update',
            'url': 'https://example.com/copilot-update',
            'text': 'Microsoft has released a major update to Copilot, adding new features for code generation and debugging.',
            'source': 'Dev Weekly',
            'score': 0.88
        },
        {
            'id': 'item-4',
            'title': 'New AI Regulations Proposed in EU',
            'url': 'https://example.com/eu-ai-regulations',
            'text': 'The European Union has proposed new regulations for AI systems, focusing on transparency and accountability.',
            'source': 'Policy Watch',
            'score': 0.85
        },
        {
            'id': 'item-5',
            'title': 'Anthropic Releases Claude 4 with Extended Context',
            'url': 'https://example.com/claude-4',
            'text': 'Anthropic has launched Claude 4, featuring a 500K token context window and improved instruction following.',
            'source': 'AI News',
            'score': 0.90
        }
    ]
    
    digest = {
        'id': digest_id,
        'created_at': now.isoformat() + 'Z',
        'item_count': len(items),
        'items': items,
        'delivered': deliver,
        'status': 'completed'
    }
    
    # Store the digest
    digests_store[digest_id] = digest
    
    # Send Telegram notification
    telegram_sent = False
    telegram_error = None
    try:
        message = format_digest_for_telegram(digest)
        telegram_sent = send_telegram_message(message)
        if telegram_sent:
            digest['telegram_sent'] = True
    except Exception as e:
        telegram_error = str(e)
    
    return jsonify({
        'success': True,
        'message': 'Pipeline completed successfully',
        'digest_id': digest_id,
        'item_count': len(items),
        'delivered': deliver,
        'telegram_sent': telegram_sent,
        'telegram_error': telegram_error
    })


# ============= Scheduler =============
@app.route('/api/scheduler/status', methods=['GET'])
@token_required
def get_scheduler_status():
    return jsonify({'running': False, 'next_run': None})


@app.route('/api/scheduler/start', methods=['POST'])
@token_required
def start_scheduler():
    return jsonify({'success': True, 'message': 'Scheduler started'})


@app.route('/api/scheduler/stop', methods=['POST'])
@token_required
def stop_scheduler():
    return jsonify({'success': True, 'message': 'Scheduler stopped'})


# ============= Digests =============
@app.route('/api/digests', methods=['GET'])
@token_required
def list_digests():
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Get all digests sorted by created_at (newest first)
    all_digests = sorted(
        digests_store.values(),
        key=lambda d: d.get('created_at', ''),
        reverse=True
    )
    
    # Apply pagination
    paginated = all_digests[offset:offset + limit]
    
    # Return summary without full items
    result = []
    for d in paginated:
        result.append({
            'id': d['id'],
            'created_at': d['created_at'],
            'item_count': d['item_count'],
            'delivered': d.get('delivered', False),
            'status': d.get('status', 'completed')
        })
    
    return jsonify(result)


@app.route('/api/digests/<digest_id>', methods=['GET'])
@token_required
def get_digest(digest_id):
    if digest_id in digests_store:
        return jsonify(digests_store[digest_id])
    return jsonify({'error': 'Digest not found'}), 404


@app.route('/api/digests/<digest_id>', methods=['DELETE'])
@token_required
def delete_digest(digest_id):
    if digest_id in digests_store:
        del digests_store[digest_id]
    return jsonify({'success': True})


# ============= Webhooks =============
@app.route('/api/webhooks', methods=['GET'])
@token_required
def list_webhooks():
    return jsonify([])


@app.route('/api/webhooks', methods=['POST'])
@token_required
def create_webhook():
    return jsonify({'id': '1', 'name': request.json.get('name')})


@app.route('/api/webhooks/<webhook_id>', methods=['GET'])
@token_required
def get_webhook(webhook_id):
    return jsonify({'error': 'Webhook not found'}), 404


@app.route('/api/webhooks/<webhook_id>', methods=['PUT'])
@token_required
def update_webhook(webhook_id):
    return jsonify({'id': webhook_id})


@app.route('/api/webhooks/<webhook_id>', methods=['DELETE'])
@token_required
def delete_webhook(webhook_id):
    return jsonify({'success': True})


@app.route('/api/webhooks/<webhook_id>/test', methods=['POST'])
@token_required
def test_webhook(webhook_id):
    return jsonify({'success': True, 'message': 'Test sent'})


# ============= Metrics =============
@app.route('/metrics', methods=['GET'])
def metrics():
    return "# No metrics yet\n", 200, {'Content-Type': 'text/plain'}


if __name__ == '__main__':
    print("🚀 AI Digest Backend API Server")
    print("📍 Running on http://localhost:5000")
    print("📚 API endpoints: /api/*")
    print("❤️  Health check: /health")
    print("🔐 Default credentials: admin / admin")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
