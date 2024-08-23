from rest_framework import serializers
from django.contrib.auth.models import User

from biblioteca_app.models import Libro, Rol, Usuario

class LibroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Libro
        fields = '__all__'

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    
class UsuarioSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    lista_libros = LibroSerializer(many=True, read_only=True)
    lista_roles = RolSerializer(many=True, read_only=True)
    rol = serializers.PrimaryKeyRelatedField(queryset=Rol.objects.all(), write_only=True)
    class Meta:
        model = Usuario
        fields = '__all__'
        
    def create(self, validated_data):
        # Extraemos los datos del User
        user_data = validated_data.pop('user')
        # Creamos el User
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        # Creamos el Usuario relacionado con el User
        usuario = Usuario.objects.create(user=user, **validated_data)
        return usuario

# proceso de login 
