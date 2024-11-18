from django import forms
from django.contrib.auth.forms import UserCreationForm
from main.models import CustomUser


class RegisterForm(UserCreationForm):
    first_name=forms.CharField(required=True, max_length=15)
    last_name=forms.CharField(required=True, max_length=15)
    email=forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ["first_name","last_name","email", "password1", "password2"]