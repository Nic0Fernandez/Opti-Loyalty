from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import RegisterForm, EmailAuthenticationForm

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data.get('email').lower()
            user.save()
            
            email = form.cleaned_data.get('email').lower()
            password = form.cleaned_data.get('password1')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Inscription réussie ! Bienvenue sur notre site.")
                return redirect('home') 
            else:
                messages.error(request, "Erreur lors de l'authentification. Veuillez vous connecter.")
                return redirect('login')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = RegisterForm()
    
    return render(request, "register/register.html", {"form": form})
