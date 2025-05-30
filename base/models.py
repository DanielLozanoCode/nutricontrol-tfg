# base/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import date # Para default en ConsumoAgua

class Usuario(AbstractUser):
    edad = models.PositiveIntegerField(verbose_name=_("Edad"), null=True, blank=True)
    peso = models.FloatField(verbose_name=_("Peso (kg)"), null=True, blank=True) 
    altura = models.FloatField(verbose_name=_("Altura (cm)"), null=True, blank=True)

    SEXO_CHOICES = [('H', _('Hombre')), ('M', _('Mujer')), ('O', _('Otro'))]
    sexo = models.CharField(verbose_name=_("Sexo biológico"), max_length=1, choices=SEXO_CHOICES, null=True, blank=True)

    OBJETIVO_CHOICES = [
        ('def', _('Definición')), ('vol', _('Volumen')),
        ('man', _('Mantenimiento')), ('res', _('Resistencia')),
    ]
    objetivo = models.CharField(verbose_name=_("Objetivo principal"), max_length=20, choices=OBJETIVO_CHOICES, null=True, blank=True)
    actividad_fisica = models.CharField(verbose_name=_("Nivel de actividad física"), max_length=100, help_text=_("Ej: Sedentario, ejercicio ligero 1-2/sem, etc."), null=True, blank=True)
    
    foto_perfil = models.ImageField(
        verbose_name=_("Foto de perfil"),
        upload_to='fotos_perfil/', 
        null=True, 
        blank=True, 
        default='fotos_perfil/default.png'
    )

    # Campos para objetivos (los valores vendrán de un sistema de objetivos o del perfil)
    calorias_objetivo_fijadas = models.PositiveIntegerField(null=True, blank=True, default=2200)
    proteinas_objetivo_g = models.PositiveIntegerField(null=True, blank=True, default=150)
    grasas_objetivo_g = models.PositiveIntegerField(null=True, blank=True, default=60)
    carbohidratos_objetivo_g = models.PositiveIntegerField(null=True, blank=True, default=265)
    minutos_ejercicio_obj = models.PositiveIntegerField(null=True, blank=True, default=150)
    entrenamientos_semana_obj = models.PositiveIntegerField(null=True, blank=True, default=3)
    calorias_ejercicio_semana_obj = models.PositiveIntegerField(null=True, blank=True, default=1000)
    # Este campo podría ser calculado o no necesario si el ejercicio se registra en otro modelo
    calorias_ejercicio_hoy_registradas = models.PositiveIntegerField(null=True, blank=True, default=0) 

    def __str__(self):
        return self.username

class Alimento(models.Model):
    nombre = models.CharField(verbose_name=_("Nombre del alimento"), max_length=100, unique=True, help_text=_("Nombre del alimento"))
    calorias = models.FloatField(verbose_name=_("Calorías (por 100g)"), help_text=_("Calorías por 100 g"))
    proteinas = models.FloatField(verbose_name=_("Proteínas (por 100g)"), help_text=_("Proteínas por 100 g"))
    grasas = models.FloatField(verbose_name=_("Grasas (por 100g)"), help_text=_("Grasas por 100 g"))
    carbohidratos = models.FloatField(verbose_name=_("Carbohidratos (por 100g)"), help_text=_("Carbohidratos por 100 g"))

    def __str__(self):
        return self.nombre

class RegistroAlimentacion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Usuario"))
    alimento = models.ForeignKey(Alimento, on_delete=models.CASCADE, verbose_name=_("Alimento"))
    cantidad = models.FloatField(verbose_name=_("Cantidad (gramos)"), help_text=_("Cantidad consumida en gramos"))
    fecha = models.DateField(verbose_name=_("Fecha de Consumo"), default=timezone.now) 
    fecha_creacion = models.DateTimeField(verbose_name=_("Fecha de Registro"), auto_now_add=True)


    TIPO_COMIDA_CHOICES = [
        ('desayuno', _('Desayuno')),
        ('almuerzo', _('Almuerzo')), 
        ('comida', _('Comida')), # 'Comida' para la del mediodía como en MFP
        ('cena', _('Cena')),
        ('snacks', _('Snacks')),
    ]
    tipo_comida = models.CharField(
        max_length=20, 
        choices=TIPO_COMIDA_CHOICES, 
        verbose_name=_("Tipo de Comida"),
        null=True, # Permitir nulos si se migra desde datos sin este campo
        blank=True # Permitir vacío si se decide en el formulario
    )

    @property
    def calorias_consumidas(self):
        if self.alimento and self.alimento.calorias is not None and self.cantidad is not None:
            return (self.alimento.calorias * self.cantidad) / 100
        return 0
    @property
    def proteinas_consumidas(self):
        if self.alimento and self.alimento.proteinas is not None and self.cantidad is not None:
            return (self.alimento.proteinas * self.cantidad) / 100
        return 0
    @property
    def grasas_consumidas(self):
        if self.alimento and self.alimento.grasas is not None and self.cantidad is not None:
            return (self.alimento.grasas * self.cantidad) / 100
        return 0
    @property
    def carbohidratos_consumidos(self): 
        if self.alimento and self.alimento.carbohidratos is not None and self.cantidad is not None:
            return (self.alimento.carbohidratos * self.cantidad) / 100
        return 0
    
    def __str__(self):
        return f"{self.usuario.username} – {self.alimento.nombre} ({self.cantidad} g) - {self.fecha}"

    class Meta:
        verbose_name = _("Registro de Alimentación")
        verbose_name_plural = _("Registros de Alimentación")
        ordering = ['-fecha', '-fecha_creacion'] # Ordenar por fecha de consumo y luego por fecha de registro

class MedidaCorporal(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Usuario"))
    fecha = models.DateField(verbose_name=_("Fecha de medición"), default=timezone.now)
    peso = models.FloatField(verbose_name=_("Peso (kg)"), null=True, blank=True, help_text=_("Tu peso en kilogramos, ej: 70.5"))
    cuello = models.FloatField(verbose_name=_("Medida de cuello (cm)"), null=True, blank=True, help_text=_("Circunferencia en centímetros"))
    cintura = models.FloatField(verbose_name=_("Medida de cintura (cm)"), null=True, blank=True, help_text=_("Circunferencia en centímetros, a la altura del ombligo"))
    caderas = models.FloatField(verbose_name=_("Medida de caderas (cm)"), null=True, blank=True, help_text=_("Circunferencia en la parte más ancha"))

    class Meta:
        verbose_name = _("Medida Corporal")
        verbose_name_plural = _("Medidas Corporales")
        ordering = ['usuario', '-fecha'] 
        unique_together = ('usuario', 'fecha') 

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha} - Peso: {self.peso}kg"

# --- NUEVO MODELO PARA CONSUMO DE AGUA ---
class ConsumoAgua(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Usuario"))
    fecha = models.DateField(verbose_name=_("Fecha"), default=date.today) # Usar date.today de datetime
    cantidad_ml = models.PositiveIntegerField(verbose_name=_("Cantidad (ml)"), default=0, help_text=_("Cantidad total de agua consumida en mililitros"))
    # Opcional: numero_vasos si prefieres registrar por vasos y luego convertir
    # numero_vasos = models.PositiveIntegerField(verbose_name=_("Número de vasos"), default=0) 

    class Meta:
        verbose_name = _("Consumo de Agua")
        verbose_name_plural = _("Consumos de Agua")
        ordering = ['usuario', '-fecha']
        unique_together = ('usuario', 'fecha') # Solo un registro de agua por día por usuario

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha} - {self.cantidad_ml}ml"