# base/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, Alimento, RegistroAlimentacion
from django.utils.translation import gettext_lazy as _

# Define un nuevo User admin
class UserAdmin(BaseUserAdmin):
    # Añade tus campos personalizados a los fieldsets
    # Los fieldsets controlan el layout en la página de edición del admin
    fieldsets = BaseUserAdmin.fieldsets + (
        (_('Campos Personalizados'), {'fields': ('edad', 'peso', 'altura', 'sexo', 'objetivo', 'actividad_fisica')}),
    )
    # Añade tus campos personalizados a los add_fieldsets para la página de creación de usuario
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_('Campos Personalizados'), {'fields': ('edad', 'peso', 'altura', 'sexo', 'objetivo', 'actividad_fisica', 'first_name', 'last_name')}),
    )
    # Muestra tus campos personalizados en la lista de usuarios
    list_display = BaseUserAdmin.list_display + ('edad', 'peso', 'altura', 'sexo', 'objetivo')

# Registra tu modelo Usuario con la clase UserAdmin personalizada
admin.site.register(Usuario, UserAdmin)

@admin.register(Alimento)
class AlimentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'calorias', 'proteinas', 'grasas', 'carbohidratos')
    search_fields = ('nombre',)

@admin.register(RegistroAlimentacion)
class RegistroAlimentacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'alimento', 'cantidad', 'fecha', 'calorias_consumidas') # CORREGIDO AQUÍ
    list_filter = ('fecha', 'usuario', 'alimento')
    search_fields = ('usuario__username', 'alimento__nombre')
    date_hierarchy = 'fecha'

    # Si quieres que 'calorias_consumidas' sea "ordenable" en el admin,
    # y como es una propiedad, necesitarás definir un método para ello.
    # Pero para list_display, simplemente referenciar la propiedad funciona.
    def get_calorias_consumidas(self, obj):
        return obj.calorias_consumidas
    get_calorias_consumidas.short_description = _('Calorías Consumidas')
    # Si necesitas ordenarlo:
    # get_calorias_consumidas.admin_order_field = '?' # No se puede ordenar directamente por una propiedad calculada sin más