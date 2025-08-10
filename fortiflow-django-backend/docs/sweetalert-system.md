# Sistema Centralizado de Sweet Alerts - FortiFlow

Este sistema permite manejar todos los Sweet Alerts de la aplicación de manera centralizada, eliminando la duplicación de código y estandarizando las notificaciones.

## 🚀 Cómo Usar el Sistema

### 1. En las Vistas de Django

#### Opción A: Usar los Mixins (Recomendado)

```python
from core.mixins import HTMXResponseMixin, HTMXDeleteMixin

class MiVistaCrear(LoginRequiredMixin, HTMXResponseMixin, CreateView):
    model = MiModelo
    form_class = MiForm
    template_name = "mi_template.html"
    success_message = "El elemento ha sido creado exitosamente."  # Opcional

class MiVistaEditar(LoginRequiredMixin, HTMXResponseMixin, UpdateView):
    model = MiModelo
    form_class = MiForm
    template_name = "mi_template.html"
    success_message = "El elemento ha sido editado exitosamente."  # Opcional

class MiVistaEliminar(LoginRequiredMixin, HTMXDeleteMixin, DeleteView):
    model = MiModelo
    delete_success_message = "El elemento ha sido eliminado."  # Opcional
```

#### Opción B: Headers HTTP Manuales

```python
def form_valid(self, form):
    response = super().form_valid(form)
    if self.request.headers.get('HX-Request'):
        return HttpResponse(
            status=204,
            headers={
                'HX-Trigger': 'closeModal',
                'X-Success-Message': 'Mensaje personalizado aquí',
                'X-Entity-Type': 'mi_entidad',  # Opcional
                'X-Action-Type': 'create'       # Opcional
            }
        )
    return response
```

### 2. En los Templates

#### Formularios HTMX

Asegúrate de que tus formularios tengan los atributos necesarios:

```html
<form method="post" 
      hx-post="{% url 'mi-url' %}" 
      hx-target="#mi-target"
      id="mi-formulario"
      data-form-type="entidad-accion"
      class="space-y-4">
    {% csrf_token %}
    <!-- Campos del formulario -->
</form>
```

#### Llamadas JavaScript Manuales

Si necesitas mostrar Sweet Alerts manualmente:

```javascript
// Sweet Alert de éxito
showSuccess({
    title: 'Título personalizado',
    text: 'Mensaje de éxito',
    onSuccess: function() {
        // Callback opcional después del éxito
        console.log('Sweet Alert confirmado');
    }
});

// Sweet Alert de error
showError({
    title: 'Error',
    text: 'Mensaje de error'
});

// Sweet Alert de confirmación
showConfirm({
    title: '¿Estás seguro?',
    text: 'Esta acción no se puede deshacer.',
    confirmButtonText: 'Sí, continuar',
    cancelButtonText: 'Cancelar'
}).then((result) => {
    if (result.isConfirmed) {
        // Usuario confirmó
        console.log('Confirmado');
    }
});
```

## 🔧 Configuración del Sistema

### 1. Nombres de Entidades Automáticos

El sistema genera automáticamente los títulos basándose en el nombre del modelo:

```javascript
const entityNames = {
    'client': 'Cliente',
    'contract': 'Contrato',
    'user': 'Usuario',
    'portfolio': 'Portfolio',
    'debtor': 'Deudor',
    'obligation': 'Obligación',
    'assignment': 'Asignación',
    'program': 'Programa',
    'management': 'Gestión'
};
```

Para agregar nuevas entidades, edita `sweetalert-manager.js`.

### 2. Acciones Automáticas

```javascript
const actionNames = {
    'create': 'creado',
    'edit': 'editado',
    'update': 'actualizado',
    'delete': 'eliminado'
};
```

### 3. Personalizar Mensajes

#### En el Mixin de Django:

```python
class MiVista(HTMXResponseMixin, CreateView):
    success_message = "Mensaje completamente personalizado"
    
    def get_success_message(self):
        # Lógica personalizada para el mensaje
        if self.object.campo_especial:
            return "Mensaje especial para casos especiales"
        return super().get_success_message()
```

## 📋 Tipos de Formulario Recomendados

Usa el patrón `entidad-accion` en el atributo `data-form-type`:

- `client-create`
- `client-edit`
- `contract-create`
- `contract-edit`
- `user-create`
- `user-edit`
- `portfolio-create`
- `portfolio-edit`
- etc.

## 🎨 Personalización de Estilos

Los Sweet Alerts usan las siguientes clases CSS que puedes personalizar:

```css
.swal-global-success {
    /* Estilos para Sweet Alerts de éxito */
}

.swal-global-error {
    /* Estilos para Sweet Alerts de error */
}
```

## 🐛 Depuración

El sistema incluye logs de depuración. Abre las DevTools (F12) para ver:

```
htmx:afterOnLoad triggered: {
    status: 204,
    target: "modal-content",
    formId: "mi-formulario",
    formType: "client-create",
    url: "/clients/create/"
}
```

## 📝 Migración de Templates Existentes

### Antes:
```html
<script>
    document.body.addEventListener('htmx:afterOnLoad', function(evt) {
        if (evt.detail.xhr.status === 204) {
            Swal.fire('Éxito', 'Operación exitosa', 'success');
        }
    });
</script>
```

### Después:
```html
<!-- El script global se encarga automáticamente -->
<!-- Solo necesitas el data-form-type en el formulario -->
```

## 🚨 Consideraciones Importantes

1. **Headers HTTP**: El sistema funciona mejor con headers HTTP `X-Success-Message`
2. **Form Types**: Usa consistentemente el patrón `entidad-accion`
3. **Z-Index**: El sistema maneja automáticamente el z-index de los modales
4. **Múltiples Listeners**: Evita duplicar listeners `htmx:afterOnLoad` en templates individuales

## 📚 Ejemplos Completos

Ver los archivos de ejemplo en:
- `templates/clients/partials/contract_edit.html` (simplificado)
- `apps/client/views.py` (usando mixins)
- `static/js/sweetalert-manager.js` (lógica central)
