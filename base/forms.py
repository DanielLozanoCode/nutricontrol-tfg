# base/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm # Asegúrate de importar AuthenticationForm
from .models import Usuario, RegistroAlimentacion

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = Usuario
        fields = [
            'username',
            'email',
            'password1',
            'password2',
            'edad',
            'peso',
            'altura',
            'sexo',
            'objetivo',
            'actividad_fisica',
        ]

class RegistroAlimentacionForm(forms.ModelForm):
    alimento_nombre = forms.CharField(label="Buscar alimento", required=True)

    class Meta:
        model = RegistroAlimentacion
        fields = ['alimento_nombre', 'cantidad']
        widgets = {
            'cantidad': forms.NumberInput(attrs={'placeholder': 'Cantidad en gramos'}),
        }

# --- NUEVO FORMULARIO PARA LOGIN ---
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Username', # La etiqueta se ocultará con CSS en la plantilla login.html
        widget=forms.TextInput(attrs={
            'placeholder': 'Dirección de email o Nombre de usuario', # Placeholder como en la imagen de referencia
            'autofocus': True,
            # Puedes añadir una clase si es necesario para estilos adicionales, ej: 'form-control'
        })
    )
    password = forms.CharField(
        label='Password', # La etiqueta se ocultará con CSS
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña',
            # Puedes añadir una clase si es necesario: 'form-control'
        })
    )