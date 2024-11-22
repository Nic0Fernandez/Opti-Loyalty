# PizzAdvisor

Système de compte client avec recommandations personnalisées en fonction des meilleures ventes, de l'historique du client ou encore de la saisonnalité.

## Table des Matières

- [Installation](#installation)
- [Utilisation](#utilisation)

## Installation

1. **Cloner le dépôt :**
    ```bash
    git clone https://github.com/votre-utilisateur/votre-projet.git
    cd votre-projet
    ```

2. **Créer un environnement virtuel :**
    ```bash
    python -m venv env
    ```

3. **Activer l'environnement virtuel :**
    - **Windows :**
      ```bash
      env\Scripts\activate
      ```
    - **macOS/Linux :**
      ```bash
      source env/bin/activate
      ```

4. **Installer les dépendances :**
    ```bash
    pip install -r requirements.txt
    ```

## Utilisation

Une fois les dépendances installées, pour tester le site:
    ```
    cd apps
    ```
    
Puis
    ```
    python .\manage.py runserver
    ```

Tous les scripts (et notebooks équivalents) utilisés pour entraîner les modèles et réaliser les tests ainsi que la génération des données clients sont disponibles dans les dossier "scripts" et "scripts/notebooks" depuis la racine du projet.

Le dossier "media" contient les images utilisées. Le dossier apps contient toute la partie front-end et liaison avec le back-end. Chaque app correspond à une page. L'app "models" contient les scripts d'entrainement des modèles utilisés par le site.

L'app "home" contient la plupart des traitements. Le fichier "top_pizzas.py" contient la plupart des requêtes sql nécessaires aux affichages présents sur la page d'accueil du site. 
