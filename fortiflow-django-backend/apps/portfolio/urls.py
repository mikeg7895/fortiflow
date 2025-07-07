from django.urls import path
from apps.portfolio.views import PortfolioListView

urlpatterns = [
    path("<int:pk>/", PortfolioListView.as_view(), name="portfolio-list"),
]
    