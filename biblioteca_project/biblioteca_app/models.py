from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Libro(models.Model):
    titulo = models.CharField(max_length=100)
    autor = models.CharField(max_length=100)
    año_publicacion = models.IntegerField()
    cantidad_stock = models.IntegerField()
    def __str__(self):
        return self.titulo+" "+self.autor+" "+str(self.año_publicacion)+" "+str(self.cantidad_stock)
    
class Rol(models.Model):
    nombre = models.CharField(max_length=50)
    def __str__(self):
        return self.nombre
    
class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    lista_libros = models.ManyToManyField(Libro, related_name='usuarios')
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE,  related_name='usuarios')
    
    def __str__(self):
        return self.nombre + " " + self.email + " " + self.rol.nombre+ " " + self.lista_libros.all()