from django.urls import path
from apps.client.views import ClientListView, ClientCreateView, ClientEditView, ClientDeleteView, ContractListView, ContractCreateView, ContractEditView, ContractDeleteView

urlpatterns = [
    path("", ClientListView.as_view(), name="client-list"),
    path("create/", ClientCreateView.as_view(), name="client-create"),
    path("edit/<int:pk>/", ClientEditView.as_view(), name="client-edit"),
    path("delete/<int:pk>/", ClientDeleteView.as_view(), name="client-delete"),
    path("contract/<int:pk>/", ContractListView.as_view(), name="contract-list"),
    path("contract/create/<int:pk>/", ContractCreateView.as_view(), name="contract-create"),
    path("contract/edit/<int:pk>/", ContractEditView.as_view(), name="contract-edit"),
    path("contract/delete/<int:pk>/", ContractDeleteView.as_view(), name="contract-delete"),
]