"""
Middleware for JWT authentication.
Validates JWT tokens from Authorization header and attaches user to request.
"""
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware to handle JWT token authentication.
    Looks for 'Authorization: Bearer <token>' header and validates it.
    """
    
    # Paths that don't require JWT authentication
    EXEMPT_PATHS = [
        '/admin/',
        '/static/',
        '/api/login/',
        '/api/register/',
        '/calendar_data/',
        '/api/verify/',  # Verify endpoint doesn't require auth
        '/api/refresh/',  # Refresh endpoint doesn't require auth
        '/api/logout/',  # Logout endpoint doesn't require auth (uses refresh token)
        '/api/chart-scores/',
        '/api/chart-attendance/',
        '/api/chart-students/',
        '/api/calendar-data/',
        '/api/student-count/',
    ]
    
    def process_request(self, request):
        """Process request to check JWT token in Authorization header."""
        # Check if path is exempt
        if any(request.path.startswith(path) for path in self.EXEMPT_PATHS):
            return None
        
        # Check if path is an API endpoint
        if not request.path.startswith('/api/'):
            return None
        
        # Get Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Missing or invalid Authorization header'}, status=401)
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Validate JWT token
        from .jwt_utils import JWTHandler
        from django.conf import settings
        
        jwt_handler = JWTHandler(settings.SECRET_KEY)
        is_valid, payload = jwt_handler.verify_token(token)
        
        if not is_valid:
            return JsonResponse({'error': 'Invalid or expired token'}, status=401)
        
        # Attach user to request
        try:
            user = User.objects.get(id=payload['user_id'])
            request.user = user
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=401)
        
        return None
