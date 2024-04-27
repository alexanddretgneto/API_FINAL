from django.urls import include, path
from .views import ListUsersView, UserDeleteView, UserDetailsView
from rest_framework.authtoken import views
from rest_framework.authtoken.views import ObtainAuthToken

urlpatterns = [
    path('users/', ListUsersView.as_view(), name='user-create'),  # Rota para criar usuários
    path('users/<int:pk>/', UserDeleteView.as_view(), name='user-delete'),  # Rota para deletar usuários
    path('user/', UserDetailsView.as_view(), name='user_details'),  # Rota para detalhes do usuário
    
    ]