from django.contrib import admin
from django.urls import path, include

# from LittleLemmonApp import views esse é o que ele dá
from rest_framework.authtoken import views

from LittleLemmonApp.views import logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('LittleLemmonApp.urls')),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
    path('api-auth/', include('rest_framework.urls')),  # Adiciona as rotas de autenticação do DRF
 
]
