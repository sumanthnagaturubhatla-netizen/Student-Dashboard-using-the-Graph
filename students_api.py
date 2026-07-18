from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import json
import logging

from .jwt_utils import JWTHandler
from .students_models import RefreshToken

logger = logging.getLogger(__name__)


def get_jwt_handler():
    """Get JWT handler instance with Django settings."""
    from django.conf import settings
    return JWTHandler(settings.SECRET_KEY)


@require_http_methods(["POST"])
def api_login(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({'error': 'Username and password required'}, status=400)
        
        user = authenticate(username=username, password=password)
        if not user:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
        
        # Generate tokens
        jwt_handler = get_jwt_handler()
        access_token = jwt_handler.generate_access_token(user.id, user.username)
        refresh_token_str = jwt_handler.generate_refresh_token()
        
        # Store refresh token in database
        expires_at = timezone.now() + timedelta(days=7)
        refresh_token = RefreshToken.objects.create(
            user=user,
            token=refresh_token_str,
            expires_at=expires_at
        )
        
        return JsonResponse({
            'success': True,
            'access_token': access_token,
            'refresh_token': refresh_token_str,
            'user_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
        }, status=200)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return JsonResponse({'error': 'Login failed'}, status=500)


@require_http_methods(["POST"])
def api_refresh(request):
    try:
        data = json.loads(request.body)
        refresh_token_str = data.get('refresh_token')
        
        if not refresh_token_str:
            return JsonResponse({'error': 'Refresh token required'}, status=400)
        
        # Validate refresh token exists and is valid
        try:
            refresh_token = RefreshToken.objects.get(token=refresh_token_str)
        except RefreshToken.DoesNotExist:
            return JsonResponse({'error': 'Invalid refresh token'}, status=401)
        
        if not refresh_token.is_valid():
            return JsonResponse({'error': 'Refresh token expired or revoked'}, status=401)
        
        # Generate new access token
        jwt_handler = get_jwt_handler()
        user = refresh_token.user
        access_token = jwt_handler.generate_access_token(user.id, user.username)
        
        return JsonResponse({
            'success': True,
            'access_token': access_token,
            'user_id': user.id,
            'username': user.username,
        }, status=200)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Refresh token error: {str(e)}")
        return JsonResponse({'error': 'Token refresh failed'}, status=500)


@require_http_methods(["POST"])
def api_logout(request):    
    try:
        data = json.loads(request.body)
        refresh_token_str = data.get('refresh_token')
        
        if refresh_token_str:
            try:
                refresh_token = RefreshToken.objects.get(token=refresh_token_str)
                refresh_token.is_revoked = True
                refresh_token.save()
            except RefreshToken.DoesNotExist:
                pass  # Token doesn't exist, logout still succeeds
        
        return JsonResponse({'success': True, 'message': 'Logged out successfully'}, status=200)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return JsonResponse({'error': 'Logout failed'}, status=500)


@require_http_methods(["POST"])
def api_verify_token(request):
    try:
        token = None
        
        # Try to get token from Authorization header first
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        
        # Fall back to body data
        if not token:
            data = json.loads(request.body) if request.body else {}
            token = data.get('token')
        
        if not token:
            return JsonResponse({'error': 'Token required'}, status=400)
        
        jwt_handler = get_jwt_handler()
        is_valid, payload = jwt_handler.verify_token(token)
        
        if is_valid:
            return JsonResponse({
                'valid': True,
                'user_id': payload.get('user_id'),
                'username': payload.get('username'),
                'exp': payload.get('exp'),
                'iat': payload.get('iat'),
            }, status=200)
        else:
            return JsonResponse({'valid': False, 'error': 'Invalid or expired token'}, status=401)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return JsonResponse({'error': 'Token verification failed'}, status=500)


@require_http_methods(["GET"])
def api_verify_token_get(request):
    try:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return JsonResponse({'valid': False, 'error': 'Missing Authorization header'}, status=401)
        
        token = auth_header[7:]
        jwt_handler = get_jwt_handler()
        is_valid, payload = jwt_handler.verify_token(token)
        
        if is_valid:
            return JsonResponse({
                'valid': True,
                'user_id': payload.get('user_id'),
                'username': payload.get('username'),
                'exp': payload.get('exp'),
                'iat': payload.get('iat'),
            }, status=200)
        else:
            return JsonResponse({'valid': False, 'error': 'Invalid or expired token'}, status=401)
    
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return JsonResponse({'error': 'Token verification failed'}, status=500)
