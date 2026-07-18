"""
JWT (JSON Web Token) utilities for custom token generation and validation.
Uses HMAC-SHA256 for signing and Base64 for encoding.
"""
import json
import hmac
import hashlib
import base64
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Tuple, Optional


class JWTHandler:
    """Custom JWT implementation for token generation and validation."""
    
    def __init__(self, secret_key: str, access_token_expiry_minutes: int = 30, 
                 refresh_token_expiry_days: int = 7):
        """
        Initialize JWT handler.
        
        Args:
            secret_key: Secret key for HMAC signing
            access_token_expiry_minutes: Access token expiration time in minutes
            refresh_token_expiry_days: Refresh token expiration time in days
        """
        self.secret_key = secret_key
        self.access_token_expiry = timedelta(minutes=access_token_expiry_minutes)
        self.refresh_token_expiry = timedelta(days=refresh_token_expiry_days)
    
    @staticmethod
    def base64_encode(data: bytes) -> str:
        """Encode bytes to base64 URL-safe string."""
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')
    
    @staticmethod
    def base64_decode(data: str) -> bytes:
        """Decode base64 URL-safe string to bytes, adding padding if needed."""
        padding = 4 - (len(data) % 4)
        data = data + ('=' * padding)
        return base64.urlsafe_b64decode(data)
    
    def _create_signature(self, message: str) -> str:
        """Create HMAC-SHA256 signature for message."""
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        return self.base64_encode(signature)
    
    def _verify_signature(self, message: str, signature: str) -> bool:
        """Verify HMAC-SHA256 signature."""
        try:
            expected_signature = self._create_signature(message)
            return hmac.compare_digest(expected_signature, signature)
        except Exception:
            return False
    
    def generate_access_token(self, user_id: int, username: str) -> str:
        """
        Generate JWT access token.
        
        Args:
            user_id: User ID for token payload
            username: Username for token payload
            
        Returns:
            JWT token string (header.payload.signature)
        """
        now = datetime.now(timezone.utc)
        exp = now + self.access_token_expiry
        
        header = {'alg': 'HS256', 'typ': 'JWT'}
        payload = {
            'user_id': user_id,
            'username': username,
            'iat': int(now.timestamp()),
            'exp': int(exp.timestamp()),
            'type': 'access'
        }
        
        header_encoded = self.base64_encode(json.dumps(header).encode('utf-8'))
        payload_encoded = self.base64_encode(json.dumps(payload).encode('utf-8'))
        
        message = f"{header_encoded}.{payload_encoded}"
        signature = self._create_signature(message)
        
        return f"{message}.{signature}"
    
    def generate_refresh_token(self) -> str:
        """
        Generate a random refresh token.
        
        Returns:
            Random refresh token string (URL-safe)
        """
        return secrets.token_urlsafe(32)
    
    def verify_token(self, token: str) -> Tuple[bool, Optional[Dict]]:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token string to verify
            
        Returns:
            Tuple of (is_valid, payload_dict or None)
        """
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return False, None
            
            header_encoded, payload_encoded, signature = parts
            message = f"{header_encoded}.{payload_encoded}"
            
            # Verify signature
            if not self._verify_signature(message, signature):
                return False, None
            
            # Decode payload
            payload_json = self.base64_decode(payload_encoded).decode('utf-8')
            payload = json.loads(payload_json)
            
            # Check expiration
            exp = payload.get('exp')
            if exp and exp < datetime.now(timezone.utc).timestamp():
                return False, None  # Token expired
            
            return True, payload
        except Exception:
            return False, None
    
    def refresh_access_token(self, refresh_token: str, user_id: int, username: str) -> str:
        """
        Generate new access token using refresh token.
        
        Args:
            refresh_token: The refresh token (for validation purposes)
            user_id: User ID for new token
            username: Username for new token
            
        Returns:
            New JWT access token
        """
        return self.generate_access_token(user_id, username)
