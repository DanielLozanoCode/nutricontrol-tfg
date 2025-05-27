# base/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from datetime import date
from django.utils.translation import gettext_lazy as _ # Para traducciones en modelos/forms

class Usuario(AbstractUser):
    # Campos existentes
    edad = models.PositiveIntegerField(verbose_name=_("Edad"), null=True, blank=True)
    peso = models.FloatField(verbose_name=_("Peso (kg)"), null=True, blank=True)
    altura = models.FloatField(verbose_name=_("Altura (cm)"), null=True, blank=True) # Considera IntegerField si siempre son cm enteros

    SEXO_CHOICES = [
        ('H', _('Hombre')),
        ('M', _('Mujer')),
        ('O', _('Otro')),
    ]
    sexo = models.CharField(
        verbose_name=_("Sexo biológico"), 
        max_length=1, 
        choices=SEXO_CHOICES, 
        null=True, 
        blank=True
    )

    OBJETIVO_CHOICES = [
        # Estos son tus choices actuales. Puedes expandirlos/modificarlos si quieres más granularidad como MyFitnessPal
        ('def', _('Definición')),
        ('vol', _('Volumen')),
        ('man', _('Mantenimiento')),
        ('res', _('Resistencia')),
        # Ejemplos adicionales si quisieras alinearte más con MFP:
        # ('perder_peso', _('Perder peso')),
        # ('ganar_musculo', _('Ganar músculo')),
    ]
    objetivo = models.CharField(
        verbose_name=_("Objetivo principal"),
        max_length=20, # Ajusta si los keys de tus choices son más largos
        choices=OBJETIVO_CHOICES, 
        null=True, 
        blank=True
    )

    actividad_fisica = models.CharField(
        verbose_name=_("Nivel de actividad física"),
        max_length=100, # Podría ser un ChoiceField también
        help_text=_("Ej: Sedentario, ejercicio ligero 1-2/sem, etc."),
        null=True,
        blank=True
    )
    # first_name y last_name ya vienen de AbstractUser.

    def __str__(self):
        return self.username

class Alimento(models.Model):
    nombre = models.CharField(
        verbose_name=_("Nombre del alimento"),
        max_length=100, 
        unique=True, 
        help_text=_("Nombre del alimento")
    )
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
    fecha = models.DateField(verbose_name=_("Fecha"), default=date.today)

    @property
    def calorias_consumidas(self): # Renombrado de calorias_totales para consistencia y claridad
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
    
    # Si quieres mantener calorias_totales por retrocompatibilidad con alguna parte
    # que ya lo use, puedes dejarlo o hacer que llame a calorias_consumidas.
    # Por claridad, usaré calorias_consumidas consistentemente.
    def calorias_totales(self): # Este es el que tenías antes
        return self.calorias_consumidas

    def __str__(self):
        return f"{self.usuario.username} – {self.alimento.nombre} ({self.cantidad} g) - {self.fecha}"

    class Meta:
        verbose_name = _("Registro de Alimentación")
        verbose_name_plural = _("Registros de Alimentación")
        ordering = ['-fecha', '-id']