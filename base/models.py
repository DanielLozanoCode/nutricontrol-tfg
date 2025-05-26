from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from datetime import date

class Usuario(AbstractUser):
    edad = models.PositiveIntegerField(null=True, blank=True)
    peso = models.FloatField(null=True, blank=True)
    altura = models.FloatField(null=True, blank=True)

    SEXO_CHOICES = [
        ('H', 'Hombre'),
        ('M', 'Mujer'),
        ('O', 'Otro'),
    ]
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, null=True, blank=True)

    OBJETIVO_CHOICES = [
        ('def', 'Definición'),
        ('vol', 'Volumen'),
        ('man', 'Mantenimiento'),
        ('res', 'Resistencia'),
    ]
    objetivo = models.CharField(max_length=3, choices=OBJETIVO_CHOICES, null=True, blank=True)

    actividad_fisica = models.CharField(
        max_length=100,
        help_text="Tipo de actividad o deporte habitual",
        null=True,
        blank=True
    )

    def __str__(self):
        return self.username

class Alimento(models.Model):
    nombre        = models.CharField(max_length=100, unique=True, help_text="Nombre del alimento")
    calorias      = models.FloatField(help_text="Calorías por 100 g")
    proteinas     = models.FloatField(help_text="Proteínas por 100 g")
    grasas        = models.FloatField(help_text="Grasas por 100 g")
    carbohidratos = models.FloatField(help_text="Carbohidratos por 100 g")

    def __str__(self):
        return self.nombre

class RegistroAlimentacion(models.Model):
    usuario    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    alimento   = models.ForeignKey(Alimento, on_delete=models.CASCADE)
    cantidad   = models.FloatField(help_text="Cantidad en gramos")
    fecha      = models.DateField(default=date.today)

    def calorias_totales(self):
        return (self.alimento.calorias * self.cantidad) / 100

    def __str__(self):
        return f"{self.usuario.username} – {self.alimento.nombre} ({self.cantidad} g)"
