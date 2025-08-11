import os
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import View
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.urls import reverse_lazy
from core.mixins import HTMXResponseMixin, HTMXDeleteMixin, SmartPaginationMixin
from apps.client.models import Client, Contract
from apps.client.forms import CreateClientForm, CreateContractForm

class ClientListView(LoginRequiredMixin, SmartPaginationMixin, ListView):
    model = Client
    context_object_name = "clients"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            pass
        elif user.groups.filter(name__in=['Admin', 'Supervisor']).exists() and hasattr(user, 'tenant'):
            queryset = queryset.filter(tenant=user.tenant)
        else:
            queryset = queryset.filter(pk=user.pk)
        
        # Filtros de búsqueda
        nombre = self.request.GET.get('nombre', '').strip()
        if nombre:
            queryset = queryset.filter(name__icontains=nombre)
            
        return queryset.order_by('-id')

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["clients/partials/client_list.html"]
        return ["clients/show.html"]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['request'] = self.request
        return context


class ClientCreateView(LoginRequiredMixin, HTMXResponseMixin, CreateView):
    model = Client
    form_class = CreateClientForm
    template_name = "clients/partials/client_create.html"
    success_message = "El cliente ha sido creado exitosamente."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_success_url(self):
        return reverse_lazy('client-list')


class ClientEditView(LoginRequiredMixin, HTMXResponseMixin, UpdateView):
    model = Client
    template_name = "clients/partials/client_edit.html"
    form_class = CreateClientForm
    success_message = "El cliente ha sido actualizado exitosamente."
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_success_url(self):
        return reverse_lazy('client-list')


class ClientDeleteView(LoginRequiredMixin, HTMXDeleteMixin, DeleteView):
    model = Client
    delete_success_message = "El cliente ha sido eliminado exitosamente."
    
    def get_success_url(self):
        return reverse_lazy('client-list')
    
    def delete(self, request, *args, **kwargs):
        """Custom delete to handle logo file removal"""
        client = self.get_object()
        try:
            if client.logo:
                os.remove(client.logo.path)
        except:
            pass
        return super().delete(request, *args, **kwargs)


class ContractListView(LoginRequiredMixin, SmartPaginationMixin, ListView):
    model = Contract
    context_object_name = "contracts"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        pk = self.kwargs.get('pk')
        queryset = queryset.filter(client=pk)
        
        # Filtros de búsqueda
        fecha_inicio = self.request.GET.get('fecha_inicio', '').strip()
        fecha_fin = self.request.GET.get('fecha_fin', '').strip()
        
        if fecha_inicio:
            from datetime import datetime
            try:
                fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                queryset = queryset.filter(start_date__gte=fecha_inicio_obj)
            except ValueError:
                pass
        if fecha_fin:
            from datetime import datetime
            try:
                fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                queryset = queryset.filter(end_date__lte=fecha_fin_obj)
            except ValueError:
                pass
                
        return queryset.order_by('-id')

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["clients/partials/contract_list.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = Client.objects.get(pk=self.kwargs.get('pk'))
        context['request'] = self.request
        return context


class ContractCreateView(LoginRequiredMixin, HTMXResponseMixin, CreateView):
    model = Contract
    form_class = CreateContractForm
    template_name = "clients/partials/contract_create.html"
    success_message = "El contrato ha sido creado exitosamente."
    
    def get_success_url(self):
        return reverse_lazy('client-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = Client.objects.get(pk=self.kwargs.get('pk'))
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['client'] = Client.objects.get(pk=self.kwargs.get('pk'))
        return kwargs


class ContractEditView(LoginRequiredMixin, HTMXResponseMixin, UpdateView):
    model = Contract
    template_name = "clients/partials/contract_edit.html"
    form_class = CreateContractForm
    success_message = "El contrato ha sido editado exitosamente."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['client'] = self.object.client
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = self.object.client
        return context

    def get_success_url(self):
        return reverse_lazy('client-list')


class ContractDeleteView(LoginRequiredMixin, HTMXDeleteMixin, DeleteView):
    model = Contract
    delete_success_message = "El contrato ha sido eliminado exitosamente."
