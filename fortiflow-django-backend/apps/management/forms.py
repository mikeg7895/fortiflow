
from django import forms
from .models import Program, Assignment, Management
from apps.account.models import CustomUser
from apps.portfolio.models import Debtor


class ManagementForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        import datetime
        instance = kwargs.get('instance', None)
        # Solo poner initial si es nuevo (no edición)
        if instance is None or not getattr(instance, 'pk', None):
            if 'initial' not in kwargs:
                kwargs['initial'] = {}
            if 'date_enagement' not in kwargs['initial']:
                kwargs['initial']['date_enagement'] = datetime.date.today()
            super().__init__(*args, **kwargs)
        else:
            # Si es edición, no tocar initial, solo pasar a super
            super().__init__(*args, **kwargs)
    class Meta:
        model = Management
        fields = ['action', 'type_contact', 'effect', 'contact', 'phone', 'date_enagement', 'commitment', 'observation', 'next_management']
        widgets = {
            'action': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Acción'}),
            'type_contact': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Tipo de contacto'}),
            'effect': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Efecto'}),
            'contact': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Contacto'}),
            'phone': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Teléfono'}),
            'date_enagement': forms.DateInput(attrs={'type': 'date', 'class': 'input input-bordered w-full'}),
            'commitment': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Compromiso'}),
            'observation': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'placeholder': 'Observación'}),
            'next_management': forms.DateInput(attrs={'type': 'date', 'class': 'input input-bordered w-full'}),
        }


class ProgramForm(forms.ModelForm):
    title = forms.CharField(
        label='Título',
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Título del programa',
        }),
        error_messages={
            'required': 'El título es obligatorio.',
            'max_length': 'El título no puede tener más de 255 caracteres.',
        }
    )

    description = forms.CharField(
        label='Descripción',
        widget=forms.Textarea(attrs={
            'class': 'textarea textarea-bordered w-full',
            'placeholder': 'Descripción del programa',
        }),
        error_messages={
            'required': 'La descripción es obligatoria.',
        }
    )

    supervisor = forms.ModelChoiceField(
        label='Supervisor',
        queryset=None,
        widget=forms.Select(attrs={
            'class': 'select select-bordered w-full',
        }),
        error_messages={
            'required': 'El supervisor es obligatorio.',
        }
    )

    calls_initiated = forms.BooleanField(
        label='¿Llamadas iniciadas?',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'checkbox',
        })
    )

    is_finished = forms.BooleanField(
        label='¿Finalizado?',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'checkbox',
        })
    )

    is_paused = forms.BooleanField(
        label='¿Pausado?',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'checkbox',
        })
    )

    class Meta:
        model = Program
        fields = ['title', 'description', 'supervisor', 'calls_initiated', 'is_finished', 'is_paused']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        from apps.account.models import CustomUser
        self.fields['supervisor'].queryset = CustomUser.objects.all()

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['program', 'agent', 'debtor']

    def __init__(self, *args, **kwargs):
        program = kwargs.pop('program', None)
        super().__init__(*args, **kwargs)
        if program:
            self.fields['program'].queryset = Program.objects.filter(pk=program.pk)
            self.fields['program'].initial = program.pk
            self.fields['program'].required = False
            self.fields['program'].widget = forms.HiddenInput()
        else:
            self.fields['program'].queryset = Program.objects.all()
        self.fields['agent'].queryset = CustomUser.objects.all()
        self.fields['debtor'].queryset = Debtor.objects.all()
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'select select-bordered w-full'
            else:
                field.widget.attrs['class'] = 'input input-bordered w-full'

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Si el campo program está oculto y no viene en cleaned_data, usar initial
        if not self.cleaned_data.get('program') and self.fields['program'].initial:
            instance.program_id = self.fields['program'].initial
        if commit:
            instance.save()
            self.save_m2m()
        return instance
