# base/forms.py (CORREGIDO)

from django import forms # forms se usa para forms.CharField, forms.PasswordInput, etc.
from django.contrib.auth.forms import AuthenticationForm 
# PasswordInput NO se importa desde aquí. Se usa forms.PasswordInput.
# UserCreationForm ya no la usábamos directamente para el wizard.
from django.utils.translation import gettext_lazy as _
from .models import Usuario, RegistroAlimentacion

# --- FORMULARIOS PARA EL ASISTENTE DE REGISTRO MULTIPASOS ---

class Paso0NombreForm(forms.Form):
    first_name = forms.CharField(
        label=_("Nombre"),
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': _('¿Cómo te llamas?'), 'autofocus': True}),
        help_text=_("Tu nombre nos ayudará a personalizar tu experiencia.")
    )

class Paso1ObjetivosForm(forms.Form):
    objetivo = forms.ChoiceField(
        # NO incluimos label aquí si lo vamos a poner en la descripción de la plantilla
        choices=Usuario.OBJETIVO_CHOICES, 
        widget=forms.RadioSelect, # No es necesario attrs aquí si el CSS apunta a la estructura
        # help_text=_("Selecciona la opción que mejor describa tu meta.") # Podemos ponerlo en la plantilla
    )
    
    

class Paso2DetallesFisicosForm(forms.Form):
    edad = forms.IntegerField(
        label=_("Edad"),
        min_value=12,
        max_value=99,
        widget=forms.NumberInput(attrs={'placeholder': _('Años')})
    )
    peso = forms.FloatField(
        label=_("Peso actual (kg)"),
        min_value=20,
        max_value=300,
        widget=forms.NumberInput(attrs={'placeholder': _('Ej: 70.5'), 'step': '0.1'})
    )
    altura = forms.IntegerField(
        label=_("Altura (cm)"),
        min_value=100,
        max_value=250,
        widget=forms.NumberInput(attrs={'placeholder': _('Ej: 175')})
    )
    sexo = forms.ChoiceField(
        label=_("Sexo biológico"),
        choices=Usuario.SEXO_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'sexo-radio-option'})
    )
    # Aquí podrías añadir actividad_fisica si lo moviste:
    # actividad_fisica = forms.CharField(
    #     label=_("Nivel de actividad física habitual"),
    #     widget=forms.TextInput(attrs={'placeholder': _('Ej: Sedentario, 3 días de gimnasio/sem, etc.')}),
    #     help_text=_("Describe brevemente tu rutina de ejercicio o actividad."),
    #     required=False # O True, según necesites
    # )

class Paso3CredencialesForm(forms.Form):
    username = forms.CharField(
        label=_("Nombre de usuario"),
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': _('Elige un nombre de usuario único')}),
        help_text=_("Será tu identificador único en NutriControl.")
    )
    email = forms.EmailField(
        label=_("Correo electrónico"),
        widget=forms.EmailInput(attrs={'placeholder': _('tu.correo@ejemplo.com')}),
        help_text=_("Usaremos tu email para la recuperación de cuenta y notificaciones importantes.")
    )
    password = forms.CharField(
        label=_("Contraseña"),
        widget=forms.PasswordInput(attrs={'placeholder': _('Mínimo 8 caracteres')}), # Correcto: usa forms.PasswordInput
        help_text=_("Elige una contraseña segura.")
    )
    confirm_password = forms.CharField(
        label=_("Confirmar contraseña"),
        widget=forms.PasswordInput(attrs={'placeholder': _('Vuelve a escribir la contraseña')}) # Correcto: usa forms.PasswordInput
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Usuario.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(_("Este nombre de usuario ya está en uso. Por favor, elige otro."))
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("Esta dirección de correo electrónico ya está registrada."))
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', _("Las contraseñas no coinciden."))
        
        if password:
            try:
                from django.contrib.auth.password_validation import validate_password
                validate_password(password)
            except forms.ValidationError as e:
                self.add_error('password', e)
            
        return cleaned_data

# --- FORMULARIO DE LOGIN EXISTENTE (PERSONALIZADO) ---
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label=_('Usuario o Email'),
        widget=forms.TextInput(attrs={
            'placeholder': _('Dirección de email o Nombre de usuario'),
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label=_('Contraseña'),
        widget=forms.PasswordInput(attrs={ # Correcto: usa forms.PasswordInput
            'placeholder': _('Contraseña'),
        })
    )

# --- FORMULARIO DE REGISTRO DE ALIMENTACIÓN EXISTENTE ---
class RegistroAlimentacionForm(forms.ModelForm):
    alimento_nombre = forms.CharField(label=_("Buscar alimento"), required=True)

    class Meta:
        model = RegistroAlimentacion
        fields = ['alimento_nombre', 'cantidad']
        widgets = {
            'cantidad': forms.NumberInput(attrs={'placeholder': _('Cantidad en gramos')}),
        }

# --- ANTIGUO FORMULARIO DE REGISTRO (COMENTADO) ---
# from django.contrib.auth.forms import UserCreationForm # Esta importación es para el antiguo form
# class RegistroForm(UserCreationForm):
#     email = forms.EmailField(required=True)
# 
#     class Meta:
#         model = Usuario
#         fields = [
#             'username', 'email', 
#             'edad', 'peso', 'altura', 'sexo', 'objetivo', 'actividad_fisica',
#         ]