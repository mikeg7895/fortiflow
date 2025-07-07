import os
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView
from django.views.generic.edit import View
from django.http import HttpResponse
from django.urls import reverse_lazy
from core.mixins import SmartPaginationMixin
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
            return queryset
        if user.groups.filter(name__in=['Admin', 'Supervisor']).exists() and hasattr(user, 'tenant'):
            return queryset.filter(tenant=user.tenant)
        return queryset.filter(pk=user.pk)

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["clients/partials/client_list.html"]
        return ["clients/show.html"]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = CreateClientForm
    template_name = "clients/partials/client_create.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            return HttpResponse(
                status=204,
                headers={'HX-Trigger': 'clientCreated'}
            )
        return response
    
    def get_success_url(self):
        return reverse_lazy('client-list')


class ClientEditView(LoginRequiredMixin, UpdateView):
    model = Client
    template_name = "clients/partials/client_edit.html"
    form_class = CreateClientForm

    def form_valid(self, form):
        super().form_valid(form)
        if self.request.headers.get("HX-Request"):
            return HttpResponse(status=204, headers={"HX-Trigger": "clientUpdated"})
        return HttpResponseRedirect(self.get_success_url())
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_success_url(self):
        return reverse_lazy('client-list')


class ClientDeleteView(LoginRequiredMixin, View):
    def delete(self, request, pk, *args, **kwargs):
        try:
            client = Client.objects.get(pk=pk)
            try:
                os.remove(client.logo.path)
            except:
                pass
            client.delete()
            return HttpResponse(status=204, headers={'HX-Trigger': 'clientDeleted'})
        except Client.DoesNotExist:
            return HttpResponse(status=404)
    
    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() != 'delete':
            return HttpResponseNotAllowed(['DELETE'])
        return super().dispatch(request, *args, **kwargs)


class ContractListView(LoginRequiredMixin, SmartPaginationMixin, ListView):
    model = Contract
    context_object_name = "contracts"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        pk = self.kwargs.get('pk')
        return queryset.filter(client=pk)

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["clients/partials/contract_list.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = Client.objects.get(pk=self.kwargs.get('pk'))
        return context


class ContractCreateView(LoginRequiredMixin, CreateView):
    model = Contract
    form_class = CreateContractForm
    template_name = "clients/partials/contract_create.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            return HttpResponse(
                status=204,
                headers={'HX-Trigger': 'contractCreated'}
            )
        return response
    
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


class ContractEditView(LoginRequiredMixin, UpdateView):
    model = Contract
    template_name = "clients/partials/contract_edit.html"
    form_class = CreateContractForm

    def form_valid(self, form):
        super().form_valid(form)
        if self.request.headers.get("HX-Request"):
            return HttpResponse(status=204, headers={"HX-Trigger": "contractUpdated"})

    def get_success_url(self):
        return reverse_lazy('client-list')


class ContractDeleteView(LoginRequiredMixin, View):
    def delete(self, request, pk, *args, **kwargs):
        try:
            contract = Contract.objects.get(pk=pk)
            contract.delete()
            return HttpResponse(status=204, headers={'HX-Trigger': 'contractDeleted'})
        except Contract.DoesNotExist:
            return HttpResponse(status=404)
    
    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() != 'delete':
            return HttpResponseNotAllowed(['DELETE'])
        return super().dispatch(request, *args, **kwargs)
