"""
Authentication module for API security.
Provides JWT token generation, validation, and API key management.
"""

import jwt
import os
import secrets
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Tuple
from functools import wraps
from flask import request, jsonify, current_app
from ..logging_config import get_logger

logger = get_logger(__name__)

# Configuration
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
TOKEN_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))
API_KEYS_FILE = Path(os.getenv('API_KEYS_FILE', 'api_keys.json'))


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class TokenManager:
    """Manages JWT token generation and validation."""

    @staticmethod
    def generate_token(user_id: str, expires_in_hours: int = TOKEN_EXPIRATION_HOURS) -> str:
        """
        Generate JWT token for user.

        Args:
            user_id: User identifier
            expires_in_hours: Token expiration time in hours

        Returns:
            JWT token string
        """
        try:
            payload = {
                'user_id': user_id,
                'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
                'iat': datetime.utcnow(),
                'type': 'access'
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
            logger.info(
                f"Generated token for user: {user_id}",
                extra={"component": "auth", "user_id": user_id}
            )
            return token
        except Exception as e:
            logger.error(
                f"Failed to generate token: {str(e)}",
                extra={"component": "auth", "error": str(e)},
                exc_info=True
            )
            raise AuthenticationError(f"Token generation failed: {str(e)}")

    @staticmethod
    def validate_token(token: str) -> Dict:
        """
        Validate JWT token and return payload.

        Args:
            token: JWT token to validate

        Returns:
            Token payload (user_id, exp, iat, type)

        Raises:
            AuthenticationError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            logger.debug(
                f"Token validated for user: {payload.get('user_id')}",
                extra={"component": "auth"}
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning(
                "Token validation failed: expired",
                extra={"component": "auth"}
            )
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning(
                f"Token validation failed: {str(e)}",
                extra={"component": "auth", "error": str(e)}
            )
            raise AuthenticationError("Invalid token")
        except Exception as e:
            logger.error(
                f"Unexpected token validation error: {str(e)}",
                extra={"component": "auth", "error": str(e)},
                exc_info=True
            )
            raise AuthenticationError("Token validation failed")

    @staticmethod
    def refresh_token(token: str) -> str:
        """
        Refresh token if still valid.

        Args:
            token: Current JWT token

        Returns:
            New JWT token with extended expiration
        """
        try:
            payload = TokenManager.validate_token(token)
            user_id = payload.get('user_id')
            return TokenManager.generate_token(user_id)
        except AuthenticationError:
            raise


class APIKeyManager:
    """Manages API keys for non-interactive access."""

    def __init__(self, keys_file: Path = API_KEYS_FILE):
        """
        Initialize API key manager.

        Args:
            keys_file: Path to API keys JSON file
        """
        self.keys_file = keys_file
        self.keys = self._load_keys()
        logger.info(
            f"APIKeyManager initialized with {len(self.keys)} keys",
            extra={"component": "auth", "key_count": len(self.keys)}
        )

    def _load_keys(self) -> Dict[str, Dict]:
        """Load API keys from file."""
        try:
            if self.keys_file.exists():
                with open(self.keys_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(
                f"Failed to load API keys: {str(e)}",
                extra={"component": "auth", "error": str(e)},
                exc_info=True
            )
            return {}

    def _save_keys(self) -> None:
        """Save API keys to file."""
        try:
            self.keys_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.keys_file, 'w') as f:
                json.dump(self.keys, f, indent=2)
            logger.debug(
                "API keys saved to file",
                extra={"component": "auth"}
            )
        except Exception as e:
            logger.error(
                f"Failed to save API keys: {str(e)}",
                extra={"component": "auth", "error": str(e)},
                exc_info=True
            )

    def create_key(self, name: str, user_id: str = 'system') -> Tuple[str, str]:
        """
        Create new API key.

        Args:
            name: Key name/description
            user_id: Associated user ID

        Returns:
            Tuple of (key_id, key_secret) - secret only shown once!
        """
        try:
            key_id = f"key_{secrets.token_hex(8)}"
            key_secret = secrets.token_urlsafe(32)

            self.keys[key_id] = {
                'name': name,
                'user_id': user_id,
                'secret': key_secret,
                'created_at': datetime.utcnow().isoformat(),
                'last_used': None,
                'active': True
            }
            self._save_keys()

            logger.info(
                f"Created API key: {name}",
                extra={"component": "auth", "key_id": key_id, "user_id": user_id}
            )
            return key_id, key_secret
        except Exception as e:
            logger.error(
                f"Failed to create API key: {str(e)}",
                extra={"component": "auth", "error": str(e)},
                exc_info=True
            )
            raise AuthenticationError(f"Key creation failed: {str(e)}")

    def validate_key(self, key_id: str, key_secret: str) -> bool:
        """
        Validate API key.

        Args:
            key_id: Key identifier
            key_secret: Key secret

        Returns:
            True if valid, False otherwise
        """
        try:
            if key_id not in self.keys:
                logger.warning(
                    f"API key validation failed: key not found",
                    extra={"component": "auth", "key_id": key_id}
                )
                return False

            key_data = self.keys[key_id]

            if not key_data.get('active'):
                logger.warning(
                    f"API key validation failed: key inactive",
                    extra={"component": "auth", "key_id": key_id}
                )
                return False

            if key_data.get('secret') != key_secret:
                logger.warning(
                    f"API key validation failed: secret mismatch",
                    extra={"component": "auth", "key_id": key_id}
                )
                return False

            # Update last used time
            self.keys[key_id]['last_used'] = datetime.utcnow().isoformat()
            self._save_keys()

            logger.debug(
                f"API key validated successfully",
                extra={"component": "auth", "key_id": key_id}
            )
            return True
        except Exception as e:
            logger.error(
                f"API key validation error: {str(e)}",
                extra={"component": "auth", "error": str(e)},
                exc_info=True
            )
            return False

    def list_keys(self, user_id: str = None) -> list:
        """
        List API keys (without secrets).

        Args:
            user_id: Filter by user ID (optional)

        Returns:
            List of key information (secrets excluded)
        """
        keys_list = []
        for key_id, key_data in self.keys.items():
            if user_id and key_data.get('user_id') != user_id:
                continue

            keys_list.append({
                'key_id': key_id,
                'name': key_data.get('name'),
                'user_id': key_data.get('user_id'),
                'created_at': key_data.get('created_at'),
                'last_used': key_data.get('last_used'),
                'active': key_data.get('active')
            })
        return keys_list

    def revoke_key(self, key_id: str) -> bool:
        """
        Revoke (deactivate) API key.

        Args:
            key_id: Key identifier

        Returns:
            True if revoked, False if not found
        """
        try:
            if key_id not in self.keys:
                logger.warning(
                    f"API key revoke failed: key not found",
                    extra={"component": "auth", "key_id": key_id}
                )
                return False

            self.keys[key_id]['active'] = False
            self._save_keys()

            logger.info(
                f"API key revoked: {key_id}",
                extra={"component": "auth", "key_id": key_id}
            )
            return True
        except Exception as e:
            logger.error(
                f"Failed to revoke API key: {str(e)}",
                extra={"component": "auth", "error": str(e)},
                exc_info=True
            )
            return False

    def delete_key(self, key_id: str) -> bool:
        """
        Permanently delete API key.

        Args:
            key_id: Key identifier

        Returns:
            True if deleted, False if not found
        """
        try:
            if key_id not in self.keys:
                return False

            del self.keys[key_id]
            self._save_keys()

            logger.info(
                f"API key deleted: {key_id}",
                extra={"component": "auth", "key_id": key_id}
            )
            return True
        except Exception as e:
            logger.error(
                f"Failed to delete API key: {str(e)}",
                extra={"component": "auth", "error": str(e)},
                exc_info=True
            )
            return False


def get_auth_manager() -> APIKeyManager:
    """Get global API key manager instance (singleton)."""
    if not hasattr(get_auth_manager, '_instance'):
        get_auth_manager._instance = APIKeyManager()
    return get_auth_manager._instance


def require_auth(f):
    """
    Decorator to require authentication for Flask routes.
    Supports both JWT tokens and API keys.

    Usage:
        @app.route('/api/protected', methods=['GET'])
        @require_auth
        def protected_endpoint():
            return jsonify({'data': 'secret'})

    Authorization header format:
        - JWT: Authorization: Bearer <token>
        - API Key: Authorization: ApiKey <key_id>:<key_secret>
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Get authorization header
            auth_header = request.headers.get('Authorization', '')

            if not auth_header:
                logger.warning(
                    "Request without authorization header",
                    extra={"component": "auth", "path": request.path}
                )
                return jsonify({'error': 'Missing authorization header'}), 401

            parts = auth_header.split(' ', 1)
            if len(parts) != 2:
                return jsonify({'error': 'Invalid authorization header format'}), 401

            auth_type, auth_data = parts

            # JWT Token authentication
            if auth_type.lower() == 'bearer':
                try:
                    payload = TokenManager.validate_token(auth_data)
                    # Store in request context
                    request.user_id = payload.get('user_id')
                    request.auth_type = 'token'
                    logger.debug(
                        f"Request authenticated via JWT token",
                        extra={"component": "auth", "user_id": request.user_id, "path": request.path}
                    )
                    return f(*args, **kwargs)
                except AuthenticationError as e:
                    return jsonify({'error': str(e)}), 401

            # API Key authentication
            elif auth_type.lower() == 'apikey':
                try:
                    key_id, key_secret = auth_data.split(':', 1)
                    auth_mgr = get_auth_manager()

                    if not auth_mgr.validate_key(key_id, key_secret):
                        return jsonify({'error': 'Invalid API key'}), 401

                    # Store in request context
                    request.user_id = auth_mgr.keys[key_id].get('user_id')
                    request.auth_type = 'api_key'
                    logger.debug(
                        f"Request authenticated via API key",
                        extra={"component": "auth", "key_id": key_id, "path": request.path}
                    )
                    return f(*args, **kwargs)
                except (ValueError, KeyError):
                    return jsonify({'error': 'Invalid API key format'}), 401

            else:
                return jsonify({'error': 'Unsupported authorization type'}), 401

        except Exception as e:
            logger.error(
                f"Authentication error: {str(e)}",
                extra={"component": "auth", "error": str(e)},
                exc_info=True
            )
            return jsonify({'error': 'Authentication failed'}), 500

    return decorated_function
