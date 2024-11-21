import django
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from main.models import Coupon

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os
import threading

# Configurer Django pour accéder aux paramètres
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "optiloyalty.settings")  
django.setup()

# Chemin vers la base de données
db_path = settings.DATABASES['default']['NAME']

# Create your views here.

def home(request):
    user = request.user
    coupons = user.coupons.all()  # Récupérer tous les coupons de l'utilisateur
    context = {
        'loyalty_status': user.current_card,
        'points': user.points,
        'coupons': coupons,
    }

    # Lancer l'observateur dans un thread séparé (en arrière-plan)
    threading.Thread(target=start_observer, daemon=True).start()

    return render(request, 'home/home.html', context)
class DatabaseChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print(f"Événement détecté : {event.src_path}")  # Vérifier quel fichier est modifié
        if event.src_path == os.path.abspath(db_path):
            print(f"La base de données {db_path} a été modifiée!")
            execute_script()


def execute_script():
    print("Exécution du script Python en réponse à une modification.")
    # Ajoutez ici le code à exécuter

# Fonction pour démarrer l'observateur dans un thread
def start_observer():
    event_handler = DatabaseChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(db_path), recursive=False)
    observer.start()
    print(f"Surveillance de {db_path} pour les modifications...")
    
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


    
