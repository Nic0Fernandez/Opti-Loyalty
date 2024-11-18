# Generated by Django 5.1.3 on 2024-11-18 15:37

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='Email')),
                ('first_name', models.CharField(max_length=30, verbose_name='Prénom')),
                ('last_name', models.CharField(max_length=30, verbose_name='Nom')),
                ('points', models.PositiveIntegerField(default=0, verbose_name='Points de fidélité')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reduced_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Prix réduit')),
                ('product', models.CharField(max_length=255, verbose_name='Produit applicable')),
                ('qr_code', models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='QR Code Unique')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('is_redeemed', models.BooleanField(default=False, verbose_name='Utilisé')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coupons', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Coupon',
                'verbose_name_plural': 'Coupons',
            },
        ),
    ]