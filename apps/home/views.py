from django.shortcuts import render
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.decorators import login_required
import subprocess
import pandas as pd
import joblib  # Utiliser joblib au lieu de pickle
import sqlite3
import sys
import os

from home.top_pizzas import top_5_pizzas



# Chemin vers la base de données
db_path = settings.DATABASES['default']['NAME']

@login_required
def home(request):
    user = request.user

    # Vérifier si les recommandations sont en cache
    cache_key = f"user_{user.id}_recommendations"
    recommendations = cache.get(cache_key)

    if not recommendations:
        recommendations = execute_script(user.id)
        cache.set(cache_key, recommendations, timeout=60 * 60 * 24)

    context = {
        'pizzas': top_5_pizzas(db_path),
        'MEDIA_URL': settings.MEDIA_URL,
        "recommendations": recommendations,
    }
    return render(request, 'home/home.html', context)

def execute_script(client_id):
    print("Entrainement des modèles et récupération des recommandations")

    # Exécuter le script de formation des modèles
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TRAIN_MODELS_SCRIPT = os.path.join(BASE_DIR, "models", "scripts", "train_models.py")

    print(f"Python interpreter used: {sys.executable}")
    print(f"Executing script at: {TRAIN_MODELS_SCRIPT}")

    try:
        subprocess.run([sys.executable, TRAIN_MODELS_SCRIPT], check=True)
        print("Entraînement des modèles terminé")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de train_models : {e}")
        return {}

    try:
        # Charger les modèles
        COLLABORATIVE_MODEL_PATH = os.path.join(BASE_DIR, "models", "collaborative_model.joblib")
        GRADIENT_BOOSTING_MODEL_PATH = os.path.join(BASE_DIR, "models", "gradient_boosting_model.joblib")
        RANDOM_FOREST_MODEL_PATH = os.path.join(BASE_DIR, "models", "random_forest_model.joblib")
        TFIDF_SIMILARITY_PATH = os.path.join(BASE_DIR, "models", "cosine_similarity.joblib")
        TFIDF_VECTORIZER_PATH = os.path.join(BASE_DIR, "models", "tfidf_vectorizer.joblib")

        collaborative_model = load_model(COLLABORATIVE_MODEL_PATH)
        gradient_boosting_model = load_model(GRADIENT_BOOSTING_MODEL_PATH)
        random_forest_model = load_model(RANDOM_FOREST_MODEL_PATH)
        cosine_sim = load_model(TFIDF_SIMILARITY_PATH)

        print("Tous les modèles ont été chargés avec succès.")

        # Récupérer l'historique de l'utilisateur
        user_history = get_user_history(client_id)
        print(f"Historique de l'utilisateur récupéré : {user_history}")

        # Générer les recommandations
        ingredient_recommendations = recommend_based_on_ingredients(client_id)
        print("Recommandations basées sur les ingrédients générées.")

        collaborative_recommendations = get_collaborative_recommendations(collaborative_model, user_history)
        print("Recommandations collaboratives générées.")

        boosting_recommendations = get_boosting_recommendations(gradient_boosting_model, user_history)
        print("Recommandations par Gradient Boosting générées.")

        forest_recommendations = get_forest_recommendations(random_forest_model, user_history)
        print("Recommandations par Random Forest générées.")

        tfidf_recommendations = get_tfidf_recommendations(client_id, user_history, cosine_sim)
        print("Recommandations TF-IDF générées.")

        recommendations = {
            "ingredients": ingredient_recommendations,
            "collaborative": collaborative_recommendations,
            "boosting": boosting_recommendations,
            "forest": forest_recommendations,
            "tfidf": tfidf_recommendations,
        }

        print("Recommandations générées :", recommendations)
        return recommendations

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
        import traceback
        traceback.print_exc()
        return {}

def load_model(path):
    """Charger un modèle depuis un fichier joblib."""
    try:
        model = joblib.load(path)
        print(f"Modèle chargé depuis {path}")
        return model
    except FileNotFoundError:
        print(f"Erreur : Le fichier modèle {path} n'existe pas.")
        return None
    except Exception as e:
        print(f"Erreur lors du chargement du modèle {path} : {e}")
        return None

def get_user_history(client_id):
    """Récupérer l'historique des commandes d'un client."""
    conn = sqlite3.connect(db_path)
    query = f"""
    SELECT pizza_id
    FROM orders
    WHERE client_id = {client_id};
    """
    user_data = pd.read_sql_query(query, conn)
    conn.close()
    return user_data


def recommend_based_on_ingredients(client_id):
    """Recommandations basées sur les ingrédients."""
    from models.scripts.recommandation_ingredient import recommend_pizzas_based_on_ingredients, load_data

    pizzas_df, orders_df = load_data()
    user_pizzas = get_user_history(client_id)['pizza_id'].tolist()
    recommendations = recommend_pizzas_based_on_ingredients(user_pizzas, pizzas_df, top_k=10)
    return recommendations


def get_collaborative_recommendations(model, user_history):
    """Recommandations via le modèle collaboratif."""
    recommendations = []
    for pizza in user_history['pizza_id']:
        score = model.predict(user_history['client_id'], pizza).est
        recommendations.append((pizza, score))
    return sorted(recommendations, key=lambda x: x[1], reverse=True)[:10]


def get_boosting_recommendations(model, user_history):
    """Recommandations via Gradient Boosting."""
    features = prepare_features_for_model(user_history)
    predictions = model.predict_proba(features)
    return extract_top_predictions(predictions)


def get_forest_recommendations(model, user_history):
    """Recommandations via Random Forest."""
    features = prepare_features_for_model(user_history)
    predictions = model.predict_proba(features)
    return extract_top_predictions(predictions)


def get_tfidf_recommendations(client_id, user_history, cosine_sim, num_recommendations=10):
    conn = sqlite3.connect(db_path)
    pizzas_df = pd.read_sql_query("SELECT pizza_id, name, ingredients FROM menu", conn)
    conn.close()

    ordered_pizza_ids = user_history['pizza_id'].unique()
    pizza_indices = pizzas_df[pizzas_df['pizza_id'].isin(ordered_pizza_ids)].index

    similar_scores = cosine_sim[pizza_indices].mean(axis=0)

    pizza_scores = list(enumerate(similar_scores))
    pizza_scores = [
        (i, score) for i, score in pizza_scores if pizzas_df.iloc[i]['pizza_id'] not in ordered_pizza_ids
    ]
    pizza_scores = sorted(pizza_scores, key=lambda x: x[1], reverse=True)

    recommended_pizzas = []
    for i, score in pizza_scores[:num_recommendations]:
        pizza = pizzas_df.iloc[i]
        recommended_pizzas.append((pizza['name'], pizza['pizza_id'], score))

    return recommended_pizzas


def prepare_features_for_model(user_history):
    return user_history


def extract_top_predictions(predictions):
    scores = sorted(enumerate(predictions), key=lambda x: x[1], reverse=True)
    return scores[:10]
