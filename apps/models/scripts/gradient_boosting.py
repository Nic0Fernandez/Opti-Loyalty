# gradient_boosting.py

import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
import warnings
warnings.filterwarnings("ignore")
import os

def get_boosting_recommendations(client_id, db_path):
    """
    Entraîne le modèle Gradient Boosting et retourne les recommandations pour un client donné.
    """
    # Chemin absolu vers la base de données
    conn = sqlite3.connect(db_path)

    # Chargement des données
    menu = pd.read_sql_query("SELECT * FROM main_pizza", conn)
    orders = pd.read_sql_query("SELECT * FROM orders", conn)

    # Fermer la connexion
    conn.close()

    # Jointure pour obtenir les noms des pizzas
    order_data = orders.merge(menu, on='pizza_id')

    # Remplacer pizza_id par name
    order_data_grouped = order_data.groupby(['client_id', 'name'])['name'].count().unstack(fill_value=0)

    # Création des labels pour recommandation
    # La pizza la plus commandée pour chaque client devient la cible
    order_data_grouped['most_ordered'] = order_data_grouped.idxmax(axis=1)
    target = order_data_grouped['most_ordered']
    features = order_data_grouped.drop(columns=['most_ordered'])

    # Séparation des données pour entraînement et test
    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

    # Entraînement du modèle Gradient Boosting
    model = GradientBoostingClassifier(n_estimators=40, learning_rate=0.2, random_state=42, max_depth=3, subsample=0.8)
    model.fit(X_train, y_train)

    # Préparer les données pour le client donné
    if client_id in features.index:
        user_features = features.loc[[client_id]]
    else:
        # Si le client n'existe pas dans les données d'entraînement, retourner une recommandation par défaut
        user_features = pd.DataFrame(0, index=[client_id], columns=features.columns)

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

    print(recommendations)
    return recommendations

# Permettre d'exécuter le script directement pour tester
if __name__ == "__main__":
    # Chemin absolu vers la base de données
    current_dir = os.path.dirname(os.path.abspath(__file__))  
    db_path = os.path.join(current_dir, '../../../db.sqlite3') 

    client_id = 1  # Exemple de client_id
    recommendations = get_boosting_recommendations(client_id, db_path)
    print(f"Recommandations pour le client {client_id} : {recommendations}")
