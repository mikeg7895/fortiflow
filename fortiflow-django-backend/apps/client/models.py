from django.db import models
from apps.account.models import Tenant


class Client(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="client_logo/", null=True, blank=True)

    tenants = models.ManyToManyField(Tenant, through="Contract", related_name="clients")

    def __str__(self):
        return self.name


class Contract(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now=True)
    end_date = models.DateField(null=True, blank=True)