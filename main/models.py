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
    points = models.PositiveIntegerField(default=0, verbose_name="Points de fidélité")

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    @property
    def current_card(self):
        if self.points < 250:
            return "bronze"
        elif self.points < 750:
            return "argent"
        else:
            return "gold"

    def __str__(self):
        return self.email

class Coupon(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='coupons')
    reduced_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix réduit")
    product = models.CharField(max_length=255, verbose_name="Produit applicable")
    qr_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="QR Code Unique")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    is_redeemed = models.BooleanField(default=False, verbose_name="Utilisé")

    def __str__(self):
        return f"Coupon {self.id} pour {self.product} - {self.reduced_price}€"

    class Meta:
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"