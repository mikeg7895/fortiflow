from apps.portfolio.models import Obligation
from apps.portfolio.forms import ObligationForm
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView
from django.views import View
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.urls import reverse_lazy
from core.mixins import SmartPaginationMixin, HTMXResponseMixin, HTMXDeleteMixin
import os
from apps.client.models import Contract
from apps.client.models import Client
from apps.portfolio.models import Portfolio, Debtor
from apps.portfolio.forms import PortfolioForm, DebtorForm
from apps.portfolio.models import Portfolio
from django.views.decorators.http import require_GET
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string


class ObligationListView(LoginRequiredMixin, SmartPaginationMixin, ListView):
    model = Obligation
    context_object_name = "obligations"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        portfolio_id = self.kwargs.get('portfolio_id', None)
        if portfolio_id:
            queryset = queryset.filter(portfolio_id=portfolio_id)
        
        # Filtros de búsqueda
        deudor_nombre = self.request.GET.get('deudor_nombre', '').strip()
        tipo_portfolio = self.request.GET.get('tipo_portfolio', '').strip()
        estado = self.request.GET.get('estado', '').strip()
        
        if deudor_nombre:
            queryset = queryset.filter(debtor__name__icontains=deudor_nombre)
        if tipo_portfolio:
            queryset = queryset.filter(portfolio_type=tipo_portfolio)
        if estado:
            queryset = queryset.filter(status__icontains=estado)
            
        return queryset.select_related('debtor').order_by('-id')

    def get_template_names(self):
        portfolio_id = self.kwargs.get('portfolio_id', None)
        if portfolio_id:
            if self.request.headers.get("HX-Request"):
                return ["obligations/partials/obligation_list.html"]
            return ["obligations/show.html"]
        if self.request.headers.get("HX-Request"):
            return ["obligations/partials/obligation_list.html"]
        return ["obligations/show.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        portfolio_id = self.kwargs.get('portfolio_id', None)
        if portfolio_id:

            context['portfolio_id'] = portfolio_id
            try:
                context['portfolio'] = Portfolio.objects.get(pk=portfolio_id)
            except Portfolio.DoesNotExist:
                context['portfolio'] = None
        context['request'] = self.request
        return context

class ObligationCreateView(LoginRequiredMixin, HTMXResponseMixin, CreateView):
    model = Obligation
    form_class = ObligationForm
    success_message = "La obligación ha sido creada exitosamente."
    
    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ["obligations/partials/obligation_create.html"]
        return ["obligations/partials/obligation_form.html"]

    def form_valid(self, form):
        portfolio_id = self.kwargs.get('portfolio_id')
        form.instance.portfolio_id = portfolio_id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('obligation-list', kwargs={'portfolio_id': self.kwargs.get('portfolio_id')})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['portfolio_id'] = self.kwargs.get('portfolio_id')
        return context

class ObligationEditView(LoginRequiredMixin, HTMXResponseMixin, UpdateView):
    model = Obligation
    form_class = ObligationForm
    success_message = "La obligación ha sido actualizada exitosamente."
    
    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ["obligations/partials/obligation_edit.html"]
        return ["obligations/partials/obligation_form.html"]

    def get_success_url(self):
        return reverse('obligation-list', kwargs={'portfolio_id': self.object.portfolio_id})

class ObligationDeleteView(LoginRequiredMixin, HTMXDeleteMixin, DeleteView):
    model = Obligation
    delete_success_message = "La obligación ha sido eliminada exitosamente."
    
    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ["obligations/partials/obligation_delete.html"]
        return ["obligations/partials/obligation_confirm_delete.html"]

    def get_success_url(self):
        return reverse('obligation-list', kwargs={'portfolio_id': self.object.portfolio_id})

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
        
        # Filtros de búsqueda por nombre o descripción
        nombre = self.request.GET.get('nombre', '').strip()
        descripcion = self.request.GET.get('descripcion', '').strip()
        estado = self.request.GET.get('estado', '').strip()
        
        if nombre:
            queryset = queryset.filter(name__icontains=nombre)
        if descripcion:
            queryset = queryset.filter(description__icontains=descripcion)
        if estado:
            queryset = queryset.filter(status=estado)

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
            
            # Solo cargar contratos si hay un cliente seleccionado
            if selected_client_id:
                context['contracts'] = Contract.objects.filter(
                    client_id=selected_client_id, 
                    client__tenant=self.request.user.tenant
                )
            else:
                context['contracts'] = Contract.objects.none()
                
            context['selected_client_id'] = selected_client_id
            context['selected_contract_id'] = selected_contract_id
        
        context['request'] = self.request
        return context


class PortfolioCreateView(LoginRequiredMixin, HTMXResponseMixin, CreateView):
    model = Portfolio
    form_class = PortfolioForm
    template_name = "portfolio/partials/portfolio_create.html"
    success_message = "El portfolio ha sido creado exitosamente."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        contract_id = self.kwargs.get('pk')
        # Si hay contrato en la URL, úsalo; si no, busca en POST
        if contract_id:
            kwargs['contract'] = Contract.objects.get(pk=contract_id)
        else:
            contract_id_post = self.request.POST.get('contract')
            if contract_id_post:
                kwargs['contract'] = Contract.objects.get(pk=contract_id_post)
            else:
                kwargs['contract'] = None
        return kwargs

    def get_success_url(self):
        contract_id = self.kwargs.get('pk') or self.request.POST.get('contract')
        if contract_id:
            return reverse_lazy('portfolio-list', kwargs={'pk': contract_id})
        return reverse_lazy('portfolio-list-general')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contract_id = self.kwargs.get('pk')
        if contract_id:
            context['contract'] = Contract.objects.get(pk=contract_id)
        else:
            # Para el formulario general, pasar clientes
            context['clients'] = Client.objects.filter(tenant=self.request.user.tenant)
            context['contracts'] = []
        return context


@method_decorator(require_GET, name='dispatch')
class ContractListByClientView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        client_id = request.GET.get('client_id')
        if client_id:
            contracts = Contract.objects.filter(
                client_id=client_id, 
                client__tenant=request.user.tenant
            )
        else:
            contracts = Contract.objects.none()
        
        html = render_to_string('portfolio/partials/contract_options.html', {'contracts': contracts})
        return HttpResponse(html)


class PortfolioEditView(LoginRequiredMixin, HTMXResponseMixin, UpdateView):
    model = Portfolio
    form_class = PortfolioForm
    template_name = "portfolio/partials/portfolio_edit.html"
    success_message = "El portfolio ha sido actualizado exitosamente."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['contract'] = Contract.objects.get(pk=self.kwargs.get('contract_id'))
        return kwargs
    
    def get_success_url(self):
        return reverse_lazy('portfolio-list', kwargs={'pk': self.kwargs.get('pk')})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contract'] = Contract.objects.get(pk=self.kwargs.get('contract_id'))
        return context
        

class PortfolioDeleteView(LoginRequiredMixin, HTMXDeleteMixin, DeleteView):
    model = Portfolio
    delete_success_message = "El portfolio ha sido eliminado exitosamente."
    
    def delete(self, request, *args, **kwargs):
        """Custom delete to handle logo file removal"""
        portfolio = self.get_object()
        try:
            if portfolio.logo:
                os.remove(portfolio.logo.path)
        except:
            pass
        return super().delete(request, *args, **kwargs)

class DebtorListView(LoginRequiredMixin, SmartPaginationMixin, ListView):
    model = Debtor
    context_object_name = "debtors"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        portfolio_id = self.kwargs.get('portfolio_id', None)

        if portfolio_id:
            queryset = queryset.filter(obligations__portfolio_id=portfolio_id).distinct()

        nombre = self.request.GET.get('nombre', '').strip()
        cedula = self.request.GET.get('cedula', '').strip()
        if nombre:
            queryset = queryset.filter(name__icontains=nombre)
        if cedula:
            queryset = queryset.filter(identification__icontains=cedula)

        return queryset.order_by('name')

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["debtors/partials/debtor_list.html"]
        return ["debtors/show_general.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['request'] = self.request
        return context
    
class DebtorCreateView(LoginRequiredMixin, HTMXResponseMixin, CreateView):
    model = Debtor
    form_class = DebtorForm
    template_name = "debtors/partials/debtor_create.html"
    success_message = "El deudor ha sido creado exitosamente."
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_success_url(self):
        return reverse_lazy('debtor-list')

class DebtorEditView(LoginRequiredMixin, HTMXResponseMixin, UpdateView):
    model = Debtor
    form_class = DebtorForm
    template_name = "debtors/partials/debtor_edit.html"
    success_message = "El deudor ha sido actualizado exitosamente."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_success_url(self):
        return reverse_lazy('debtor-list')

class DebtorDeleteView(LoginRequiredMixin, HTMXDeleteMixin, DeleteView):
    model = Debtor
    success_message = "El deudor ha sido eliminado exitosamente."
    
    def get_success_url(self):
        return reverse_lazy('debtor-list')