from django.contrib import admin
from apps.portfolio.models import Portfolio, Debtor, Obligation

admin.site.register(Portfolio)
admin.site.register(Debtor)
admin.site.register(Obligation)
