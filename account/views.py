from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.urls import reverse

@login_required
def account(request):
    """Affiche les informations du compte de l'utilisateur."""
    return render(request, 'account/account.html', {
        'user': request.user,
    })
    
@login_required
def change_password(request):
    """Permet à l'utilisateur connecté de changer son mot de passe."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Évite la déconnexion après modification
            messages.success(request, "Votre mot de passe a été mis à jour avec succès.")
            return redirect(reverse('account'))
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'account/change_password.html', {'form': form})
    
@login_required
def delete_account(request):
    """Supprime le compte de l'utilisateur connecté."""
    if request.method == "POST":
        user = request.user
        user.delete()
        messages.success(request, "Votre compte a été supprimé avec succès.")
        return redirect(reverse('home'))  # Rediriger vers la page d'accueil ou une autre page après suppression
    else:
        messages.error(request, "Action non autorisée.")
        return redirect(reverse('account'))
