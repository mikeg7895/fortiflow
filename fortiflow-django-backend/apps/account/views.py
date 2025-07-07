from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import login
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from core.mixins import SmartPaginationMixin
from apps.account.forms import CustomLoginForm, CustomUserCreationForm, CustomUserEditForm
from apps.account.models import CustomUser


class CustomLoginView(LoginView):
    template_name = "auth/login.html"
    authentication_form = CustomLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        login(self.request, form.get_user())
        if self.request.headers.get("HX-Request"):
            return JsonResponse({"redirect": "/dashboard/"}) 
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get("HX-Request"):
            return render(self.request, self.template_name, {"form": form})
        return super().form_invalid()


class UserCreateView(LoginRequiredMixin, CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = "users/partials/user_create.html"
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            return HttpResponse(
                status=204,
                headers={'HX-Trigger': 'userCreated'}
            )
        return response
    
    def get_success_url(self):
        return reverse_lazy('user-list')


class UserListView(LoginRequiredMixin, SmartPaginationMixin, ListView):
    model = CustomUser
    context_object_name = "users"
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
            return ["users/partials/user_list.html"]
        return ["users/show.html"]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class UserEditView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserEditForm
    template_name = "users/partials/user_edit.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get("HX-Request"):
            return HttpResponse(status=204, headers={"HX-Trigger": "userUpdated"})
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse_lazy('user-list')


class UserDeleteView(LoginRequiredMixin, View):
    def delete(self, request, pk, *args, **kwargs):
        try:
            user = CustomUser.objects.get(pk=pk)
            user.delete()
            return HttpResponse(status=204, headers={'HX-Trigger': 'userDeleted'})
        except CustomUser.DoesNotExist:
            return HttpResponse(status=404)
    
    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() != 'delete':
            return HttpResponseNotAllowed(['DELETE'])
        return super().dispatch(request, *args, **kwargs)