from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    phone = forms.CharField(label="Téléphone",max_length=10,required=True)

    class Meta:
        model = User
        fields = ["phone", "password1", "password2"]