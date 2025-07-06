from django.urls import path
from apps.account.views import (
    CustomLoginView,
    UserListView,
    UserCreateView,
    UserEditView,
    UserDeleteView,
)

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="custom-login"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("create/", UserCreateView.as_view(), name="user-create"),
    path("edit/<int:pk>/", UserEditView.as_view(), name="user-edit"),
    path("delete/<int:pk>/", UserDeleteView.as_view(), name="user-delete"),
]