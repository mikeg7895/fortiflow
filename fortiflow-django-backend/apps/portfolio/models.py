from django.db import models
from apps.client.models import Contract


class Portfolio(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=255)
    date_created = models.DateField(auto_now=True)
    date_updated = models.DateField(auto_now=True)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name="portfolios")

    def __str__(self):
        return self.name
    

class Deptor(models.Model):
    name = models.CharField(max_length=255)
    identification = models.BigIntegerField()
    number_phone = models.BigIntegerField()
    address = models.CharField(max_length=255)
    email = models.EmailField()

    def __str__(self):
        return self.name


class Obligation(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="obligations")
    deptor = models.ForeignKey(Deptor, on_delete=models.CASCADE, related_name="obligations")
    portfolio_type = models.CharField(max_length=255)
    credit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date_amount = models.DateField()
    expiration_date = models.DateField()
    days_delinquency = models.IntegerField()
    status = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    interest = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.portfolio.name