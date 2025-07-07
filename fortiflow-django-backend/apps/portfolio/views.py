from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from core.mixins import SmartPaginationMixin
from apps.client.models import Contract
from apps.portfolio.models import Portfolio

# Create your views here.
class PortfolioListView(LoginRequiredMixin, SmartPaginationMixin, ListView):
    model = Portfolio
    context_object_name = "portfolios"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        pk = self.kwargs.get('pk')
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(contract=pk)

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["portfolio/partials/portfolio_list.html"]
        return ["portfolio/show.html"]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contract'] = Contract.objects.get(pk=self.kwargs.get('pk'))
        return context