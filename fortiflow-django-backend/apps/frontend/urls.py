from django.urls import path
from apps.frontend.views import DashboardView, LoginView, UsersView

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("login/", LoginView.as_view(), name="login"),
    path("users/", UsersView.as_view(), name="users"),
]