from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from apps.portfolio.models import Portfolio, Obligation, Debtor
from apps.management.models import Assignment, Management, Program
from apps.client.models import Client, Contract

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"
    login_url = reverse_lazy("custom-login")
    redirect_field_name = "next"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tenant = self.request.user.tenant
        today = timezone.now().date()
        
        # Estadísticas principales usando relaciones existentes correctamente
        context.update(self.get_portfolio_stats(tenant, today))
        context.update(self.get_collection_stats(tenant, today))
        context.update(self.get_management_stats(tenant, today))
        context.update(self.get_recent_activities(tenant))
        context.update(self.get_chart_data(tenant, today))
        
        return context
    
    def get_portfolio_stats(self, tenant, today):
        """Estadísticas de portfolios y obligaciones usando relaciones existentes"""
        
        # Total de portfolios activos
        active_portfolios = Portfolio.objects.filter(
            contract__client__tenant=tenant,
            status='active'
        ).count()
        
        # Total de obligaciones y montos
        obligations_qs = Obligation.objects.filter(
            portfolio__contract__client__tenant=tenant
        )
        
        obligations_stats = obligations_qs.aggregate(
            total_amount=Sum('amount'),
            total_balance=Sum('balance'),
            total_obligations=Count('id')
        )
        
        # Contar deudores únicos usando la relación correcta
        total_debtors = Debtor.objects.filter(
            obligations__portfolio__contract__client__tenant=tenant
        ).distinct().count()
        
        # Manejar valores None
        total_amount = obligations_stats['total_amount'] or 0
        total_balance = obligations_stats['total_balance'] or 0
        total_obligations = obligations_stats['total_obligations'] or 0
        
        # Cartera vencida
        overdue_stats = obligations_qs.filter(
            expiration_date__lt=today,
            balance__gt=0
        ).aggregate(
            overdue_amount=Sum('balance'),
            overdue_count=Count('id')
        )
        
        overdue_amount = overdue_stats['overdue_amount'] or 0
        overdue_count = overdue_stats['overdue_count'] or 0
        
        # Cartera por vencer (próximos 30 días)
        upcoming_stats = obligations_qs.filter(
            expiration_date__range=[today, today + timedelta(days=30)],
            balance__gt=0
        ).aggregate(
            upcoming_amount=Sum('balance'),
            upcoming_count=Count('id')
        )
        
        upcoming_amount = upcoming_stats['upcoming_amount'] or 0
        upcoming_count = upcoming_stats['upcoming_count'] or 0
        
        # Porcentaje de cartera vencida
        if total_balance > 0:
            overdue_percentage = round((overdue_amount / total_balance) * 100, 2)
        else:
            overdue_percentage = 0
        
        return {
            'active_portfolios': active_portfolios,
            'total_amount': total_amount,
            'total_balance': total_balance,
            'total_obligations': total_obligations,
            'total_debtors': total_debtors,
            'overdue_amount': overdue_amount,
            'overdue_count': overdue_count,
            'upcoming_amount': upcoming_amount,
            'upcoming_count': upcoming_count,
            'overdue_percentage': overdue_percentage,
        }
    
    def get_collection_stats(self, tenant, today):
        """Estadísticas de cobranza"""
        
        # Estadísticas por tipo de cartera
        portfolio_type_stats = list(Obligation.objects.filter(
            portfolio__contract__client__tenant=tenant
        ).values('portfolio_type').annotate(
            count=Count('id'),
            total_amount=Sum('amount'),
            total_balance=Sum('balance')
        ).order_by('portfolio_type'))
        
        # Limpiar valores None y agregar nombres legibles
        for stat in portfolio_type_stats:
            stat['total_amount'] = stat['total_amount'] or 0
            stat['total_balance'] = stat['total_balance'] or 0
            # Agregar nombre legible del tipo
            if stat['portfolio_type'] == 'ADMINISTRATIVE':
                stat['type_display'] = 'Administrative'
            elif stat['portfolio_type'] == 'PRELEGAL':
                stat['type_display'] = 'Pre-legal'
            elif stat['portfolio_type'] == 'LEGAL':
                stat['type_display'] = 'Legal'
            else:
                stat['type_display'] = stat['portfolio_type']
        
        # Promedio de días en mora
        avg_delinquency = Obligation.objects.filter(
            portfolio__contract__client__tenant=tenant,
            balance__gt=0
        ).aggregate(avg_days=Avg('days_delinquency'))['avg_days'] or 0
        
        # Recuperación del mes actual (asumiendo que balance = 0 significa pagado)
        current_month = today.replace(day=1)
        monthly_collections = Obligation.objects.filter(
            portfolio__contract__client__tenant=tenant,
            date_amount__gte=current_month,
            balance=0
        ).aggregate(
            recovered_amount=Sum('amount'),
            recovered_count=Count('id')
        )
        
        recovered_amount = monthly_collections['recovered_amount'] or 0
        recovered_count = monthly_collections['recovered_count'] or 0
        
        return {
            'portfolio_type_stats': portfolio_type_stats,
            'avg_delinquency_days': round(avg_delinquency, 1),
            'monthly_recovered_amount': recovered_amount,
            'monthly_recovered_count': recovered_count,
        }
    
    def get_management_stats(self, tenant, today):
        """Estadísticas de gestión y programas"""
        
        # Programas activos
        active_programs = Program.objects.filter(
            supervisor__tenant=tenant,
            is_finished=False
        ).count()
        
        # Asignaciones totales y por agente
        assignments_qs = Assignment.objects.filter(
            program__supervisor__tenant=tenant
        )
        
        assignments_stats = assignments_qs.aggregate(
            total_assignments=Count('id'),
            active_assignments=Count('id', filter=Q(program__is_finished=False))
        )
        
        # Gestiones del mes actual
        current_month = today.replace(day=1)
        monthly_managements = Management.objects.filter(
            assignment__program__supervisor__tenant=tenant,
            date_enagement__gte=current_month
        ).count()
        
        # Top agentes por asignaciones
        top_agents = list(assignments_qs.values(
            'agent__first_name', 'agent__last_name'
        ).annotate(
            assignment_count=Count('id')
        ).order_by('-assignment_count')[:5])
        
        return {
            'active_programs': active_programs,
            'total_assignments': assignments_stats['total_assignments'] or 0,
            'active_assignments': assignments_stats['active_assignments'] or 0,
            'monthly_managements': monthly_managements,
            'top_agents': top_agents,
        }
    
    def get_recent_activities(self, tenant):
        """Actividades recientes"""
        
        # Próximos vencimientos (próximos 7 días)
        upcoming_obligations = Obligation.objects.filter(
            portfolio__contract__client__tenant=tenant,
            expiration_date__range=[timezone.now().date(), timezone.now().date() + timedelta(days=7)],
            balance__gt=0
        ).select_related('debtor').order_by('expiration_date')[:10]
        
        return {
            'upcoming_obligations': upcoming_obligations,
        }
    
    def get_chart_data(self, tenant, today):
        """Datos para gráficos"""
        
        # Datos para gráfico de recuperación mensual (últimos 6 meses)
        chart_months = []
        recovered_data = []
        
        for i in range(6):
            month_date = today.replace(day=1) - timedelta(days=30*i)
            month_start = month_date.replace(day=1)
            if month_date.month == 12:
                month_end = month_date.replace(year=month_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = month_date.replace(month=month_date.month + 1, day=1) - timedelta(days=1)
            
            recovered_result = Obligation.objects.filter(
                portfolio__contract__client__tenant=tenant,
                date_amount__range=[month_start, month_end],
                balance=0
            ).aggregate(total=Sum('amount'))
            
            recovered = recovered_result['total'] or 0
            
            chart_months.insert(0, month_date.strftime('%B'))
            recovered_data.insert(0, float(recovered))
        
        # Datos para gráfico de cartera por tipo
        portfolio_chart_data = []
        portfolio_stats = Obligation.objects.filter(
            portfolio__contract__client__tenant=tenant
        ).values('portfolio_type').annotate(
            total=Sum('balance')
        )
        
        for stat in portfolio_stats:
            total_balance = stat['total'] or 0
            if total_balance > 0:
                if stat['portfolio_type'] == 'ADMINISTRATIVE':
                    name = 'Administrative'
                elif stat['portfolio_type'] == 'PRELEGAL':
                    name = 'Pre-legal'
                elif stat['portfolio_type'] == 'LEGAL':
                    name = 'Legal'
                else:
                    name = stat['portfolio_type']
                
                portfolio_chart_data.append({
                    'name': name,
                    'value': float(total_balance)
                })
        
        return {
            'chart_months': chart_months,
            'recovered_data': recovered_data,
            'portfolio_chart_data': portfolio_chart_data,
        }
