from flask import Flask, jsonify, request, Response, send_from_directory
import threading
import asyncio
import os
import time
from pathlib import Path
from src.workflows.pipeline import Pipeline
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from .services import metrics as metrics_module
from .services.storage import get_storage
from .services.config import get_config_manager
from .services.auth import TokenManager, get_auth_manager, require_auth, AuthenticationError
from .services.webhooks import (
    get_webhook_manager,
    get_webhook_sender,
    WebhookType,
    WebhookManager,
)
from .services.scheduler import (
    start_scheduler,
    stop_scheduler,
    schedule_job,
    list_jobs as scheduler_list_jobs,
    remove_job as scheduler_remove_job,
)
from .logging_config import setup_logging, get_logger

# Initialize logging
setup_logging(log_level=os.getenv('LOG_LEVEL', 'INFO'))
logger = get_logger(__name__)

app = Flask(__name__)
storage = get_storage()
config_mgr = get_config_manager()
auth_mgr = get_auth_manager()
webhook_mgr = get_webhook_manager()
webhook_sender = get_webhook_sender()

logger.info("Flask server initialized", extra={"component": "server"})


# =================
# Authentication Endpoints
# =================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Login endpoint - generates JWT token.
    Default credentials: admin/admin (change in production!)
    """
    try:
        data = request.get_json() or {}
        username = data.get('username', '')
        password = data.get('password', '')

        # Simple default auth (CHANGE IN PRODUCTION!)
        if username == 'admin' and password == 'admin':
            token = TokenManager.generate_token(username)
            logger.info(
                f"User logged in: {username}",
                extra={"component": "server.auth", "user": username}
            )
            return jsonify({
                'token': token,
                'user': username,
                'expires_in_hours': int(os.getenv('JWT_EXPIRATION_HOURS', '24'))
            }), 200
        else:
            logger.warning(
                f"Failed login attempt",
                extra={"component": "server.auth", "user": username}
            )
            return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        logger.error(
            f"Login error: {str(e)}",
            extra={"component": "server.auth", "error": str(e)},
            exc_info=True
        )
        return jsonify({'error': 'Authentication failed'}), 500


@app.route('/api/auth/refresh', methods=['POST'])
@require_auth
def refresh_token():
    """Refresh JWT token (requires valid token)."""
    try:
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.split(' ')[1] if ' ' in auth_header else ''

        new_token = TokenManager.refresh_token(token)
        logger.info(
            f"Token refreshed for user: {request.user_id}",
            extra={"component": "server.auth", "user": request.user_id}
        )
        return jsonify({'token': new_token}), 200

    except AuthenticationError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        logger.error(
            f"Token refresh error: {str(e)}",
            extra={"component": "server.auth", "error": str(e)},
            exc_info=True
        )
        return jsonify({'error': 'Token refresh failed'}), 500


@app.route('/api/auth/keys', methods=['POST'])
@require_auth
def create_api_key():
    """Create new API key (requires authentication)."""
    try:
        data = request.get_json() or {}
        name = data.get('name', 'Unnamed Key')

        key_id, key_secret = auth_mgr.create_key(name, request.user_id)

        logger.info(
            f"API key created by user: {request.user_id}",
            extra={"component": "server.auth", "user": request.user_id}
        )
        return jsonify({
            'key_id': key_id,
            'key_secret': key_secret,
            'message': 'Save the key_secret - it will not be shown again!'
        }), 201

    except Exception as e:
        logger.error(
            f"API key creation error: {str(e)}",
            extra={"component": "server.auth", "error": str(e)},
            exc_info=True
        )
        return jsonify({'error': 'Key creation failed'}), 500


@app.route('/api/auth/keys', methods=['GET'])
@require_auth
def list_api_keys():
    """List API keys for current user."""
    try:
        keys = auth_mgr.list_keys(request.user_id)
        logger.debug(
            f"Listed {len(keys)} API keys for user: {request.user_id}",
            extra={"component": "server.auth", "user": request.user_id}
        )
        return jsonify({'keys': keys}), 200

    except Exception as e:
        logger.error(
            f"API key listing error: {str(e)}",
            extra={"component": "server.auth", "error": str(e)},
            exc_info=True
        )
        return jsonify({'error': 'Listing keys failed'}), 500


@app.route('/api/auth/keys/<key_id>', methods=['DELETE'])
@require_auth
def revoke_api_key(key_id):
    """Revoke (deactivate) API key."""
    try:
        success = auth_mgr.revoke_key(key_id)

        if not success:
            return jsonify({'error': 'Key not found'}), 404

        logger.info(
            f"API key revoked by user: {request.user_id}",
            extra={"component": "server.auth", "user": request.user_id, "key": key_id}
        )
        return jsonify({'revoked': True, 'key_id': key_id}), 200

    except Exception as e:
        logger.error(
            f"API key revocation error: {str(e)}",
            extra={"component": "server.auth", "error": str(e)},
            exc_info=True
        )
        return jsonify({'error': 'Revocation failed'}), 500


@app.route('/api/auth/verify', methods=['GET'])
@require_auth
def verify_token():
    """Verify current token is valid."""
    try:
        return jsonify({
            'valid': True,
            'user': request.user_id,
            'auth_type': request.auth_type
        }), 200

    except Exception as e:
        logger.error(
            f"Token verification error: {str(e)}",
            extra={"component": "server.auth", "error": str(e)},
            exc_info=True
        )
        return jsonify({'error': 'Verification failed'}), 500


# =================

@app.route('/')
def dashboard():
    """Serve the main dashboard."""
    try:
        static_dir = Path(__file__).parent.parent / 'static'
        return send_from_directory(str(static_dir), 'index.html')
    except Exception as e:
        logger.error(f"Failed to serve dashboard: {str(e)}", extra={"component": "server"})
        return jsonify({'error': 'Dashboard not available'}), 500


@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files (CSS, JavaScript)."""
    try:
        static_dir = Path(__file__).parent.parent / 'static'
        return send_from_directory(str(static_dir), path)
    except Exception as e:
        logger.debug(f"Static file not found: {path}", extra={"component": "server"})
        return jsonify({'error': 'File not found'}), 404


# =================

@app.route('/health')
def health():
    """Health check endpoint."""
    logger.debug("Health check endpoint called", extra={"component": "server.health"})
    return jsonify({'status': 'ok', 'timestamp': time.time()})


@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint."""
    logger.debug("Metrics endpoint called", extra={"component": "server.metrics"})
    data = generate_latest()
    return Response(data, mimetype=CONTENT_TYPE_LATEST)


@app.route('/info')
def info():
    """System information endpoint."""
    logger.debug("Info endpoint called", extra={"component": "server.info"})
    return jsonify({
        'name': 'AI Digest',
        'version': '0.1.0',
        'status': 'running',
        'timestamp': time.time(),
    })


# =================
# Digest Management Endpoints
# =================

@app.route('/api/digests', methods=['GET'])
@require_auth
def list_digests():
    """List recent digests with pagination."""
    try:
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)
        days = request.args.get('days', None, type=int)

        logger.debug(
            "Listing digests",
            extra={
                "limit": limit,
                "offset": offset,
                "days": days,
                "component": "server.digests",
            },
        )

        digests = storage.list_digests(limit=limit, offset=offset, days=days)

        return jsonify({
            'digests': [d.dict() for d in digests],
            'count': len(digests),
            'limit': limit,
            'offset': offset,
        }), 200

    except Exception as e:
        logger.error(
            f"Failed to list digests: {str(e)}",
            extra={"error": str(e), "component": "server.digests"},
            exc_info=True,
        )
        return jsonify({'error': str(e)}), 500


@app.route('/api/digests/<digest_id>', methods=['GET'])
@require_auth
def get_digest(digest_id):
    """Retrieve a specific digest by ID."""
    try:
        logger.debug(
            f"Retrieving digest: {digest_id}",
            extra={"digest_id": digest_id, "component": "server.digests"},
        )

        digest = storage.get_digest(digest_id)
        if digest is None:
            return jsonify({'error': 'Digest not found'}), 404

        return jsonify(digest.dict()), 200

    except Exception as e:
        logger.error(
            f"Failed to retrieve digest: {str(e)}",
            extra={"digest_id": digest_id, "error": str(e), "component": "server.digests"},
            exc_info=True,
        )
        return jsonify({'error': str(e)}), 500


@app.route('/api/digests/<digest_id>', methods=['DELETE'])
@require_auth
def delete_digest(digest_id):
    """Delete a digest."""
    try:
        logger.info(
            f"Deleting digest: {digest_id}",
            extra={"digest_id": digest_id, "component": "server.digests"},
        )

        success = storage.delete_digest(digest_id)
        if not success:
            return jsonify({'error': 'Digest not found'}), 404

        return jsonify({'deleted': True, 'digest_id': digest_id}), 200

    except Exception as e:
        logger.error(
            f"Failed to delete digest: {str(e)}",
            extra={"digest_id": digest_id, "error": str(e), "component": "server.digests"},
            exc_info=True,
        )
        return jsonify({'error': str(e)}), 500


# =================
# Pipeline Execution Endpoints
# =================

def run_pipeline_background(deliver: bool = False):
    """Run pipeline in background thread."""
    async def _run():
        logger.info(
            "Starting background pipeline run",
            extra={"deliver": deliver, "component": "server.pipeline"},
        )
        try:
            start_time = time.time()
            p = Pipeline()
            await p.run(deliver=deliver)
            duration = time.time() - start_time

            # Save digest metadata
            digest_id = time.strftime('%Y%m%d_%H%M%S')
            storage.save_digest([], digest_id=digest_id, duration_seconds=duration)

            logger.info(
                "Background pipeline run completed",
                extra={
                    "deliver": deliver,
                    "duration": duration,
                    "component": "server.pipeline",
                },
            )
        except Exception as e:
            logger.error(
                f"Background pipeline run failed: {str(e)}",
                extra={"deliver": deliver, "error": str(e), "component": "server.pipeline"},
                exc_info=True,
            )

    try:
        asyncio.run(_run())
    except Exception as e:
        logger.error(
            f"Pipeline background execution error: {str(e)}",
            extra={"error": str(e), "component": "server.pipeline"},
            exc_info=True,
        )


@app.route('/api/pipeline/run', methods=['POST'])
@require_auth
def trigger_pipeline():
    """Trigger immediate pipeline run (background)."""
    try:
        data = request.get_json() or {}
        deliver = data.get('deliver', False)

        logger.info(
            "Pipeline trigger endpoint called",
            extra={"deliver": deliver, "component": "server.pipeline"},
        )

        thread = threading.Thread(
            target=run_pipeline_background,
            args=(deliver,),
            daemon=True,
        )
        thread.start()

        return jsonify({'started': True, 'deliver': deliver}), 202

    except Exception as e:
        logger.error(
            f"Failed to trigger pipeline: {str(e)}",
            extra={"error": str(e), "component": "server.pipeline"},
            exc_info=True,
        )
        return jsonify({'error': str(e)}), 500


# =================
# Scheduler Management Endpoints
# =================

@app.route('/api/scheduler/status', methods=['GET'])
@require_auth
def scheduler_status():
    """Get scheduler status."""
    try:
        logger.debug("Checking scheduler status", extra={"component": "server.scheduler"})

        jobs = scheduler_list_jobs()

        return jsonify({
            'running': len(jobs) > 0,
            'jobs': jobs,
            'job_count': len(jobs),
        }), 200

    except Exception as e:
        logger.error(
            f"Failed to get scheduler status: {str(e)}",
            extra={"error": str(e), "component": "server.scheduler"},
            exc_info=True,
        )
        return jsonify({'error': str(e)}), 500


@app.route('/api/scheduler/start', methods=['POST'])
@require_auth
def scheduler_start():
    """Start the scheduler."""
    try:
        data = request.get_json() or {}
        deliver = data.get('deliver', True)
        hour = data.get('hour', 6)
        minute = data.get('minute', 0)

        logger.info(
            f"Starting scheduler at {hour:02d}:{minute:02d} UTC",
            extra={
                "deliver": deliver,
                "hour": hour,
                "minute": minute,
                "component": "server.scheduler",
            },
        )

        scheduler = start_scheduler(deliver=deliver)

        # Override if custom time
        if hour != 6 or minute != 0:
            try:
                scheduler.remove_job("daily_digest_6am")
            except:
                pass
            schedule_job("daily", hour=hour, minute=minute, deliver=deliver)

        jobs = scheduler_list_jobs()

        return jsonify({
            'started': True,
            'deliver': deliver,
            'jobs': jobs,
        }), 200

    except Exception as e:
        logger.error(
            f"Failed to start scheduler: {str(e)}",
            extra={"error": str(e), "component": "server.scheduler"},
            exc_info=True,
        )
        return jsonify({'error': str(e)}), 500


@app.route('/api/scheduler/stop', methods=['POST'])
@require_auth
def scheduler_stop():
    """Stop the scheduler."""
    try:
        logger.info("Stopping scheduler", extra={"component": "server.scheduler"})

        stop_scheduler()

        return jsonify({'stopped': True}), 200

    except Exception as e:
        logger.error(
            f"Failed to stop scheduler: {str(e)}",
            extra={"error": str(e), "component": "server.scheduler"},
            exc_info=True,
        )
        return jsonify({'error': str(e)}), 500


# =================
# Configuration Management Endpoints
# =================

@app.route('/api/config', methods=['GET'])
@require_auth
def get_config():
    """Get complete system configuration."""
    try:
        logger.debug("Getting system configuration", extra={"component": "server.config"})
        config = config_mgr.get_config()
        return jsonify(config.dict()), 200
    except Exception as e:
        logger.error(
            f"Failed to get configuration: {str(e)}",
            extra={"error": str(e), "component": "server.config"},
            exc_info=True,
        )
        return jsonify({'error': str(e)}), 500


@app.route('/api/config', methods=['POST'])
@require_auth
def update_config():
    """Update complete system configuration."""
    try:
        data = request.get_json() or {}
        logger.info(
            "Updating system configuration",
            extra={"component": "server.config"}
        )
        
        # Use update_config method which validates via Pydantic
        config_mgr.update_config(data)
        
        return jsonify(config_mgr.get_config().dict()), 200
    except Exception as e:
        logger.error(
            f"Failed to update configuration: {str(e)}",
            extra={"error": str(e), "component": "server.config"},
            exc_info=True,
        )
        return jsonify({'error': str(e)}), 400


@app.route('/api/config/adapters', methods=['GET'])
@require_auth
def get_adapters_config():
    """Get adapter configurations."""
    try:
        logger.debug("Getting adapter configurations", extra={"component": "server.config"})
        config = config_mgr.get_config()
        adapters = {name: adapter.dict() for name, adapter in config.adapters.items()}
        return jsonify({'adapters': adapters}), 200
    except Exception as e:
        logger.error(
            f"Failed to get adapter configuration: {str(e)}",
            extra={"error": str(e), "component": "server.config"},
            exc_info=True,
        )
        return jsonify({'error': str(e)}), 500


@app.route('/api/config/adapters/<adapter_name>', methods=['POST'])
@require_auth
def update_adapter_config(adapter_name):
    """Update specific adapter configuration."""
    try:
        data = request.get_json() or {}
        logger.info(
            f"Updating adapter configuration: {adapter_name}",
            extra={"adapter": adapter_name, "component": "server.config"}
        )
        
        config_mgr.set_adapter_config(adapter_name, data)
        
        config = config_mgr.get_config()
        adapter = config.adapters.get(adapter_name)
        return jsonify({'adapter': adapter.dict() if adapter else None}), 200
    except Exception as e:
        logger.error(
            f"Failed to update adapter configuration: {str(e)}",
            extra={"error": str(e), "component": "server.config"},
            exc_info=True,
        )
        return jsonify({'error': str(e)}), 400


@app.route('/api/config/delivery', methods=['GET'])
@require_auth
def get_delivery_config():
    """Get delivery configuration."""
    try:
        logger.debug("Getting delivery configuration", extra={"component": "server.config"})
        config = config_mgr.get_config()
        return jsonify(config.delivery.dict()), 200
    except Exception as e:
        logger.error(
            f"Failed to get delivery configuration: {str(e)}",
            extra={"error": str(e), "component": "server.config"},
            exc_info=True,
        )
        return jsonify({'error': str(e)}), 500


@app.route('/api/config/delivery', methods=['POST'])
@require_auth
def update_delivery_config():
    """Update delivery configuration."""
    try:
        data = request.get_json() or {}
        logger.info(
            "Updating delivery configuration",
            extra={"component": "server.config"}
        )
        
        config_mgr.set_delivery_config(data)
        
        config = config_mgr.get_config()
        return jsonify(config.delivery.dict()), 200
    except Exception as e:
        logger.error(
            f"Failed to update delivery configuration: {str(e)}",
            extra={"error": str(e), "component": "server.config"},
            exc_info=True,
        )
        return jsonify({'error': str(e)}), 400


@app.route('/api/config/scheduler', methods=['GET'])
@require_auth
def get_scheduler_config():
    """Get scheduler configuration."""
    try:
        logger.debug("Getting scheduler configuration", extra={"component": "server.config"})
        config = config_mgr.get_config()
        return jsonify(config.scheduler.dict()), 200
    except Exception as e:
        logger.error(
            f"Failed to get scheduler configuration: {str(e)}",
            extra={"error": str(e), "component": "server.config"},
            exc_info=True,
        )
        return jsonify({'error': str(e)}), 500


@app.route('/api/config/scheduler', methods=['POST'])
@require_auth
def update_scheduler_config():
    """Update scheduler configuration."""
    try:
        data = request.get_json() or {}
        logger.info(
            "Updating scheduler configuration",
            extra={"component": "server.config"}
        )
        
        config_mgr.set_scheduler_config(data)
        
        config = config_mgr.get_config()
        return jsonify(config.scheduler.dict()), 200
    except Exception as e:
        logger.error(
            f"Failed to update scheduler configuration: {str(e)}",
            extra={"error": str(e), "component": "server.config"},
            exc_info=True,
        )
        return jsonify({'error': str(e)}), 400


@app.route('/api/config/logging', methods=['GET'])
@require_auth
def get_logging_config():
    """Get logging configuration."""
    try:
        logger.debug("Getting logging configuration", extra={"component": "server.config"})
        config = config_mgr.get_config()
        return jsonify(config.logging.dict()), 200
    except Exception as e:
        logger.error(
            f"Failed to get logging configuration: {str(e)}",
            extra={"error": str(e), "component": "server.config"},
            exc_info=True,
        )
        return jsonify({'error': str(e)}), 500


@app.route('/api/config/logging', methods=['POST'])
@require_auth
def update_logging_config():
    """Update logging configuration."""
    try:
        data = request.get_json() or {}
        logger.info(
            "Updating logging configuration",
            extra={"component": "server.config"}
        )
        
        config_mgr.set_logging_config(data)
        
        config = config_mgr.get_config()
        return jsonify(config.logging.dict()), 200
    except Exception as e:
        logger.error(
            f"Failed to update logging configuration: {str(e)}",
            extra={"error": str(e), "component": "server.config"},
            exc_info=True,
        )
        return jsonify({'error': str(e)}), 400


# =================
# Webhook Endpoints
# =================

@app.route('/api/webhooks', methods=['GET'])
@require_auth
def list_webhooks():
    """List all webhooks."""
    try:
        webhooks = webhook_mgr.list_webhooks()
        logger.info(
            f"Retrieved {len(webhooks)} webhooks",
            extra={"component": "server.webhooks", "count": len(webhooks)}
        )
        return jsonify([webhook.to_dict() for webhook in webhooks]), 200
    except Exception as e:
        logger.error(
            f"Failed to list webhooks: {str(e)}",
            extra={"error": str(e), "component": "server.webhooks"},
            exc_info=True,
        )
        return jsonify({'error': str(e)}), 400


@app.route('/api/webhooks', methods=['POST'])
@require_auth
def create_webhook():
    """Create a new webhook."""
    try:
        data = request.get_json() or {}
        webhook_id = data.get('id')
        name = data.get('name')
        webhook_type = data.get('type')
        url = data.get('url')
        headers = data.get('headers', {})
        payload_template = data.get('payload_template')

        if not all([webhook_id, name, webhook_type, url]):
            return jsonify({'error': 'Missing required fields: id, name, type, url'}), 400

        try:
            webhook_type = WebhookType(webhook_type)
        except ValueError:
            return jsonify({'error': f'Invalid webhook type. Must be one of: {", ".join([t.value for t in WebhookType])}'}), 400

        webhook = webhook_mgr.create_webhook(
            webhook_id=webhook_id,
            name=name,
            type=webhook_type,
            url=url,
            headers=headers,
            payload_template=payload_template,
        )

        logger.info(
            f"Created webhook {webhook_id}",
            extra={"component": "server.webhooks", "webhook_id": webhook_id}
        )

        return jsonify(webhook.to_dict()), 201
    except ValueError as e:
        logger.warning(
            f"Webhook creation failed: {str(e)}",
            extra={"error": str(e), "component": "server.webhooks"}
        )
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(
            f"Failed to create webhook: {str(e)}",
            extra={"error": str(e), "component": "server.webhooks"},
            exc_info=True,
        )
        return jsonify({'error': str(e)}), 500


@app.route('/api/webhooks/<webhook_id>', methods=['GET'])
@require_auth
def get_webhook(webhook_id):
    """Get a specific webhook."""
    try:
        webhook = webhook_mgr.get_webhook(webhook_id)
        if not webhook:
            return jsonify({'error': 'Webhook not found'}), 404

        logger.debug(
            f"Retrieved webhook {webhook_id}",
            extra={"component": "server.webhooks", "webhook_id": webhook_id}
        )

        return jsonify(webhook.to_dict()), 200
    except Exception as e:
        logger.error(
            f"Failed to get webhook: {str(e)}",
            extra={"error": str(e), "component": "server.webhooks"},
            exc_info=True,
        )
        return jsonify({'error': str(e)}), 500


@app.route('/api/webhooks/<webhook_id>', methods=['PUT'])
@require_auth
def update_webhook(webhook_id):
    """Update a webhook."""
    try:
        data = request.get_json() or {}
        
        webhook = webhook_mgr.update_webhook(
            webhook_id=webhook_id,
            name=data.get('name'),
            url=data.get('url'),
            enabled=data.get('enabled'),
            headers=data.get('headers'),
            payload_template=data.get('payload_template'),
        )

        logger.info(
            f"Updated webhook {webhook_id}",
            extra={"component": "server.webhooks", "webhook_id": webhook_id}
        )

        return jsonify(webhook.to_dict()), 200
    except ValueError as e:
        logger.warning(
            f"Webhook update failed: {str(e)}",
            extra={"error": str(e), "component": "server.webhooks"}
        )
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(
            f"Failed to update webhook: {str(e)}",
            extra={"error": str(e), "component": "server.webhooks"},
            exc_info=True,
        )
        return jsonify({'error': str(e)}), 500


@app.route('/api/webhooks/<webhook_id>', methods=['DELETE'])
@require_auth
def delete_webhook(webhook_id):
    """Delete a webhook."""
    try:
        if not webhook_mgr.delete_webhook(webhook_id):
            return jsonify({'error': 'Webhook not found'}), 404

        logger.info(
            f"Deleted webhook {webhook_id}",
            extra={"component": "server.webhooks", "webhook_id": webhook_id}
        )

        return jsonify({'message': 'Webhook deleted'}), 200
    except Exception as e:
        logger.error(
            f"Failed to delete webhook: {str(e)}",
            extra={"error": str(e), "component": "server.webhooks"},
            exc_info=True,
        )
        return jsonify({'error': str(e)}), 500


@app.route('/api/webhooks/<webhook_id>/toggle', methods=['POST'])
@require_auth
def toggle_webhook(webhook_id):
    """Toggle webhook enabled/disabled status."""
    try:
        webhook = webhook_mgr.toggle_webhook(webhook_id)

        logger.info(
            f"Toggled webhook {webhook_id} to {webhook.enabled}",
            extra={"component": "server.webhooks", "webhook_id": webhook_id, "enabled": webhook.enabled}
        )

        return jsonify(webhook.to_dict()), 200
    except ValueError as e:
        logger.warning(
            f"Webhook toggle failed: {str(e)}",
            extra={"error": str(e), "component": "server.webhooks"}
        )
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(
            f"Failed to toggle webhook: {str(e)}",
            extra={"error": str(e), "component": "server.webhooks"},
            exc_info=True,
        )
        return jsonify({'error': str(e)}), 500


@app.route('/api/webhooks/<webhook_id>/test', methods=['POST'])
@require_auth
def test_webhook(webhook_id):
    """Test a webhook by sending a test notification."""
    try:
        webhook = webhook_mgr.get_webhook(webhook_id)
        if not webhook:
            return jsonify({'error': 'Webhook not found'}), 404

        # Send test notification
        success = asyncio.run(webhook_sender.send_to_webhook(
            webhook,
            title="Test Digest",
            content="This is a test notification from AI Digest",
            digest_id="test-digest"
        ))

        logger.info(
            f"Test webhook {webhook_id}: {'success' if success else 'failed'}",
            extra={"component": "server.webhooks", "webhook_id": webhook_id, "success": success}
        )

        return jsonify({
            'success': success,
            'message': 'Test notification sent successfully' if success else 'Test notification failed'
        }), 200 if success else 500
    except Exception as e:
        logger.error(
            f"Failed to test webhook: {str(e)}",
            extra={"error": str(e), "component": "server.webhooks"},
            exc_info=True,
        )
        return jsonify({'error': str(e)}), 500


# =================
# Error Handlers
# =================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(
        f"Internal server error: {str(error)}",
        extra={"error": str(error), "component": "server"},
        exc_info=True,
    )
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    logger.info(
        "Starting Flask server",
        extra={"host": "0.0.0.0", "port": 5000, "component": "server"},
    )
    app.run(host='0.0.0.0', port=5000)
