from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import HttpResponseRedirect

class JWTTemplateAuthMixin:
    def dispatch(self, request, *args, **kwargs):
        jwt_authenticator = JWTAuthentication()
        try:
            user_auth_tuple = jwt_authenticator.authenticate(request)
            if user_auth_tuple is not None:
                request.user, _ = user_auth_tuple
                return super().dispatch(request, *args, **kwargs)
        except (InvalidToken, TokenError):
            pass
        return HttpResponseRedirect('/login/')
