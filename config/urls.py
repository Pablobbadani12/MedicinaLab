from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

# Personalización del Admin de Django
admin.site.site_header = 'Administración VisionSalud'
admin.site.site_title = 'Administración VisionSalud'
admin.site.index_title = 'Administración VisionSalud'
@csrf_exempt
def logout_view(request):
    """Vista de logout que acepta GET y POST para evitar error 403 CSRF."""
    auth_logout(request)
    return redirect('/login/')


urlpatterns = [
    # ── Sobrescribe el logout del admin ──────────────────────────────────────
    path('admin/logout/', logout_view, name='admin_logout'),

    # ── Sobrescribe el login del admin para usar el login propio ─────────────
    path('admin/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='admin_login'),

    path('admin/', admin.site.urls),

    # Raíz: redirige al dashboard de informes
    path('', RedirectView.as_view(url='/informes/', permanent=False), name='home'),

    # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),

    # Captura cualquier sub-path de /login/... y redirige al login correcto
    re_path(r'^login/.+$', RedirectView.as_view(url='/login/', permanent=False)),

    # Aplicaciones
    path('empresas/', include('apps.empresas.urls')),
    path('pacientes/', include('apps.pacientes.urls')),
    path('informes/', include('apps.informes.urls', namespace='informes')),
    path('turnos/', include('apps.turnos.urls', namespace='turnos')),
    path('preocupacional/', include('apps.preocupacional.urls', namespace='preocupacional')),
]

from django.views.static import serve

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]

