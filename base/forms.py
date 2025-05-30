# base/forms.py

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import Usuario, Alimento, RegistroAlimentacion, MedidaCorporal
from django.utils import timezone

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
        label=_("¿Cuál es tu objetivo principal?"),
        choices=Usuario.OBJETIVO_CHOICES,
        widget=forms.RadioSelect,
        help_text=_("Selecciona la opción que mejor describa tu meta.")
    )

class Paso2DetallesFisicosForm(forms.Form):
    edad = forms.IntegerField(
        label=_("Edad"),
        min_value=12, max_value=99,
        widget=forms.NumberInput(attrs={'placeholder': _('Años')})
    )
    peso = forms.FloatField(
        label=_("Peso actual (kg)"),
        min_value=20, max_value=300,
        widget=forms.NumberInput(attrs={'placeholder': _('Ej: 70.5'), 'step': '0.1'})
    )
    altura = forms.IntegerField(
        label=_("Altura (cm)"),
        min_value=100, max_value=250,
        widget=forms.NumberInput(attrs={'placeholder': _('Ej: 175')})
    )
    sexo = forms.ChoiceField(
        label=_("Sexo biológico"),
        choices=Usuario.SEXO_CHOICES,
        widget=forms.RadioSelect
    )
    actividad_fisica = forms.CharField(
        label=_("Nivel de actividad física habitual"),
        widget=forms.TextInput(attrs={'placeholder': _('Ej: Sedentario, 3 días gimnasio/sem...')}),
        help_text=_("Describe brevemente tu rutina de ejercicio o actividad."),
        required=False 
    )

class Paso3CredencialesForm(forms.Form):
    username = forms.CharField(
        label=_("Nombre de usuario"), max_length=150,
        widget=forms.TextInput(attrs={'placeholder': _('Elige un nombre de usuario único')}),
        help_text=_("Será tu identificador único en NutriControl.")
    )
    email = forms.EmailField(
        label=_("Correo electrónico"),
        widget=forms.EmailInput(attrs={'placeholder': _('tu.correo@ejemplo.com')}),
        help_text=_("Usaremos tu email para la recuperación de cuenta y notificaciones.")
    )
    password = forms.CharField(
        label=_("Contraseña"),
        widget=forms.PasswordInput(attrs={'placeholder': _('Mínimo 8 caracteres')}),
        help_text=_("Elige una contraseña segura.")
    )
    confirm_password = forms.CharField(
        label=_("Confirmar contraseña"),
        widget=forms.PasswordInput(attrs={'placeholder': _('Vuelve a escribir la contraseña')})
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
            from django.contrib.auth.password_validation import validate_password
            try: validate_password(password)
            except forms.ValidationError as e: self.add_error('password', e)
        return cleaned_data

# --- FORMULARIO DE LOGIN ---
class LoginForm(AuthenticationForm):
    username = forms.CharField(label=_('Usuario o Email'), widget=forms.TextInput(attrs={'placeholder': _('Dirección de email o Nombre de usuario'),'autofocus': True}))
    password = forms.CharField(label=_('Contraseña'), widget=forms.PasswordInput(attrs={'placeholder': _('Contraseña')}))

# --- ANTIGUO FORMULARIO DE REGISTRO DE CONSUMO DE ALIMENTACIÓN (AHORA COMENTADO/REEMPLAZADO) ---
# class RegistroAlimentacionForm(forms.ModelForm):
#     alimento_nombre = forms.CharField(label=_("Buscar alimento"), required=True, widget=forms.TextInput(attrs={'placeholder': _('Escribe un alimento...')}))
#     tipo_comida = forms.ChoiceField(choices=RegistroAlimentacion.TIPO_COMIDA_CHOICES, label=_("Tipo de Comida"), required=False)
# 
#     class Meta:
#         model = RegistroAlimentacion
#         fields = ['alimento_nombre', 'cantidad', 'tipo_comida'] 
#         widgets = {
#             'cantidad': forms.NumberInput(attrs={'placeholder': _('Cantidad en gramos')}),
#         }

# --- NUEVO FORMULARIO PARA CREAR UN ALIMENTO EN LA BASE DE DATOS ---
class CrearAlimentoForm(forms.ModelForm):
    class Meta:
        model = Alimento
        fields = ['nombre', 'calorias', 'proteinas', 'grasas', 'carbohidratos']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': _('Ej: Pechuga de pollo a la plancha')}),
            'calorias': forms.NumberInput(attrs={'placeholder': _('Kcal por 100g'), 'step': '0.1'}),
            'proteinas': forms.NumberInput(attrs={'placeholder': _('Gramos por 100g'), 'step': '0.1'}),
            'grasas': forms.NumberInput(attrs={'placeholder': _('Gramos por 100g'), 'step': '0.1'}),
            'carbohidratos': forms.NumberInput(attrs={'placeholder': _('Gramos por 100g'), 'step': '0.1'}),
        }
        labels = {
            'nombre': _('Nombre del Alimento Personalizado'),
            'calorias': _('Calorías (por 100g)'),
            'proteinas': _('Proteínas (g por 100g)'),
            'grasas': _('Grasas (g por 100g)'),
            'carbohidratos': _('Carbohidratos (g por 100g)'),
        }
        help_texts = {
            'nombre': _("Asegúrate de que el nombre sea descriptivo."),
            'calorias': _("Valor numérico."),
            # Puedes añadir más help_texts si lo deseas
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if Alimento.objects.filter(nombre__iexact=nombre).exists():
            # Podrías lanzar un ValidationError, o simplemente advertir y permitirlo.
            # Por ahora, lanzaremos una advertencia si se usa desde una vista que muestre messages.
            # O podrías querer que los nombres sean únicos, en cuyo caso el modelo ya lo manejaría si 'unique=True'.
            # El modelo Alimento ya tiene unique=True para 'nombre'.
            pass # El validador del modelo se encargará si unique=True
        return nombre

# --- FORMULARIO PARA MEDIDAS CORPORALES ---
class MedidaCorporalForm(forms.ModelForm):
    class Meta:
        model = MedidaCorporal
        fields = ['peso', 'cuello', 'cintura', 'caderas']
        widgets = {
            'peso': forms.NumberInput(attrs={'placeholder': _('Tu peso actual en kg'), 'step': '0.1'}),
            'cuello': forms.NumberInput(attrs={'placeholder': _('Circunferencia en cm'), 'step': '0.1'}),
            'cintura': forms.NumberInput(attrs={'placeholder': _('Circunferencia en cm'), 'step': '0.1'}),
            'caderas': forms.NumberInput(attrs={'placeholder': _('Circunferencia en cm'), 'step': '0.1'}),
        }
        help_texts = {
            'peso': _('Ej: 70.5'),
            'cuello': _('Mide la parte más ancha de tu cuello.'),
            'cintura': _('Mide alrededor de tu cintura, a la altura del ombligo.'),
            'caderas': _('Mide la parte más ancha de tus caderas.'),
        }
        labels = { 
            'peso': _('Peso (kg)'), 'cuello': _('Cuello (cm)'),
            'cintura': _('Cintura (cm)'), 'caderas': _('Caderas (cm)'),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cuello'].required = False
        self.fields['cintura'].required = False
        self.fields['caderas'].required = False