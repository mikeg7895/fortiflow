import os
from django import forms
from django.utils.text import slugify
from datetime import datetime
from apps.client.models import Client, Contract


class CreateClientForm(forms.ModelForm):
    name = forms.CharField(
        label='Nombre',
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Nombre del cliente',
        }),
        error_messages={
            'required': 'El nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 255 caracteres.',
        }
    )

    logo = forms.ImageField(
        label='Logo',
        widget=forms.FileInput(attrs={
            'class': 'file-input file-input-bordered w-full',
            'placeholder': 'Logo del cliente',
            'accept': 'image/*',
        }),
        error_messages={
            'required': 'El logo es obligatorio.',
        }
    )

    class Meta:
        model = Client
        fields = ['name', 'logo']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data['name']
        tenant = self.request.user.tenant if hasattr(self.request.user, 'tenant') else None
        if tenant and Client.objects.filter(name=name, tenant=tenant).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe un cliente con este nombre en su organización.")
            
        return name

    def clean_logo(self):
        logo = self.cleaned_data.get('logo', None)
        if not logo:
            raise forms.ValidationError("El logo es obligatorio.")
        return logo
    
    def save(self, commit=True):
        client = super().save(commit=False)
        
        # Debug: Verificar que el request y user estén disponibles
        if not self.request:
            raise forms.ValidationError("Request no disponible en el formulario.")
        if not hasattr(self.request.user, 'tenant'):
            raise forms.ValidationError("El usuario no tiene un tenant asignado.")
        if not self.request.user.tenant:
            raise forms.ValidationError("El tenant del usuario es nulo.")
            
        client.tenant = self.request.user.tenant

        logo = self.cleaned_data.get('logo')
        
        old_logo = None
        if client.pk:
            try:
                old_client = Client.objects.get(pk=client.pk)
                old_logo = old_client.logo
            except Client.DoesNotExist:
                old_logo = None
        
        if logo:
            if old_logo and old_logo.name == logo.name:
                client.save()
                return client
            
            name, ext = os.path.splitext(logo.name)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            client_name_slug = slugify(client.name)
            new_filename = f"{client_name_slug}_{timestamp}{ext}"
            
            logo.name = new_filename
            client.logo = logo
            if old_logo:
                old_logo.delete()
        
        if commit:
            client.save()
        
        return client


class CreateContractForm(forms.ModelForm):
    start_date = forms.DateField(
        label='Fecha de inicio',
        widget=forms.DateInput(
            attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Fecha de inicio',
                'type': 'date',
            },
            format='%Y-%m-%d'
        ),
        input_formats=['%Y-%m-%d'],
        error_messages={
            'required': 'La fecha de inicio es obligatoria.',
        }
    )
    end_date = forms.DateField(
        label='Fecha de finalización',
        widget=forms.DateInput(
            attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Fecha de finalización',
                'type': 'date',
            },
            format='%Y-%m-%d'
        ),
        input_formats=['%Y-%m-%d'],
        required=False,
        error_messages={
            'required': 'La fecha de finalización es obligatoria.',
        }
    )
    
    class Meta:
        model = Contract
        fields = ['start_date', 'end_date']

    def __init__(self, *args, **kwargs):
        self.client = kwargs.pop('client', None)
        super().__init__(*args, **kwargs)
        
        # Solo aplicar restricciones para contratos nuevos
        if not self.instance or not self.instance.pk:
            self.fields['start_date'].widget.attrs['max'] = datetime.now().strftime('%Y-%m-%d')
            self.fields['end_date'].widget.attrs['min'] = datetime.now().strftime('%Y-%m-%d')

    def save(self, commit=True):
        contract = super().save(commit=False)
        if not contract.pk and self.client:
            contract.client = self.client
        if commit:
            contract.save()
        return contract

