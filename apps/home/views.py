from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from main.models import Coupon

# Create your views here.

def home(request):
    user = request.user
    coupons = user.coupons.all()  # Récupérer tous les coupons de l'utilisateur
    context = {
        'loyalty_status': user.current_card,
        'points': user.points,
        'coupons': coupons,
    }
    return render(request, 'home/home.html', context)