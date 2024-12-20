from django.shortcuts import render
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import subprocess
import pandas as pd
import joblib 
import sqlite3
import sys
import os

from home.top_pizzas import best_sold,get_info_pizza,pizzas_season

from models.scripts.gradient_boosting import get_boosting_recommendations
from models.scripts.random_forest import get_forest_recommendations
from models.scripts.tf_idf import get_tfidf_recommendations




# Chemin vers la base de données
db_path = settings.DATABASES['default']['NAME']

@login_required
def home(request):
    context = {
        'MEDIA_URL': settings.MEDIA_URL,
        'user': request.user,
    }
    return render(request, 'home/home.html', context)

@login_required
def get_home_data(request):
    user = request.user

    # Vérif si les recommandations sont dans cache
    cache_key = f"user_{user.id}_recommendations"
    recommendations = cache.get(cache_key)

    if not recommendations:
        recommendations = execute_script(user.id)
        cache.set(cache_key, recommendations, timeout=60 * 60 * 24)

    best_sold_pizzas = best_sold(db_path)
    recommendations_info = get_info_pizza(db_path, recommendations)
    seasonnal = pizzas_season(db_path)
    print(best_sold_pizzas)
    print(recommendations_info)

    def serialize_pizza(pizza):
        return {
            'name': pizza['name'],
            'ingredients': pizza['ingredients'],
            'unit_price': pizza['unit_price'],
            'image_url': settings.MEDIA_URL + str(pizza['image']),  
        }

    data = {
        'best_sold_pizzas': [serialize_pizza(pizza) for pizza in best_sold_pizzas],
        'recommendations': [serialize_pizza(pizza) for pizza in recommendations_info],
        "pizzas_season": [serialize_pizza(pizza) for pizza in seasonnal]
    }

    return JsonResponse(data)

def execute_script(client_id):
    print("Entrainement des modèles et récupération des recommandations")

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TRAIN_MODELS_SCRIPT = os.path.join(BASE_DIR, "models", "scripts", "train_models.py")

    try:
        subprocess.run([sys.executable, TRAIN_MODELS_SCRIPT], check=True)
        print("Entraînement des modèles terminé")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de train_models : {e}")
        return {}

    try:

        COLLABORATIVE_MODEL_PATH = os.path.join(BASE_DIR, "models", "collaborative_model.joblib")
        collaborative_model = load_model(COLLABORATIVE_MODEL_PATH)
        print("Tous les modèles ont été chargés avec succès.")

        user_history = get_user_history(client_id)

        ingredient_recommendations = recommend_based_on_ingredients(client_id)
        print("Recommandations basées sur les ingrédients générées.")
        collaborative_recommendations = get_collaborative_recommendations(collaborative_model, user_history, client_id)
        print("Recommandations collaboratives générées.")
        boosting_recommendations = get_boosting_recommendations(client_id, db_path)
        print("Recommandations par Gradient Boosting générées.")
        forest_recommendations = get_forest_recommendations(client_id, db_path)  
        print("Recommandations par Random Forest générées.")
        tfidf_recommendations = get_tfidf_recommendations(client_id, db_path)
        print("Recommandations TF-IDF générées.")

        recommendations = {
            "ingredients": ingredient_recommendations,
            "collaborative": [rec[0] for rec in collaborative_recommendations],
            "boosting": boosting_recommendations,
            "forest": forest_recommendations,
            "tfidf": tfidf_recommendations,
        }

        top_5_recommandations = aggregate_recommendations(recommendations)
        print("Top 5 des pizzas recommandées :", top_5_recommandations)

        return top_5_recommandations


    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
        import traceback
        traceback.print_exc()
        return {}



def load_model(path):
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
    conn = sqlite3.connect(db_path)
    query = f"""
    SELECT main_order.pizza_id, main_pizza.name
    FROM main_order
    JOIN main_pizza
    ON main_order.pizza_id = main_pizza.pizza_id
    WHERE client_id = {client_id}
    """
    user_data = pd.read_sql_query(query, conn)
    conn.close()
    return user_data


def recommend_based_on_ingredients(client_id):
    from models.scripts.recommandation_ingredient import recommend_pizzas_based_on_ingredients, load_data

    pizzas_df, orders_df = load_data()
    user_pizzas = get_user_history(client_id)['pizza_id'].tolist()
    recommendations = recommend_pizzas_based_on_ingredients(user_pizzas, pizzas_df, top_k=10)
    print(recommendations)
    return recommendations


def get_collaborative_recommendations(model, user_history, client_id):
    recommendations = []
    for _, row in user_history.iterrows():
        pizza_name = row['name'] 
        score = model.predict(client_id, pizza_name).est 
        recommendations.append((pizza_name, score))
    
    recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)
    return recommendations[:10]


def aggregate_recommendations(recommendations):
    scores = {}
    
    for model_name, recs in recommendations.items():
        if isinstance(recs, list):
            for idx, pizza in enumerate(recs):
                points = 10 - idx  
                if points < 1:  
                    break
                if pizza in scores:
                    scores[pizza] += points
                else:
                    scores[pizza] = points
        else:
            print("Problème format")

    sorted_pizzas = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    top_5_pizzas = [pizza for pizza, score in sorted_pizzas[:5]]
    return top_5_pizzas