from django import forms
from apps.portfolio.models import Portfolio


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
        