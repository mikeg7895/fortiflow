from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, TokenError
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

class RefreshTokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')

        if access_token:
            try:
                AccessToken(access_token)
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
            except TokenError:
                if refresh_token:
                    try:
                        refresh = RefreshToken(refresh_token)
                        new_access = refresh.access_token
                        request.META['HTTP_AUTHORIZATION'] = f'Bearer {new_access}'
                        request.new_access_token = str(new_access)
                    except TokenError:
                        pass
        return None

    def process_response(self, request, response):
        if hasattr(request, 'new_access_token'):
            response.set_cookie(
                key='access_token',
                value=request.new_access_token,
                httponly=True,
                secure=True,
                samesite='Lax',
                max_age=60*60
            )
        return response
