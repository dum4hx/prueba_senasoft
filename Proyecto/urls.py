"""
URL configuration for Proyecto project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from App import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='inicio'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('seleccionar_vuelos/', views.seleccionar_vuelos, name='seleccionar_vuelos'),
    path('confirmar_reserva/', views.confirmar_reserva, name='confirmar_reserva'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
    path('procesar-pago/', views.procesar_pago, name='procesar_pago'),
    path('confirmar-pago/', views.confirmar_pago, name='confirmar_pago'),
    path('mis_vuelos/', views.mis_vuelos, name='mis_vuelos'),
    path('mis_vuelos/descargar/<int:id_pago>/', views.descargar_tiquete_pdf, name='descargar_tiquete_pdf'),



]

urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)