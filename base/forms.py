# base/forms.py

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import Usuario, Alimento, RegistroAlimentacion, MedidaCorporal, ConsumoAgua, Ejercicio, RegistroEjercicioRealizado, NotaDiariaEjercicio
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
        # El modelo Alimento ya tiene unique=True para 'nombre', por lo que la validación
        # a nivel de base de datos lo manejará. Si quieres un error más amigable a nivel de form:
        # if self.instance.pk is None and Alimento.objects.filter(nombre__iexact=nombre).exists():
        #     raise forms.ValidationError(_("Un alimento con este nombre ya existe."))
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

# --- NUEVO: FORMULARIO PARA AÑADIR CONSUMO DE ALIMENTO (DESDE EL MODAL DEL DIARIO) ---
class AnadirConsumoAlimentoForm(forms.Form):
    alimento_nombre = forms.CharField(
        label=_("Buscar alimento existente"),
        widget=forms.TextInput(attrs={
            'placeholder': _('Escribe el nombre de un alimento...'),
            'list': 'sugerencias_para_consumo_diario', # ID del datalist que usaremos en la plantilla
            'autocomplete': 'off' # Para evitar el autocompletado del navegador
        }),
        help_text=_("Selecciona un alimento de la lista o escribe su nombre exacto.")
    )
    cantidad = forms.FloatField(
        label=_("Cantidad (gramos)"),
        min_value=0.1,
        widget=forms.NumberInput(attrs={'placeholder': _('Ej: 150'), 'step': '0.1'})
    )
    # Estos campos serán HiddenInput, prellenados por la vista/JS
    fecha = forms.DateField(widget=forms.HiddenInput())
    tipo_comida = forms.CharField(widget=forms.HiddenInput())

    # Campo oculto para almacenar el ID del alimento seleccionado (poblado por JS o validación)
    alimento_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    def clean_alimento_nombre(self):
        nombre = self.cleaned_data.get('alimento_nombre')
        try:
            alimento = Alimento.objects.get(nombre__iexact=nombre)
            # Guardamos el ID en cleaned_data para que la vista pueda usarlo directamente
            # Esto es útil si no tenemos un campo oculto 'alimento_id' que se pueble con JS
            self.cleaned_data['alimento_id_validated'] = alimento.id
            return nombre # Devolvemos el nombre, la vista usará el ID validado
        except Alimento.DoesNotExist:
            raise forms.ValidationError(_("Este alimento no se encuentra en la base de datos. Por favor, regístralo primero usando la opción del menú o elige uno existente."))
        except Alimento.MultipleObjectsReturned:
             raise forms.ValidationError(_("Se encontraron múltiples alimentos con este nombre exacto (esto no debería ocurrir si 'nombre' es único). Contacte al administrador."))
        return nombre

    def clean(self):
        cleaned_data = super().clean()
        alimento_id_from_hidden = cleaned_data.get('alimento_id') # Del campo oculto opcional
        alimento_id_from_validation = cleaned_data.get('alimento_id_validated')

        if not alimento_id_from_hidden and not alimento_id_from_validation:
            # Si no tenemos un ID ni por campo oculto ni por validación del nombre,
            # y el campo 'alimento_nombre' no tuvo un error previo, es un problema.
            # Pero la validación de 'alimento_nombre' ya debería haber fallado si no se encontró.
            pass # La validación de 'alimento_nombre' es la principal fuente del ID aquí.

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar clases de Bootstrap si se desea para consistencia en el modal
        self.fields['alimento_nombre'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['cantidad'].widget.attrs.update({'class': 'form-control form-control-sm'})
        
class RegistrarEjercicioCardioForm(forms.Form):
    ejercicio_nombre = forms.CharField(
        label=_("Buscar Ejercicio Cardiovascular"),
        widget=forms.TextInput(attrs={
            'placeholder': _('Escribe el nombre del ejercicio cardio...'),
            'list': 'sugerencias_ejercicio_cardio', # Datalist ID
            'autocomplete': 'off'
        }),
        help_text=_("Selecciona un ejercicio cardiovascular de la lista.")
    )
    duracion_minutos = forms.IntegerField(
        label=_("Duración (minutos)"),
        min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': _('Ej: 30')})
    )
    # Campos ocultos para pasar datos adicionales a la vista
    fecha = forms.DateField(widget=forms.HiddenInput())
    ejercicio_id = forms.IntegerField(widget=forms.HiddenInput(), required=False) # Para el ID del ejercicio seleccionado

    def clean_ejercicio_nombre(self):
        nombre = self.cleaned_data.get('ejercicio_nombre')
        try:
            # Asegurarse que el ejercicio es de tipo cardio
            ejercicio = Ejercicio.objects.get(nombre__iexact=nombre, tipo='cardio')
            self.cleaned_data['ejercicio_id_validated'] = ejercicio.id
            return nombre
        except Ejercicio.DoesNotExist:
            raise forms.ValidationError(_("Este ejercicio cardiovascular no existe en la base de datos o no es de tipo cardio."))
        return nombre

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ejercicio_nombre'].widget.attrs.update({'class': 'form-control form-control-sm mb-1'})
        self.fields['duracion_minutos'].widget.attrs.update({'class': 'form-control form-control-sm'})


class RegistrarEjercicioFuerzaForm(forms.Form):
    ejercicio_nombre = forms.CharField(
        label=_("Buscar Ejercicio de Fuerza"),
        widget=forms.TextInput(attrs={
            'placeholder': _('Escribe el nombre del ejercicio de fuerza...'),
            'list': 'sugerencias_ejercicio_fuerza', # Datalist ID
            'autocomplete': 'off'
        })
    )
    series = forms.IntegerField(
        label=_("Series"),
        min_value=1,
        required=False, # Puede que solo quieran registrar el ejercicio sin detalles
        widget=forms.NumberInput(attrs={'placeholder': _('Ej: 3')})
    )
    repeticiones_por_serie = forms.CharField(
        label=_("Repeticiones por Serie"),
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('Ej: 12,10,8 o 3x10')}),
        help_text=_("Puedes usar comas o 'x' para separar.")
    )
    peso_utilizado_kg = forms.CharField(
        label=_("Peso Utilizado (kg) por Serie"),
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('Ej: 50,55,60 o 3x50kg')}),
        help_text=_("Opcional. Especifica el peso para cada serie si varía.")
    )
    # Campos ocultos
    fecha = forms.DateField(widget=forms.HiddenInput())
    ejercicio_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    def clean_ejercicio_nombre(self):
        nombre = self.cleaned_data.get('ejercicio_nombre')
        try:
            # Asegurarse que el ejercicio es de tipo fuerza
            ejercicio = Ejercicio.objects.get(nombre__iexact=nombre, tipo='fuerza')
            self.cleaned_data['ejercicio_id_validated'] = ejercicio.id
            return nombre
        except Ejercicio.DoesNotExist:
            raise forms.ValidationError(_("Este ejercicio de fuerza no existe en la base de datos o no es de tipo fuerza."))
        return nombre

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ejercicio_nombre'].widget.attrs.update({'class': 'form-control form-control-sm mb-1'})
        self.fields['series'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['repeticiones_por_serie'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['peso_utilizado_kg'].widget.attrs.update({'class': 'form-control form-control-sm'})


class NotaDiariaEjercicioForm(forms.ModelForm):
    class Meta:
        model = NotaDiariaEjercicio
        fields = ['texto_nota']
        widgets = {
            'texto_nota': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': _('Escribe aquí tus notas sobre el entrenamiento de hoy...')
            }),
        }
        labels = {
            'texto_nota': _("Notas del Ejercicio de Hoy") # Ocultar si es obvio por el contexto de la página
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['texto_nota'].widget.attrs.update({'class': 'form-control'})