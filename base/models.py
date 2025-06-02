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

    calorias_objetivo_fijadas = models.PositiveIntegerField(null=True, blank=True, default=2200, verbose_name=_("Objetivo de Ingesta Calórica (kcal)"))
    # Nuevos nombres para objetivos de ejercicio semanales para claridad
    minutos_ejercicio_obj_semana = models.PositiveIntegerField(null=True, blank=True, default=150, verbose_name=_("Minutos de Ejercicio Objetivo (Semanal)"))
    entrenamientos_semana_obj = models.PositiveIntegerField(null=True, blank=True, default=3, verbose_name=_("Entrenamientos por Semana Objetivo"))
    calorias_ejercicio_semana_obj = models.PositiveIntegerField(null=True, blank=True, default=1000, verbose_name=_("Calorías de Ejercicio Objetivo (Semanal)"))
    # Campos de objetivos de macros que ya tenías
    proteinas_objetivo_g = models.PositiveIntegerField(null=True, blank=True, default=150, verbose_name=_("Proteínas Objetivo (g)"))
    grasas_objetivo_g = models.PositiveIntegerField(null=True, blank=True, default=60, verbose_name=_("Grasas Objetivo (g)"))
    carbohidratos_objetivo_g = models.PositiveIntegerField(null=True, blank=True, default=265, verbose_name=_("Carbohidratos Objetivo (g)"))
    
    calorias_ejercicio_hoy_registradas = models.PositiveIntegerField(default=0, verbose_name=_("Calorías de Ejercicio Registradas Hoy (kcal)"))

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
        ('desayuno', _('Desayuno')), ('almuerzo', _('Almuerzo')),
        ('comida', _('Comida')), ('cena', _('Cena')), ('snacks', _('Snacks')),
    ]
    tipo_comida = models.CharField(max_length=20, choices=TIPO_COMIDA_CHOICES, verbose_name=_("Tipo de Comida"), null=True, blank=True)

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
        ordering = ['-fecha', '-fecha_creacion']

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

class ConsumoAgua(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Usuario"))
    fecha = models.DateField(verbose_name=_("Fecha"), default=date.today)
    cantidad_ml = models.PositiveIntegerField(verbose_name=_("Cantidad (ml)"), default=0, help_text=_("Cantidad total de agua consumida en mililitros"))

    class Meta:
        verbose_name = _("Consumo de Agua")
        verbose_name_plural = _("Consumos de Agua")
        ordering = ['usuario', '-fecha']
        unique_together = ('usuario', 'fecha')

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha} - {self.cantidad_ml}ml"

# --- MODELOS PARA EJERCICIOS ---

class Ejercicio(models.Model):
    nombre = models.CharField(max_length=150, unique=True, verbose_name=_("Nombre del Ejercicio"))
    TIPO_EJERCICIO_CHOICES = [
        ('cardio', _('Cardiovascular')),
        ('fuerza', _('Fuerza')),
    ]
    tipo = models.CharField(max_length=10, choices=TIPO_EJERCICIO_CHOICES, verbose_name=_("Tipo de Ejercicio"))
    GRUPO_MUSCULAR_CHOICES = [
        ('pecho', _('Pecho')), ('espalda', _('Espalda')), ('piernas', _('Piernas')),
        ('hombros', _('Hombros')), ('brazos', _('Brazos')), ('abdominales', _('Abdominales')),
        ('cardio_general', _('Cardio General')),
    ]
    grupo_muscular = models.CharField(
        max_length=20, choices=GRUPO_MUSCULAR_CHOICES,
        null=True, blank=True, verbose_name=_("Grupo Muscular")
    )
    descripcion = models.TextField(null=True, blank=True, verbose_name=_("Descripción"))
    video_url = models.URLField(max_length=255, null=True, blank=True, verbose_name=_("URL del Video Explicativo"))
    calorias_quemadas_base = models.PositiveIntegerField(
        default=50, verbose_name=_("Calorías Quemadas Base"),
        help_text=_("Para fuerza: kcal por sesión estándar. Para cardio: kcal por minuto.")
    )

    def __str__(self):
        return f"{self.get_grupo_muscular_display() if self.grupo_muscular else self.get_tipo_display()}: {self.nombre}"

    class Meta:
        verbose_name = _("Ejercicio")
        verbose_name_plural = _("Ejercicios")
        ordering = ['grupo_muscular', 'tipo', 'nombre']

class RegistroEjercicioRealizado(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Usuario"))
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE, verbose_name=_("Ejercicio Realizado"))
    fecha = models.DateField(verbose_name=_("Fecha de Realización"), default=timezone.now)
    duracion_minutos = models.PositiveIntegerField(
        null=True, blank=True, verbose_name=_("Duración (minutos)"),
        help_text=_("Completar para ejercicios cardiovasculares.")
    )
    series = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Series"))
    repeticiones_por_serie = models.CharField(
        max_length=100, null=True, blank=True, verbose_name=_("Repeticiones por Serie"),
        help_text=_("Ej: 12,10,8 o simplemente 10 si todas iguales.")
    )
    peso_utilizado_kg = models.CharField(
        max_length=100, null=True, blank=True, verbose_name=_("Peso Utilizado (kg) por Serie"),
        help_text=_("Ej: 50,50,55 o simplemente 50 si todas iguales.")
    )
    calorias_quemadas_calculadas = models.PositiveIntegerField(default=0, verbose_name=_("Calorías Quemadas en esta Sesión"))
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.ejercicio.tipo == 'cardio':
            if self.duracion_minutos and self.ejercicio.calorias_quemadas_base > 0:
                self.calorias_quemadas_calculadas = self.ejercicio.calorias_quemadas_base * self.duracion_minutos
            else:
                self.calorias_quemadas_calculadas = 0
        elif self.ejercicio.tipo == 'fuerza':
            self.calorias_quemadas_calculadas = self.ejercicio.calorias_quemadas_base
        else:
            self.calorias_quemadas_calculadas = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.usuario.username} - {self.ejercicio.nombre} ({self.fecha})"

    class Meta:
        ordering = ['-fecha', '-fecha_creacion']
        verbose_name = _("Registro de Ejercicio Realizado")
        verbose_name_plural = _("Registros de Ejercicios Realizados")

class NotaDiariaEjercicio(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Usuario"))
    fecha = models.DateField(verbose_name=_("Fecha de la Nota"), default=timezone.now)
    texto_nota = models.TextField(
        verbose_name=_("Notas sobre el Ejercicio del Día"),
        help_text=_("Anota aquí cualquier observación general sobre tu actividad física del día.")
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Nota Diaria de Ejercicio")
        verbose_name_plural = _("Notas Diarias de Ejercicio")
        ordering = ['usuario', '-fecha']
        unique_together = ('usuario', 'fecha')

    def __str__(self):
        return f"Nota de {self.usuario.username} para {self.fecha}"