from django.shortcuts import render
from rest_framework import viewsets,status
from rest_framework.response import Response
from rest_framework.decorators import action

from biblioteca_app.models import Libro, Rol, Usuario
from biblioteca_app.serializers import LibroSerializer, RolSerializer, UsuarioSerializer

# Create your views here.

class LibroViewSet(viewsets.ModelViewSet):
    queryset = Libro.objects.all()
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

            libro.cantidad_stock -= 1
            libro.save()
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
            libro.cantidad_stock += 1
            libro.save()
            serializer = self.get_serializer(libro)
            return Response(serializer.data)
        except Libro.DoesNotExist:
            return Response({"detail": "Libro no encontrado"}, status=status.HTTP_404_NOT_FOUND)

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer