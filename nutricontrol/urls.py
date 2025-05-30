# nutricontrol/urls.py (o como se llame tu urls.py principal)

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from base.forms import LoginForm
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('base.urls')), # Esto incluye las URLs de tu app 'base'
    
    # --- URL DE LOGIN MODIFICADA ---
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html', 
        authentication_form=LoginForm  # ⬅️ --- USA TU LOGINFORM PERSONALIZADO ---
    ), name='login'),
    
    # Tu LogoutView original (ajustado en la respuesta anterior para redirigir a 'dashboard')
    # Si eliminaste /inicio/, debería ser next_page='dashboard'
    # Si mantuviste /inicio/, podría ser next_page='inicio_publico' o 'dashboard'
    # Asumiré que lo ajustamos a 'dashboard' (la raíz)
    path('logout/', auth_views.LogoutView.as_view(next_page='dashboard'), name='logout'), 
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)