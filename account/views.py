from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

@login_required
def account(request):
    if request.method == "POST":
        # Gestion du changement de mot de passe
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important pour éviter la déconnexion après changement de mot de passe
            messages.success(request, "Votre mot de passe a été mis à jour avec succès.")
            return redirect('account')  # Redirection après mise à jour
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'account.html', {
        'user': request.user,
        'form': form,
    })
