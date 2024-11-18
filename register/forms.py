from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    first_name=forms.CharField(required=True, max_length=15)
    last_name=forms.CharField(required=True, max_length=15)
    email=forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["first_name","last_name","email", "password1", "password2"]