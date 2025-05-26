from django import forms
from django.contrib.auth.forms import UserCreationForm
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
