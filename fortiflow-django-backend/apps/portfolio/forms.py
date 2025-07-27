
from django import forms
from .models import Obligation
from apps.portfolio.models import Portfolio, Debtor

class ObligationForm(forms.ModelForm):

    class Meta:
        model = Obligation
        exclude = ['portfolio']
        widgets = {
            'date_amount': forms.DateInput(attrs={'type': 'date', 'placeholder': 'Fecha de desembolso', 'class': 'input input-bordered w-full'}),
            'expiration_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'Fecha de vencimiento', 'class': 'input input-bordered w-full'}),
        }

    def __init__(self, *args, **kwargs):
        portfolio_id = kwargs.pop('portfolio_id', None)
        super().__init__(*args, **kwargs)
        # Solo mostrar deudores válidos (puedes personalizar el filtro si lo deseas)
        self.fields['debtor'].queryset = Debtor.objects.all()

        # Add modern classes to all fields
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'select select-bordered w-full'
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'textarea textarea-bordered w-full'
            elif isinstance(field.widget, forms.DateInput):
                # Already set in widgets, skip
                continue
            else:
                field.widget.attrs['class'] = 'input input-bordered w-full'


class PortfolioForm(forms.ModelForm):
    name = forms.CharField(
        label='Nombre',
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Nombre del portfolio',
        }),
        error_messages={
            'required': 'El nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 255 caracteres.',
        }
    )

    description = forms.CharField(
        label='Descripción',
        widget=forms.Textarea(attrs={
            'class': 'textarea textarea-bordered w-full',
            'placeholder': 'Descripción del portfolio',
        }),
        error_messages={
            'required': 'La descripción es obligatoria.',
        }
    )

    status = forms.ChoiceField(
        label='Estado',
        widget=forms.Select(attrs={
            'class': 'select select-bordered w-full',
        }),
        choices=Portfolio.STATUS_CHOICES,
        error_messages={
            'required': 'El estado es obligatorio.',
        }
    )

    class Meta:
        model = Portfolio
        fields = ('name', 'description', 'status')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.contract = kwargs.pop('contract', None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data['name']
        tenant = self.request.user.tenant if hasattr(self.request.user, 'tenant') else None
        if tenant and Portfolio.objects.filter(name=name, contract__client__tenant=tenant).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe un portfolio con este nombre en su organización.")
            
        return name

    def save(self, commit=True):
        portfolio = super().save(commit=False)
        portfolio.contract = self.contract
        if commit:
            portfolio.save()
        return portfolio
    
class DebtorForm(forms.ModelForm):
    name = forms.CharField(
        label='Nombre del Deudor',
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Nombre del deudor',
        }),
        error_messages={
            'required': 'El nombre del deudor es obligatorio.',
            'max_length': 'El nombre no puede tener más de 255 caracteres.',
        }
    )
            
    identification = forms.CharField(
        label='Identificación',
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Identificación del deudor',
        }),
        error_messages={
            'required': 'La identificación es obligatoria.',
        }
    )
        
    number_phone = forms.CharField(
        label='Número de Teléfono',
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Número de teléfono del deudor',
        }),
        error_messages={
            'required': 'El número de teléfono es obligatorio.',
        }
    )
        
    address = forms.CharField(
        label='Dirección',
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Dirección del deudor',
        }),
        error_messages={
            'required': 'La dirección es obligatoria.',
        }
    )
        
    email = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Correo electrónico del deudor',
        }),
        error_messages={
            'required': 'El correo electrónico es obligatorio.',
            'invalid': 'Ingrese un correo electrónico válido.',
        }
    )
        
    class Meta:
        model = Debtor
        fields = ['name', 'identification', 'number_phone', 'address', 'email']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean_identification(self):
        identification = self.cleaned_data['identification']
        if Debtor.objects.filter(identification=identification).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe un deudor con esta identificación.")
        return identification

    def clean_email(self):
        email = self.cleaned_data['email']
        if Debtor.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe un deudor con este correo electrónico.")
        return email

    def save(self, commit=True):
        debtor = super().save(commit=False)
        debtor.tenant = self.request.user.tenant
        if commit:
            debtor.save()
        return debtor

