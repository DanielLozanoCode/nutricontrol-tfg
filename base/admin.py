from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Alimento, RegistroAlimentacion

class UsuarioAdmin(UserAdmin):
    model = Usuario
    fieldsets = UserAdmin.fieldsets + (
        ('Información nutricional', {
            'fields': ('edad', 'peso', 'altura', 'sexo', 'objetivo', 'actividad_fisica')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información nutricional', {
            'fields': ('edad', 'peso', 'altura', 'sexo', 'objetivo', 'actividad_fisica')
        }),
    )

class RegistroAlimentacionInline(admin.TabularInline):
    model = RegistroAlimentacion
    extra = 0

class AlimentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'calorias', 'proteinas', 'grasas', 'carbohidratos')

class RegistroAlimentacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'alimento', 'cantidad', 'fecha', 'calorias_totales')
    list_filter = ('fecha', 'usuario')
    search_fields = ('alimento__nombre', 'usuario__username')

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Alimento, AlimentoAdmin)
admin.site.register(RegistroAlimentacion, RegistroAlimentacionAdmin)
