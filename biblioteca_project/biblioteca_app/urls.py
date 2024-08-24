from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LibroViewSet,  MyTokenObtainPairView, PrestamoViewSet, RegistroView, RolViewSet, UsuarioViewSet

router = DefaultRouter()
router.register(r'libros', LibroViewSet)
router.register(r'usuarios', UsuarioViewSet)
router.register(r'roles', RolViewSet)
router.register(r'prestamos', PrestamoViewSet, basename='prestamos')


urlpatterns = [
    path('', include(router.urls)),
    path('login/', MyTokenObtainPairView.as_view(), name='login'),
    path('registro/', RegistroView.as_view(), name='registro'),
]