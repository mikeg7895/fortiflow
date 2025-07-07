from django.urls import path
from apps.account.views import (
    CustomLoginView,
    UserListView,
    UserCreateView,
    UserEditView,
    UserDeleteView,
)
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="custom-login"),
    path("logout/", LogoutView.as_view(next_page="custom-login"), name="logout"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("create/", UserCreateView.as_view(), name="user-create"),
    path("edit/<int:pk>/", UserEditView.as_view(), name="user-edit"),
    path("delete/<int:pk>/", UserDeleteView.as_view(), name="user-delete"),
]