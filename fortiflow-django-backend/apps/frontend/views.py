from core.utils import JWTTemplateAuthMixin
from django.views.generic import TemplateView

class DashboardView(JWTTemplateAuthMixin, TemplateView):
    template_name = "dashboard/index.html"

class LoginView(TemplateView):
    template_name = "auth/login.html"

class UsersView(JWTTemplateAuthMixin, TemplateView):
    template_name = "users/show.html"
    
