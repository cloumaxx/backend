from rest_framework import serializers
from django.contrib.auth.models import User

from biblioteca_app.models import Libro, Prestamo, Rol, Usuario
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class LibroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Libro
        fields = '__all__'

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'

class PrestamoSerializer(serializers.ModelSerializer):
    libro = LibroSerializer()
    class Meta:
        model = Prestamo
        fields = fields = ['id', 'fecha_prestamo', 'fecha_devolucion', 'libro', 'usuario']

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        """
        La función `create` crea un nuevo objeto usuario utilizando los datos validados proporcionados.
        """
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


class MyTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        """
        La función `get_token` recupera información del usuario y datos relacionados para generar un token para
        autenticación.
        """
        token = super().get_token(user)
        # Acceder al modelo Usuario relacionado con el usuario autenticado
        try:
            usuario = user.usuario
            token['id'] = usuario.id
            token['nombre'] = usuario.nombre
            token['email'] = usuario.email
            token['rol'] = usuario.rol.nombre
            token['lista_libros'] = [libro.titulo for libro in usuario.lista_libros.all()]
        except Usuario.DoesNotExist:
            # Manejar el caso donde el usuario no tenga un perfil Usuario
            pass
        return token