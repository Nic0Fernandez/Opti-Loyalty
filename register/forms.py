from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from main.models import CustomUser


class RegisterForm(UserCreationForm):
    first_name=forms.CharField(required=True, max_length=15)
    last_name=forms.CharField(required=True, max_length=15)
    email=forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ["first_name","last_name","email", "password1", "password2"]


    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email
    

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", max_length=254)

    def clean(self):
        email = self.cleaned_data.get('username').lower()
        password = self.cleaned_data.get('password')
        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Email ou mot de passe incorrect.")
            elif not self.user_cache.is_active:
                raise forms.ValidationError("Cet utilisateur est inactif.")
        return self.cleaned_data