from django.shortcuts import get_object_or_404, redirect
from rest_framework import generics, status
from .permissions import IsManager
from .serializers import GroupDeliveryCrewUsersSerializer, GroupManagerUsersSerializer, UserSerializer
from django.contrib.auth.models import User, Group
from rest_framework.decorators import api_view
from rest_framework import viewsets, permissions
from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import CategorySerializer, MenuItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.decorators import action

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:  # Apenas listar para entregadores
            permission_classes = [permissions.IsAuthenticated]
        else:  # Acesso total para gerentes
            permission_classes = [permissions.IsAuthenticated, IsManager]
        return [permission() for permission in permission_classes]
   
    @action(detail=True, methods=['post'])
    def add_to_cart(self, request, pk=None):
        menuitem = self.get_object()
        quantity = int(request.data.get('quantity', 1))  # Default to 1 if quantity is not provided
        user = request.user
        unit_price = menuitem.price
        price = unit_price * quantity

        cart_item, created = Cart.objects.get_or_create(user=user, menuitem=menuitem)
        if not created:
            cart_item.quantity += quantity
            cart_item.price += price
            cart_item.save()
        else:
            cart_item.quantity = quantity
            cart_item.unit_price = unit_price
            cart_item.price = price
            cart_item.save()

        serializer = CartSerializer(cart_item)
        return Response(serializer.data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())
    #     serializer = self.get_serializer(queryset, many=True)
    #     for item in serializer.data:
    #         item['add_to_cart_url'] = request.build_absolute_uri() + f"{item['id']}/add-to-cart/"
    #     return Response(serializer.data)

    # def create(self, request, *args, **kwargs):
    #     if not request.user.groups.filter(name='Gerentes').exists():
    #         raise PermissionDenied("Apenas gerentes podem criar itens de menu.")
    #     return super(MenuItemViewSet, self).create(request, *args, **kwargs)

    # def update(self, request, *args, **kwargs):
    #     if not request.user.groups.filter(name='Gerentes').exists():
    #         raise PermissionDenied("Apenas gerentes podem atualizar itens de menu.")
    #     return super(MenuItemViewSet, self).update(request, *args, **kwargs)

    # def retrieve(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance)
    #     return Response(serializer.data)

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:  # Apenas listar para entregadores
            permission_classes = [permissions.IsAuthenticated]
        else:  # Acesso total para gerentes
            permission_classes = [permissions.IsAuthenticated, IsManager]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
   
    
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:  # Apenas listar para entregadores
            permission_classes = [permissions.IsAuthenticated]
        else:  # Acesso total para gerentes
            permission_classes = [permissions.IsAuthenticated, IsManager]
        return [permission() for permission in permission_classes]

    def get_object(self):
        if self.action == 'me':
            # Retorna o usuário autenticado
            return self.request.user
        else:
            return super().get_object()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        if 'pk' not in kwargs:
            # Se 'pk' não estiver presente nos argumentos, atualize o usuário autenticado
            instance = self.request.user
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            return super().update(request, *args, **kwargs)

    @action(detail=False, methods=['GET', 'PUT', 'DELETE'])
    def me(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
      


class GroupManagerUsersViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsManager]
    queryset = User.objects.filter(groups__name='Gerentes')  # Filtrar usuários pertencentes ao grupo 'Gerentes'
    serializer_class = GroupManagerUsersSerializer

    def create(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Gerentes').exists():
            raise PermissionDenied("Apenas gerentes podem criar usuários de grupo.")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Gerentes').exists():
            raise PermissionDenied("Apenas gerentes podem atualizar usuários de grupo.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Gerentes').exists():
            raise PermissionDenied("Apenas gerentes podem excluir usuários de grupo.")
        return super().destroy(request, *args, **kwargs)
    
class GroupDeliveryCrewUsersViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsManager]
    queryset = User.objects.filter(groups__name='Entregador')  # Filtrar usuários pertencentes ao grupo 'Entregador'
    serializer_class = GroupDeliveryCrewUsersSerializer

    def create(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Gerentes').exists():
            raise PermissionDenied("Apenas gerentes podem criar usuários de grupo.")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Gerentes').exists():
            raise PermissionDenied("Apenas gerentes podem atualizar usuários de grupo.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Gerentes').exists():
            raise PermissionDenied("Apenas gerentes podem excluir usuários de grupo.")
        return super().destroy(request, *args, **kwargs)

