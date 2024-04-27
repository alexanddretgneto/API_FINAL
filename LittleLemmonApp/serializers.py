
from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})  
    password_repeat = serializers.CharField(write_only=True, style={'input_type': 'password'})  

    # Adicionando campo de grupo
    group = serializers.StringRelatedField(source='groups.first', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password_repeat', 'group']  

    def validate(self, data):
        # Verifica se as senhas são iguais
        if data.get('password') != data.get('password_repeat'):
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('password_repeat', None)
        return super().create(validated_data)
