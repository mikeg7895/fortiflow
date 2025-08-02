from django.db import models
from apps.client.models import Contract
from django.db.models import Sum
from django.utils import timezone
from django.db.models import Q

class Portfolio(models.Model):
    STATUS_CHOICES = (
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
    )
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=255, choices=STATUS_CHOICES)
    date_created = models.DateField(auto_now=True)
    date_updated = models.DateField(auto_now=True)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name="portfolios")

    def __str__(self):
        return self.name

    @property
    def debtors_count(self):
        return self.obligations.values('debtor').distinct().count()
    
    @property
    def delinquency_percentage(self):
        today = timezone.now().date()

        total = self.obligations.aggregate(
            total=Sum("amount")
        )["total"] or 0

        vencido = self.obligations.filter(
            Q(expiration_date__lt=today) & Q(balance__gt=0)
        ).aggregate(
            vencido=Sum("amount")
        )["vencido"] or 0

        if total == 0:
            return 0

        return round((vencido / total) * 100, 2)
    

class Debtor(models.Model):
    name = models.CharField(max_length=255)
    identification = models.CharField(max_length=100)
    number_phone = models.CharField(max_length=20)  
    address = models.CharField(max_length=255)
    email = models.EmailField()

    def __str__(self):
        return self.name

class PortfolioType(models.TextChoices):
    ADMINISTRATIVE = 'ADMINISTRATIVE', 'Administrative portfolio'
    PRELEGAL = 'PRELEGAL', 'Pre-legal portfolio'
    LEGAL = 'LEGAL', 'Legal portfolio'
    
class Obligation(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="obligations")
    debtor = models.ForeignKey(Debtor, on_delete=models.CASCADE, related_name="obligations")
    portfolio_type = models.CharField(
        max_length=20,
        choices=PortfolioType.choices,
        default=PortfolioType.ADMINISTRATIVE,
    )

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