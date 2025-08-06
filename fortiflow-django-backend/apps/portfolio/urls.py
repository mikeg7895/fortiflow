from django.urls import path
from apps.portfolio.views import PortfolioListView, PortfolioCreateView, PortfolioEditView, PortfolioDeleteView, DebtorListView, DebtorCreateView, DebtorEditView, DebtorDeleteView, ContractListByClientView, ObligationListView, ObligationCreateView, ObligationEditView, ObligationDeleteView

urlpatterns = [
    # Rutas de portafolios
    path("", PortfolioListView.as_view(), name="portfolio-list-general"),
    path("<int:pk>/", PortfolioListView.as_view(), name="portfolio-list"),
    path("create/<int:pk>", PortfolioCreateView.as_view(), name="portfolio-create"),
    path("contracts/by-client/", ContractListByClientView.as_view(), name="contracts-by-client"),
    path("edit/<int:pk>/<int:contract_id>", PortfolioEditView.as_view(), name="portfolio-edit"),
    path("delete/<int:pk>/", PortfolioDeleteView.as_view(), name="portfolio-delete"),

    # Rutas de obligaciones
    path("<int:portfolio_id>/obligations/", ObligationListView.as_view(), name="obligation-list"),
    path("<int:portfolio_id>/obligations/create/", ObligationCreateView.as_view(), name="obligation-create"),
    path("obligations/edit/<int:pk>/", ObligationEditView.as_view(), name="obligation-edit"),
    path("obligations/delete/<int:pk>/", ObligationDeleteView.as_view(), name="obligation-delete"),
    
    # Rutas de deudores
    path("debtors/", DebtorListView.as_view(), name="debtor-list"),
    path("debtors/<int:portfolio_id>/", DebtorListView.as_view(), name="debtor-list-portfolio"),
    path("debtors/create/", DebtorCreateView.as_view(), name="debtor-create"),
    path("debtors/edit/<int:pk>/", DebtorEditView.as_view(), name="debtor-edit"),
    path("debtors/delete/<int:pk>/", DebtorDeleteView.as_view(), name="debtor-delete"),
]
    