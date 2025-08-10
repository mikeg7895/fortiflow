from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _


class SmartPaginationMixin:
    def get_pagination_context(self, page_obj, pages_around=2):
        """
        Genera el contexto para paginación inteligente
        
        Args:
            page_obj: El objeto página de Django
            pages_around: Número de páginas a mostrar alrededor de la actual (default: 2)
        """
        paginator = page_obj.paginator
        current_page = page_obj.number
        
        page_range_start = max(1, current_page - pages_around)
        page_range_end = min(paginator.num_pages, current_page + pages_around)
        
        total_pages_to_show = (pages_around * 2) + 1
        if page_range_end - page_range_start < total_pages_to_show - 1:
            if page_range_start == 1:
                page_range_end = min(paginator.num_pages, page_range_start + total_pages_to_show - 1)
            else:
                page_range_start = max(1, page_range_end - total_pages_to_show + 1)
        
        return {
            'custom_page_range': range(page_range_start, page_range_end + 1),
            'show_first': page_range_start > 1,
            'show_last': page_range_end < paginator.num_pages,
            'show_first_ellipsis': page_range_start > 2,
            'show_last_ellipsis': page_range_end < paginator.num_pages - 1,
        }
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if context.get('is_paginated'):
            page_obj = context['page_obj']
            pagination_context = self.get_pagination_context(page_obj)
            context.update(pagination_context)
        
        return context


class HTMXResponseMixin:
    """
    Mixin para vistas que manejan requests HTMX con Sweet Alerts centralizados
    """
    success_message = None
    error_message = None
    
    def get_success_message(self):
        """Obtiene el mensaje de éxito para esta vista"""
        if self.success_message:
            return self.success_message
        
        # Generar mensaje automático basado en la acción
        model_name = getattr(self.model, '_meta', None)
        if model_name:
            verbose_name = model_name.verbose_name.lower()
            
            if hasattr(self, 'object') and self.object and self.object.pk:
                return f"El {verbose_name} ha sido actualizado exitosamente."
            else:
                return f"El {verbose_name} ha sido creado exitosamente."
        
        return "Operación realizada exitosamente."
    
    def get_error_message(self):
        """Obtiene el mensaje de error para esta vista"""
        if self.error_message:
            return self.error_message
        return "Ha ocurrido un error al procesar la solicitud."
    
    def form_valid(self, form):
        """Maneja el form válido con respuesta HTMX"""
        response = super().form_valid(form)
        
        if self.request.headers.get('HX-Request'):
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': 'closeModal',
                    'X-Success-Message': self.get_success_message(),
                    'X-Entity-Type': self.model._meta.model_name if hasattr(self, 'model') else 'unknown',
                    'X-Action-Type': 'create' if not (hasattr(self, 'object') and self.object.pk) else 'update'
                }
            )
        return response
    
    def form_invalid(self, form):
        """Maneja el form inválido con respuesta HTMX"""
        response = super().form_invalid(form)
        
        if self.request.headers.get('HX-Request'):
            # Para formularios inválidos, retornamos el formulario con errores
            # pero también podemos enviar un header de error si es necesario
            response['X-Error-Message'] = self.get_error_message()
        
        return response


class HTMXDeleteMixin:
    """
    Mixin específico para vistas de eliminación con HTMX
    """
    delete_success_message = None
    
    def get_delete_success_message(self):
        if self.delete_success_message:
            return self.delete_success_message
            
        model_name = getattr(self.model, '_meta', None)
        if model_name:
            verbose_name = model_name.verbose_name.lower()
            return f"El {verbose_name} ha sido eliminado exitosamente."
        
        return "Elemento eliminado exitosamente."
    
    def delete(self, request, *args, **kwargs):
        """Maneja la eliminación con respuesta HTMX"""
        response = super().delete(request, *args, **kwargs)
        
        if request.headers.get('HX-Request'):
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': 'closeModal',
                    'X-Success-Message': self.get_delete_success_message(),
                    'X-Entity-Type': self.model._meta.model_name if hasattr(self, 'model') else 'unknown',
                    'X-Action-Type': 'delete'
                }
            )
        return response