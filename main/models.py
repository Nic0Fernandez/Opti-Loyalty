from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid

# Create your models here.

class CustomUser(AbstractUser):
    point = models.PositiveIntegerField(default=0, verbose_name="Points de fidélité")

    @property
    def current_card(self):
        if self.point < 250:
            return "bronze"
        elif self.point < 750:
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
    