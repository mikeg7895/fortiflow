from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'usuario'
        }),
        required=True,
        error_messages={
            'required': 'El nombre de usuario es obligatorio.',
        }
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'contraseña'
        }),
        required=True,
        error_messages={
            'required': 'La contraseña es obligatoria.',
        }
    )

    error_messages = {
        'invalid_login': 'Usuario o contraseña incorrectos.',
        'inactive': 'Usuario inactivo.',
    }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError("El nombre de usuario es obligatorio.")
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError("La contraseña es obligatoria.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            user = authenticate(self.request, username=username, password=password)
            if user is None:
                raise forms.ValidationError("Usuario o contraseña incorrectos.")
        return cleaned_data


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'usuario',
            'autocomplete': 'username'
        }),
        error_messages={
            'required': 'El nombre de usuario es obligatorio.',
            'unique': 'Este nombre de usuario ya está en uso.'
        }
    )
    
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Contraseña',
            'autocomplete': 'new-password'
        }),
        error_messages={
            'required': 'La contraseña es obligatoria.'
        }
    )
    
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Confirmar contraseña',
            'autocomplete': 'new-password'
        }),
        error_messages={
            'required': 'Debes confirmar la contraseña.',
        }
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'correo@ejemplo.com',
            'autocomplete': 'email'
        }),
        error_messages={
            'required': 'El correo electrónico es obligatorio.',
            'invalid': 'Ingresa un correo electrónico válido.',
            'unique': 'Este correo electrónico ya está en uso.'
        }
    )
    
    first_name = forms.CharField(
        label='Nombre',
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Nombre',
            'autocomplete': 'given-name'
        })
    )
    
    last_name = forms.CharField(
        label='Apellido',
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Apellido',
            'autocomplete': 'family-name'
        })
    )
    
    group = forms.ModelChoiceField(
        label='Grupo',
        queryset=Group.objects.all(),
        widget=forms.Select(attrs={
            'class': 'select select-bordered w-full',
        }),
        required=True,
        error_messages={
            'required': 'Debes seleccionar un grupo.'
        }
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'group')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está en uso.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            group = self.cleaned_data.get('group')
            if group:
                user.groups.add(group)
        return user


class CustomUserEditForm(forms.ModelForm):
    username = forms.CharField(
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'usuario',
            'autocomplete': 'username'
        }),
        error_messages={
            'required': 'El nombre de usuario es obligatorio.',
            'unique': 'Este nombre de usuario ya está en uso.'
        }
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'correo@ejemplo.com',
            'autocomplete': 'email'
        }),
        error_messages={
            'required': 'El correo electrónico es obligatorio.',
            'invalid': 'Ingresa un correo electrónico válido.',
            'unique': 'Este correo electrónico ya está en uso.'
        }
    )
    
    first_name = forms.CharField(
        label='Nombre',
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Nombre',
            'autocomplete': 'given-name'
        })
    )
    
    last_name = forms.CharField(
        label='Apellido',
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Apellido',
            'autocomplete': 'family-name'
        })
    )
    
    group = forms.ModelChoiceField(
        label='Grupo',
        queryset=Group.objects.all(),
        widget=forms.Select(attrs={
            'class': 'select select-bordered w-full',
        }),
        required=True,
        error_messages={
            'required': 'Debes seleccionar un grupo.'
        }
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'group')

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            groups = self.instance.groups.all()
            if groups.exists():
                self.fields['group'].initial = groups.first()

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            group = self.cleaned_data.get('group')
            if group:
                user.groups.set([group])
        return user
    