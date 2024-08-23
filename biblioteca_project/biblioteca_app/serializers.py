from rest_framework import serializers

from biblioteca_app.models import Libro, Rol, Usuario

class LibroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Libro
        fields = '__all__'

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'

class UsuarioSerializer(serializers.ModelSerializer):
    lista_libros = LibroSerializer(many=True, read_only=True)
    lista_roles = RolSerializer(many=True, read_only=True)
    rol = serializers.PrimaryKeyRelatedField(queryset=Rol.objects.all(), write_only=True)
    class Meta:
        model = Usuario
        fields = '__all__'