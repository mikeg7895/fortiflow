from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"
    login_url = reverse_lazy("custom-login")
    redirect_field_name = "next"
