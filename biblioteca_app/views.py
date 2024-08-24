from rest_framework import viewsets,status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone

from biblioteca_app.models import Libro, Prestamo, Rol, Usuario
from biblioteca_app.serializers import LibroSerializer, MyTokenSerializer, PrestamoSerializer, RolSerializer, UsuarioSerializer

# Create your views here.

class LibroViewSet(viewsets.ModelViewSet):
    queryset = Libro.objects.all().order_by('id')
    serializer_class = LibroSerializer

    @action(detail=False, methods=['get'])
    def libros_disponibles(self, request):
        libros = self.queryset.filter(cantidad_stock__gt=0)
        serializer = self.get_serializer(libros, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def prestar_libro(self, request, pk=None):
        try:
            libro = self.get_object()  

            usuario_id = request.data.get('usuario_id')
            if usuario_id is None:
                return Response({"detail": "Se necesita un usuario_id"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                usuario = Usuario.objects.get(id=usuario_id)
            except Usuario.DoesNotExist:
                return Response({"detail": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
            # verificar si hay unidades disponibles
            if libro.cantidad_stock <= 0:
                return Response({"detail": "No hay stock disponible"}, status=status.HTTP_400_BAD_REQUEST)
            usuario.lista_libros.add(libro)
            usuario.save()
            libro.cantidad_stock -= 1
            libro.save()
            Prestamo.objects.create(libro=libro, usuario=usuario,fecha_prestamo=timezone.now(),fecha_devolucion= None)
            serializer = self.get_serializer(libro)
            return Response(serializer.data)
        except Libro.DoesNotExist:
            return Response({"detail": "Libro no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['patch'])
    def devolver_libro(self, request, pk=None):
        try:
            libro = self.get_object()  # Obtén el libro con el ID de la URL
            usuario_id = request.data.get('usuario_id')
            if usuario_id is None:
                return Response({"detail": "Se necesita un usuario_id"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                usuario = Usuario.objects.get(id=usuario_id)
            except Usuario.DoesNotExist:
                return Response({"detail": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
            if libro not in usuario.lista_libros.all():
                return Response({"detail": "El usuario no tiene este libro"}, status=status.HTTP_400_BAD_REQUEST)
            usuario.lista_libros.remove(libro)
            usuario.save()
            libro.cantidad_stock += 1
            libro.save()
            Prestamo.objects.update(fecha_devolucion=timezone.now())

            serializer = self.get_serializer(libro)
            return Response(serializer.data)
        except Libro.DoesNotExist:
            return Response({"detail": "Libro no encontrado"}, status=status.HTTP_404_NOT_FOUND)

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all().order_by('id')
    serializer_class = UsuarioSerializer

class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all().order_by('id')
    serializer_class = RolSerializer

class PrestamoViewSet(viewsets.ModelViewSet):
    queryset = Prestamo.objects.all().order_by('id')
    serializer_class = PrestamoSerializer

    @action(detail=False, methods=['get'])
    def prestamos_por_usuario(self, request):
        usuario_id = request.query_params.get('usuario_id')
        if not usuario_id:
            return Response({"detail": "Se necesita un usuario_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            prestamos = Prestamo.objects.filter(usuario_id=usuario_id).order_by('fecha_prestamo')
            serializer = self.get_serializer(prestamos, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class RegistroView(APIView):
    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)  
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        tokens = serializer.validated_data

        try:
            usuario = user.usuario
            lista_libros = usuario.lista_libros.all()
            libros_data = LibroSerializer(lista_libros, many=True).data

            user_data = {
                'id': usuario.id,
                'nombre': usuario.nombre,
                'email': usuario.email,
                'rol': usuario.rol.nombre,
                'lista_libros':  libros_data#[libro.titulo for libro in usuario.lista_libros.all()]
            }
        except Usuario.DoesNotExist:
            user_data = {}
        response_data = {
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'user': user_data
        }
        return Response(response_data)

