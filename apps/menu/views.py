from django.shortcuts import render
from django.conf import settings
from menu.get_menu import get_menu

# Create your views here.


db_path = settings.DATABASES['default']['NAME']

def menu(request):
    context = {
        'pizzas': get_menu(db_path),
        'MEDIA_URL': settings.MEDIA_URL,
    }
    return render(request, 'menu/menu.html', context)