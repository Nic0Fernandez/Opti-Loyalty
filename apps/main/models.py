from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
import uuid
from io import BytesIO
from django.core.files import File

class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        """
        Crée et enregistre un utilisateur avec l'email et le mot de passe donnés.
        """
        if not email:
            raise ValueError('L\'adresse email doit être fournie')
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=255, verbose_name="Email")
    first_name = models.CharField(max_length=30, verbose_name="Prénom")
    last_name = models.CharField(max_length=30, verbose_name="Nom")

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']


    def __str__(self):
        return self.email

class Pizza(models.Model):
    pizza_id=models.TextField(primary_key=True,  editable=False)
    unit_price = models.DecimalField(max_digits=5, decimal_places=2)
    name = models.CharField(max_length=100)
    ingredients = models.TextField()
    category=models.TextField()
    size=models.TextField()
    image = models.ImageField(upload_to='media/pizza/')  

    def __str__(self):
        return self.name
    
    
class Order(models.Model):
    order_id=models.IntegerField(primary_key=True, editable=False)
    client_id= models.IntegerField()
    pizza_id = models.CharField(max_length=100)
    order_date=models.DateField()

    def __str__(self):
        return self.name