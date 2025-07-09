from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView
from django.views import View
from django.http import HttpResponse
from django.urls import reverse_lazy
from core.mixins import SmartPaginationMixin
from apps.client.models import Contract
from apps.client.models import Client
from apps.portfolio.models import Portfolio
from apps.portfolio.forms import PortfolioForm

class PortfolioListView(LoginRequiredMixin, SmartPaginationMixin, ListView):
    model = Portfolio
    context_object_name = "portfolios"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()

        pk = self.kwargs.get('pk', None)
        client_id = self.request.GET.get('cliente_id', None)
        contract_id = self.request.GET.get('contrato_id', None)

        if not self.request.user.is_superuser:
            queryset = queryset.filter(contract__client__tenant=self.request.user.tenant)

        if pk:
            queryset = queryset.filter(contract=pk)

        if client_id:
            queryset = queryset.filter(contract__client_id=client_id)

        if contract_id:
            queryset = queryset.filter(contract_id=contract_id)

        return queryset.order_by('-date_created')

    def get_template_names(self):
        pk = self.kwargs.get('pk', None)
        if pk:
            if self.request.headers.get("HX-Request"):
                return ["portfolio/partials/portfolio_list.html"]
            return ["portfolio/show.html"]
        if self.request.headers.get("HX-Request"):
            return ["portfolio/partials/portfolio_list_general.html"]
        return ["portfolio/show_general.html"]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk', None)
        selected_client_id = self.request.GET.get('cliente_id', None)
        selected_contract_id = self.request.GET.get('contrato_id', None)
        
        if pk:
            context['contract'] = Contract.objects.get(pk=pk)
        else:
            context['clients'] = Client.objects.filter(tenant=self.request.user.tenant)
            context['contracts'] = Contract.objects.filter(client__tenant=self.request.user.tenant)
            context['selected_client_id'] = selected_client_id
            context['selected_contract_id'] = selected_contract_id
        return context


class PortfolioCreateView(LoginRequiredMixin, CreateView):
    model = Portfolio
    form_class = PortfolioForm
    template_name = "portfolio/partials/portfolio_create.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['contract'] = Contract.objects.get(pk=self.kwargs.get('pk'))
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            return HttpResponse(
                status=204,
                headers={'HX-Trigger': 'portfolioCreated'}
            )
        return response
    
    def get_success_url(self):
        return reverse_lazy('portfolio-list', kwargs={'pk': self.kwargs.get('pk')})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contract'] = Contract.objects.get(pk=self.kwargs.get('pk'))
        return context


class PortfolioEditView(LoginRequiredMixin, UpdateView):
    model = Portfolio
    form_class = PortfolioForm
    template_name = "portfolio/partials/portfolio_edit.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['contract'] = Contract.objects.get(pk=self.kwargs.get('contract_id'))
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            return HttpResponse(
                status=204,
                headers={'HX-Trigger': 'portfolioCreated'}
            )
        return response
    
    def get_success_url(self):
        return reverse_lazy('portfolio-list', kwargs={'pk': self.kwargs.get('pk')})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contract'] = Contract.objects.get(pk=self.kwargs.get('contract_id'))
        return context
        

class PortfolioDeleteView(LoginRequiredMixin, View):
    def delete(self, request, pk, *args, **kwargs):
        try:
            portfolio = Portfolio.objects.get(pk=pk)
            try:
                os.remove(portfolio.logo.path)
            except:
                pass
            portfolio.delete()
            return HttpResponse(status=204, headers={'HX-Trigger': 'portfolioDeleted'})
        except Portfolio.DoesNotExist:
            return HttpResponse(status=404)
    
    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() != 'delete':
            return HttpResponseNotAllowed(['DELETE'])
        return super().dispatch(request, *args, **kwargs)
