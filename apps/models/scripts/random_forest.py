# random_forest.py

import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import warnings
warnings.filterwarnings("ignore")

import os

def get_forest_recommendations(client_id, db_path):
    """
    Entraîne le modèle Random Forest et retourne les recommandations pour un client donné.
    """
    # Connexion à la base de données
    conn = sqlite3.connect(db_path)

    # Chargement des données
    menu = pd.read_sql_query("SELECT pizza_id, name FROM main_pizza", conn)
    orders = pd.read_sql_query("SELECT client_id, pizza_id FROM orders", conn)

    # Fermer la connexion
    conn.close()

    # Fusionner les données pour obtenir les noms des pizzas
    order_data = orders.merge(menu, on='pizza_id')

    # Créer un tableau croisé (pivot table) pour les clients et les pizzas
    order_data_grouped = order_data.groupby(['client_id', 'name'])['name'].count().unstack(fill_value=0)

    # La pizza la plus commandée devient la cible
    order_data_grouped['most_ordered'] = order_data_grouped.idxmax(axis=1)
    target = order_data_grouped['most_ordered']
    features = order_data_grouped.drop(columns=['most_ordered'])

    # Séparer les données pour l'entraînement
    X = features
    y = target

    # Entraîner le modèle Random Forest
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    # Vérifier si le client est présent dans les données
    if client_id in X.index:
        user_features = X.loc[[client_id]]
    else:
        # Si le client n'existe pas dans les données, créer une ligne avec des zéros
        user_features = pd.DataFrame(0, index=[client_id], columns=X.columns)

    # Prédire les probabilités pour toutes les classes (pizzas)
    predictions_proba = model.predict_proba(user_features)[0]
    pizza_names = model.classes_

    # Créer une liste de tuples (pizza_name, probability)
    pizza_probabilities = list(zip(pizza_names, predictions_proba))

    # Trier par probabilité décroissante
    pizza_probabilities.sort(key=lambda x: x[1], reverse=True)

    # Retourner les 10 meilleures recommandations
    top_recommendations = pizza_probabilities[:10]

    # Extraire uniquement les noms de pizzas
    recommendations = [pizza for pizza, prob in top_recommendations]

    return recommendations


# Test du script directement (si besoin)
if __name__ == "__main__":
    # Remplacer par le chemin de votre base de données
    db_path = "path/to/db.sqlite3"
    client_id = 1  # Exemple de client
    recommendations = get_forest_recommendations(client_id, db_path)
    print(f"Recommandations pour le client {client_id} : {recommendations}")
