from django.urls import path
from apps.portfolio.views import PortfolioListView, PortfolioCreateView, PortfolioEditView, PortfolioDeleteView

urlpatterns = [
    path("", PortfolioListView.as_view(), name="portfolio-list-general"),
    path("<int:pk>/", PortfolioListView.as_view(), name="portfolio-list"),
    path("create/<int:pk>", PortfolioCreateView.as_view(), name="portfolio-create"),
    path("edit/<int:pk>/<int:contract_id>", PortfolioEditView.as_view(), name="portfolio-edit"),
    path("delete/<int:pk>/", PortfolioDeleteView.as_view(), name="portfolio-delete"),
]
    