# --- Management Edit View ---
from django.urls import reverse
from .models import Management
from .forms import ManagementForm
from django.views.generic import UpdateView, DeleteView, ListView, CreateView
from django.http import HttpResponse
from django.urls import reverse_lazy
from .models import Program, Assignment, Management
from .forms import ProgramForm, AssignmentForm
from core.mixins import SmartPaginationMixin
from django.contrib.auth.mixins import LoginRequiredMixin


class ManagementListView(LoginRequiredMixin, SmartPaginationMixin, ListView):
    model = Management
    context_object_name = 'managements'
    paginate_by = 10

    def get_queryset(self):
        assignment_id = self.kwargs.get('assignment_id')
        queryset = super().get_queryset().filter(assignment_id=assignment_id)
        accion = self.request.GET.get('accion', '').strip()
        contacto = self.request.GET.get('contacto', '').strip()
        telefono = self.request.GET.get('telefono', '').strip()
        if accion:
            queryset = queryset.filter(action__icontains=accion)
        if contacto:
            queryset = queryset.filter(contact__icontains=contacto)
        if telefono:
            queryset = queryset.filter(phone__icontains=telefono)
        return queryset.order_by('-id')

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ["managements/partials/management_list.html"]
        return ["managements/show.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import Assignment
        context['assignment'] = Assignment.objects.get(pk=self.kwargs.get('assignment_id'))
        context['request'] = self.request
        return context

class ManagementCreateView(LoginRequiredMixin, CreateView):
    model = Management
    form_class = ManagementForm

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ["managements/partials/management_create.html"]
        return ["managements/management_form.html"]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # No se requiere lógica extra, pero aquí puedes pasar datos si lo necesitas
        return kwargs

    def form_valid(self, form):
        form.instance.assignment_id = self.kwargs.get('assignment_id')
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            return HttpResponse(
                '',
                status=204,
                headers={
                    'HX-Trigger': 'managementCreated, reload-table',
                    'HX-Reswap': 'none',
                    'HX-Retarget': 'body'
                }
            )
        return response

    def get_success_url(self):
        return reverse_lazy('management-list', kwargs={'assignment_id': self.kwargs.get('assignment_id')})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import Assignment
        context['assignment'] = Assignment.objects.get(pk=self.kwargs.get('assignment_id'))
        return context

class ManagementEditView(LoginRequiredMixin, UpdateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # No modificar initial, solo pasar la instancia
        return kwargs
    model = Management
    form_class = ManagementForm

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ["managements/partials/management_edit.html"]
        return ["managements/management_form.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignment'] = self.object.assignment
        context['request'] = self.request
        return context

    def get_success_url(self):
        return reverse('management-list', args=[self.object.assignment_id])

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            return HttpResponse(status=204)
        return response

# --- Management Delete View ---
class ManagementDeleteView(LoginRequiredMixin, DeleteView):
    model = Management

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ["managements/partials/management_delete.html"]
        return ["managements/management_confirm_delete.html"]

    def get_success_url(self):
        return reverse('management-list', args=[self.object.assignment_id])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        assignment_id = self.object.assignment_id
        response = super().delete(request, *args, **kwargs)
        if self.request.headers.get('HX-Request') or self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponse(status=204)
        return response
    
class ProgramEditView(LoginRequiredMixin, UpdateView):
    model = Program
    form_class = ProgramForm

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ["programs/partials/program_edit.html"]
        return ["programs/partials/program_form.html"]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            return HttpResponse(status=204, headers={'HX-Trigger': 'reload-table'})
        return response

    def get_success_url(self):
        return reverse_lazy('program-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class ProgramDeleteView(LoginRequiredMixin, DeleteView):
    model = Program

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        if self.request.headers.get('HX-Request'):
            return HttpResponse(status=204, headers={'HX-Trigger': 'reload-table'})
        return response

    def get_success_url(self):
        return reverse_lazy('program-list')



class ProgramListView(LoginRequiredMixin, SmartPaginationMixin, ListView):
    model = Program
    context_object_name = 'programs'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        titulo = self.request.GET.get('titulo', '').strip()
        if titulo:
            queryset = queryset.filter(title__icontains=titulo)
        # Si quieres filtrar por supervisor, descomenta la siguiente línea:
        # queryset = queryset.filter(supervisor=self.request.user)
        return queryset.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['request'] = self.request
        return context

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["programs/partials/program_list.html"]
        return ["programs/show.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Puedes agregar más contexto si es necesario
        return context

class ProgramCreateView(CreateView):
    model = Program
    form_class = ProgramForm
    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ["programs/partials/program_create.html"]
        return ["programs/partials/program_form.html"]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            from django.http import HttpResponse
            return HttpResponse(status=204, headers={'HX-Trigger': 'reload-table'})
        return response

    def get_success_url(self):
        return reverse_lazy('program-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class AssignmentListView(LoginRequiredMixin, SmartPaginationMixin, ListView):
    model = Assignment
    context_object_name = 'assignments'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        program_id = self.kwargs.get('program_id', None)
        if program_id:
            queryset = queryset.filter(program_id=program_id)
        programa = self.request.GET.get('programa', '').strip()
        agente = self.request.GET.get('agente', '').strip()
        deudor = self.request.GET.get('deudor', '').strip()
        if programa:
            queryset = queryset.filter(program__title__icontains=programa)
        if agente:
            queryset = queryset.filter(agent__username__icontains=agente)
        if deudor:
            queryset = queryset.filter(debtor__name__icontains=deudor)
        return queryset.order_by('-id')

    def get_template_names(self):
        program_id = self.kwargs.get('program_id', None)
        if program_id:
            if self.request.headers.get("HX-Request"):
                return ["assignments/partials/assignment_list.html"]
            return ["assignments/show.html"]
        if self.request.headers.get("HX-Request"):
            return ["assignments/partials/assignment_list_general.html"]
        return ["assignments/show_general.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['request'] = self.request
        program_id = self.kwargs.get('program_id', None)
        if program_id:
            from .models import Program
            context['program'] = Program.objects.get(pk=program_id)
        else:
            context['program'] = None
        return context

class AssignmentCreateView(LoginRequiredMixin, CreateView):
    model = Assignment
    form_class = AssignmentForm
    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ["assignments/partials/assignment_create.html"]
        return ["assignments/partials/assignment_form.html"]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        program_id = self.kwargs.get('program_id', None)
        if program_id is not None:
            from django.shortcuts import get_object_or_404
            kwargs['program'] = get_object_or_404(Program, pk=program_id)
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            # Cierra el modal y recarga la tabla
            return HttpResponse(
                '',
                status=204,
                headers={
                    'HX-Trigger': 'assignmentCreated, reload-table',
                    'HX-Reswap': 'none',
                    'HX-Retarget': 'body'
                }
            )
        return response

    def get_success_url(self):
        program_id = self.kwargs.get('program_id', None)
        if program_id:
            return reverse_lazy('assignment-list-program', kwargs={'program_id': program_id})
        return reverse_lazy('assignment-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        program_id = self.kwargs.get('program_id', None)
        if program_id:
            from .models import Program
            context['program'] = Program.objects.get(pk=program_id)
        else:
            context['program'] = None
        return context

class AssignmentEditView(LoginRequiredMixin, UpdateView):
    model = Assignment
    form_class = AssignmentForm

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ["assignments/partials/assignment_edit.html"]
        return ["assignments/partials/assignment_form.html"]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        program_id = self.kwargs.get('program_id', None)
        if program_id is not None:
            from django.shortcuts import get_object_or_404
            kwargs['program'] = get_object_or_404(Program, pk=program_id)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        program_id = self.kwargs.get('program_id', None)
        if program_id is not None:
            from .models import Program
            context['program'] = Program.objects.get(pk=program_id)
        else:
            assignment = self.get_object()
            context['program'] = assignment.program if assignment and assignment.program_id else None
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            return HttpResponse(status=204, headers={'HX-Trigger': 'reload-table'})
        return response

    def get_success_url(self):
        return reverse_lazy('assignment-list')

class AssignmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Assignment
    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ["assignments/partials/assignment_delete.html"]
        return ["assignments/partials/assignment_confirm_delete.html"]

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        # Support both HTMX and fetch/X-Requested-With AJAX
        if (
            self.request.headers.get('HX-Request') or
            self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        ):
            return HttpResponse(status=204, headers={'HX-Trigger': 'reload-table'})
        return response

    def get_success_url(self):
        return reverse_lazy('assignment-list')
