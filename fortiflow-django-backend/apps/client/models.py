from django.db import models
from apps.account.models import Tenant


class Client(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="client_logo/", null=True, blank=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="clients")

    class Meta:
        unique_together = ('name', 'tenant')
        

    def __str__(self):
        return self.name


class Contract(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.client.name} - {self.start_date} - {self.end_date}"
    