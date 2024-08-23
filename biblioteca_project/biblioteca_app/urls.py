from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LibroViewSet, RolViewSet, UsuarioViewSet

router = DefaultRouter()
router.register(r'libros', LibroViewSet)
router.register(r'usuarios', UsuarioViewSet)
router.register(r'roles', RolViewSet)

urlpatterns = [
    path('', include(router.urls)),
]