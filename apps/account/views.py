from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.urls import reverse

@login_required
def account(request):
    return render(request, 'account/account.html', {
        'user': request.user,
    })
    
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  
            messages.success(request, "Votre mot de passe a été mis à jour avec succès.")
            return redirect(reverse('account'))
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'account/change_password.html', {'form': form})
    
@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        user.delete()
        messages.success(request, "Votre compte a été supprimé avec succès.")
        return redirect(reverse('home'))  
    else:
        messages.error(request, "Action non autorisée.")
        return redirect(reverse('account'))
