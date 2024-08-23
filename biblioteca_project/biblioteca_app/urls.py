from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LibroViewSet, LoginView, RegistroView, RolViewSet, UsuarioViewSet

router = DefaultRouter()
router.register(r'libros', LibroViewSet)
router.register(r'usuarios', UsuarioViewSet)
router.register(r'roles', RolViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('registro/', RegistroView.as_view(), name='registro'),
]