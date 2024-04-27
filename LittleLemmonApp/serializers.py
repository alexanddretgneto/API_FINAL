from sqlite3 import IntegrityError
from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        # fields = '__all__'
        fields = ['user', 'menuitem', 'quantity', 'unit_price', 'price']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'



class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    add_to_cart_url = serializers.SerializerMethodField()
    
    class Meta:
        model = MenuItem
        fields = ['id','title','price', 'category', 'add_to_cart_url']
        depth = 1
        
    def get_add_to_cart_url(self, obj):
        request = self.context.get('request')
        if request:
            base_url = request.build_absolute_uri('/')[:-1]  # Remove trailing slash
            return base_url + reverse('menuitem-add-to-cart', args=[obj.id])
        return None
               
    def create(self, validated_data):
        category_data = validated_data.pop('category')
        category, _ = Category.objects.get_or_create(**category_data)
        validated_data['category'] = category
        
        # return MenuItem.objects.create(**validated_data)
        return super(MenuItemSerializer, self).create(validated_data)
    
    def update(self, instance, validated_data):
        category_data = validated_data.pop('category')
        category_serializer = self.fields['category']
        category_instance = instance.category
        
        if category_data:
            category_instance = category_serializer.update(category_instance, category_data)
        instance.title = validated_data.get('title', instance.title)
        instance.price = validated_data.get('price', instance.price)
        instance.save()

        return instance
    
   
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})  
    password_repeat = serializers.CharField(write_only=True, style={'input_type': 'password'})  
    group = serializers.StringRelatedField(source='groups.first', read_only=True)

    class Meta:
        model = User
        fields = '__all__'

    def validate(self, data):
        if data.get('password') != data.get('password_repeat'):
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('password_repeat', None)
        return super().create(validated_data)

class GroupManagerUsersSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), write_only=True)

    class Meta:
        model = User
        fields = '__all__'
        
    def create(self, validated_data):
        group = validated_data.pop('group', None)
        user = super().create(validated_data)
        if group:
            user.groups.add(group)
        return user

    def update(self, instance, validated_data):
        group = validated_data.pop('group', None)
        user = super().update(instance, validated_data)
        if group:
            user.groups.clear()
            user.groups.add(group)
        return user

class GroupDeliveryCrewUsersSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), write_only=True)

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        group = validated_data.pop('group', None)
        user = super().create(validated_data)
        if group:
            user.groups.add(group)
        return user

    def update(self, instance, validated_data):
        group = validated_data.pop('group', None)
        user = super().update(instance, validated_data)
        if group:
            user.groups.clear()
            user.groups.add(group)
        return user
