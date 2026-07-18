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
        '/students/api/login/',
        '/students/api/register/',
        '/students/api/verify/',
        '/students/api/verify-get/',
        '/students/api/refresh/',
        '/students/api/logout/',
        '/students/api/chart-scores/',
        '/students/api/chart-attendance/',
        '/students/api/chart-students/',
        '/students/api/calendar-data/',
        '/students/api/student-count/',
        '/students/api/toggle-student/',
    ]
    
    def process_request(self, request):
        """Process request to check JWT token in Authorization header."""
        # Check if path is exempt
        if any(request.path.startswith(path) for path in self.EXEMPT_PATHS):
            return None
        
        # Check if path is an API endpoint
        if not request.path.startswith('/students/api/'):
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
